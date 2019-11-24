"""Server API endpoints"""
from datetime import datetime
import subprocess
import os
from flask import jsonify, request

from app import app
from app.models import User, Contact
from app import db
from config import Config


# ---------- Git Webhook (Re-)Deployment ----------
@app.route('/update', methods=['POST'])
def redeploy():
    """Hook to redeploy prod server via github webhook
    Performs a git pull and a restart of bot and server"""
    FNULL = open(os.devnull, 'w')
    try:
        # Make sure server is up to date
        subprocess.Popen(['git', 'pull'], stdout=FNULL)
        # Make sure there are no local changes on server
        subprocess.Popen(['git', 'reset', '--hard'], stdout=FNULL)
        # Log the pull
        with open('logs/last_pull', 'w+') as pull_log:
            pull_log.write(str(datetime.now()))
        # Restart the server
        subprocess.Popen(['./restart.sh'], stdout=FNULL)
    except Exception as exception:
        return jsonify(str(exception)), 400
    return jsonify("Successfull Redeploy"), 200

# ---------- User Creation and Info ----------
@app.route('/user/all')
def all_users():
    """Lists all created users"""
    return jsonify({"userIds": [user_id[0] for user_id in User.query.with_entities(User.user_id).all()]})

@app.route('/user/create')
def create_user():
    """Creates a new user and replies his id and register url"""
    user = User()
    db.session.add(user)
    db.session.commit()
    return jsonify({"userId": user.user_id,
                    "registerURL": "telegram.me/{botname}?start={token}".format(
                        botname=Config.BOT_NAME, token=user.telegram_start_token)})

@app.route('/user/<user_id>')
def get_user(user_id):
    """Returns a user dict"""
    # TODO: jsonify does not work on this object
    try:
        user = User.query.get(int(user_id))
        if user:
            return jsonify(user.as_dict()), 200
        else:
            return jsonify("No such user"), 400
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userId"), 400

@app.route('/user/register')
def register_users_telegram_handle():
    """Registeres provided telegramHandle for a user.
    Last handshake action
    Requires a valid auth token"""
    telegram_handle = request.args.get("telegramHandle", None)
    telegram_start_token = request.args.get("telegramStartToken", None)

    if not telegram_handle:
        return jsonify("Please provide a telegramHandle"), 400
    if not telegram_start_token:
        return jsonify("Please provivde a telegramStartToken"), 400

    try:
        user = User.query.filter_by(telegram_start_token=telegram_start_token).first()
    except ValueError:
        return jsonify("Invalid telegramStartToken"), 400

    if not user:
        return jsonify("No user with such token"), 400

    if user.telegram_handle:
        return jsonify("Telegram already registerd for this user"), 400

    user.telegram_handle = telegram_handle
    db.session.add(user)
    db.session.commit()
    return jsonify("Successfull register"), 200

# ---------- User Data Dump ----------
@app.route('/user/<user_id>/data', methods=['POST'])
def recieve_user_data(user_id):
    """Common data dump point. Applies various handlers to put provided
    data into the db"""

    def contact_handler(contact):
        """Handler to put a single contact into the db"""
        # TODO: Create a palce for handlers and extract this one
        if "firstname" not in contact or "lastname" not in contact:
            # Corrupt data
            return False
        else:
            contact = Contact(user_id=int(user_id),
                              firstname=contact.get("firstname"),
                              lastname=contact.get("lastname"))
            db.session.add(contact)
            db.session.commit()
        return True

    # TODO: Refactor data control flow
    datatype_handlers = {"contacts": contact_handler}
    json_data = request.get_json()

    if not json_data:
        return jsonify("Please provide data!"), 400

    data_origin = json_data.get("origin", None)
    data = json_data.get("data", {})

    if not data_origin:
        return jsonify("Please specify the data <origin>"), 400

    if data_origin not in ["app", "bot"]:
        return jsonify("I only take data <origin>ating from app or bot"), 400

    try:
        user = User.query.get(int(user_id))
    except ValueError:
        # Invalid ID Type
        return jsonify("Invalid userId"), 400

    if not user:
        return jsonify("No such user"), 400

    for datatype, value_list in data.items():
        # TODO: Handle data
        handled_types = {}
        if datatype in datatype_handlers.keys():
            handled_types[datatype] = 0

            for value in value_list:
                if datatype_handlers[datatype](value):
                    handled_types[datatype] += 1

    return jsonify("Added {} to db".format(handled_types)), 200

@app.route('/user/<user_id>/data/<datatype>')
def get_data_by_type(user_id, datatype):
    """Tries to fetch a specific datattype from the db"""
    datatype_to_db_col = {"contacts": Contact}

    if datatype_to_db_col.get(datatype, None):
        contacts = datatype_to_db_col[datatype].query.filter_by(user_id=int(user_id)).all()
        return jsonify([contact.as_dict() for contact in contacts]), 200
    return jsonify("not implemented yet"), 400

# ---------- Chat Bot API ----------
@app.route('/user/answersForUserAndMessage')
def get_answers():
    """Returns a json array of answers.
    The answers are based on the users gamestate
    ans personalized based on his data"""
    # TODO
    # Get user and message params
    # Get proper answer (by a personalizer instance?)
    # Reply answer array

    # TEMP
    import random
    answers = [["You sound strange", "Are you a lizardman or -women?"],
               ["You are talking to me", "Which means you are talking to a machine",
                "Dont you find this curious?"],
               ["Dont you hate yourself sometimes?"]]
    return jsonify(random.choice(answers))

@app.route('/user/replyOptionsForUser')
def get_reply_options():
    """Returns a json array of reply options personalized for a user"""
    # TODO
    # Get user param
    # Get proper reply options (by a personalizer instance?)
    # Reply reply option array (already formatted as button layout?)

    import random
    replys = ["Yes", "No", "Maybe", "Later", "Soon"]
    amount = random.randint(2, len(replys))
    random.shuffle(replys)
    return jsonify([replys[n] for n in range(amount)])

from app import db
from app.story import placeholder_assigner

attr_dict = {placeholder: db.Column(db.String(64), nullable=True, unique=False) for placeholder in placeholder_assigner.keys()}
attr_dict['__tablename__'] = 'personalization'
attr_dict['user_id'] = db.Column(db.Integer, primary_key=True)
Personalization = type("Personalization", (db.Model,), attr_dict)
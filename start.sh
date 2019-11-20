source bin/activate
flask run --host 0.0.0.0 > server_log 2>&1 &
python3 bot_draft.py > bot_log 2>&1 &

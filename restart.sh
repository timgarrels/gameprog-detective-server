#! /usr/bin/env bash

source bin/activate
if [ ! -d logs ]; then
    echo "Creating logs directory"
    mkdir -p logs
fi

# Kill server
if [ -f logs/server_pid ]; then
    if ps -p `cat logs/server_pid` > /dev/null; then
        echo "Killing running server..."
        kill `cat logs/server_pid`
    else
        echo "Server not running"
    fi
fi
# Kill bot
if [ -f logs/bot_pid ]; then
    if ps -p `cat logs/bot_pid` > /dev/null; then
        echo "Killing running bot..."
        kill `cat logs/bot_pid`
    else
        echo "Bot not running"
    fi
fi
# Restart Server
echo "Starting server..."
flask run --host 0.0.0.0 > logs/server_log 2>&1 &
echo $! > logs/server_pid
# Restart Bot
echo "Starting bot..."
python3 bot_draft.py > logs/bot_log 2>&1 &
echo $! > logs/bot_pid
sleep 1
echo "All up and running"
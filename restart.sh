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
        kill -9 `cat logs/server_pid`
        # Wait for process to really die
        while ps -p `cat logs/server_pid` > /dev/null; do
            :
        done
    else
        echo "Server not running"
    fi
fi
# Kill bot
if [ -f logs/bot_pid ]; then
    if ps -p `cat logs/bot_pid` > /dev/null; then
        echo "Killing running bot..."
        kill -9 `cat logs/bot_pid`
        # Wait for process to really die
        while ps -p `cat logs/bot_pid` > /dev/null; do
            :
        done
    else
        echo "Bot not running"
    fi
fi

# Restart Server
echo "Starting server..."
echo "----------" >> logs/server_log
flask run --host 0.0.0.0 >> logs/server_log 2>&1 &
echo $! > logs/server_pid
# Restart Bot
echo "Starting bot..."
echo "----------" >> logs/bot_log
python3 bot/bot.py >> logs/bot_log 2>&1 &
echo $! > logs/bot_pid
sleep 1
echo "All up and running"
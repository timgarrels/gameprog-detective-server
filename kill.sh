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
    else
        echo "Server not running"
    fi
fi
# Kill bot
if [ -f logs/bot_pid ]; then
    if ps -p `cat logs/bot_pid` > /dev/null; then
        echo "Killing running bot..."
        kill -9 `cat logs/bot_pid`
    else
        echo "Bot not running"
    fi
fi


#! /usr/bin/env bash

command=$1

# switch to parent folder of this script
cd $(dirname $0)

if [ "$command" == "install" ]; then
    if [ ! -d logs ]; then
        echo "Creating logs directory"
        mkdir -p logs
    fi
    if [ ! -d .venv ]; then
        echo "Creating virual environment"
        python3.8 -m venv .venv
    fi
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ./manage.sh reset_db
    exit
fi

# try to load venv
if [ -d .venv ]; then
    source .venv/bin/activate
else
    echo "please first install the server"
    exit
fi

if [ "$command" == "start" ]; then
    if ps -p `cat logs/server_pid` > /dev/null; then
        echo "server already running"
        exit
    fi
    # load environment variables form file if present
    [ -f env_vars ] && source env_vars
    echo "Starting server..."
    echo "----------" >> logs/server_log
    flask run --host 0.0.0.0 --port 8080 >> logs/server_log 2>&1 &
    echo $! > logs/server_pid
    echo "For logs use cat logs/server_log"
elif [ "$command" == "kill" ]; then
    if ps -p `cat logs/server_pid` > /dev/null; then
        echo "Killing running server..."
        kill -9 `cat logs/server_pid`
    else
        echo "Server not running"
    fi

elif [ "$command" == "restart" ]; then
    ./manage.sh kill
    ./manage.sh start
elif [ "$command" == "reset_db" ]; then
    if [ -f app/app.db ]; then
        echo "Removing old db"
        rm app/app.db
    fi
    if [ -d migrations/ ]; then
        echo "Removing old migrations"
        rm -rf migrations/
    fi
    echo "Create new db"
    [ -f env_vars ] && source env_vars
    flask db init
    flask db migrate
    flask db upgrade
elif [ "$command" == "log" ]; then
    cat logs/server_log
elif [ "$command" == "visualize_story" ]; then
    [ -f env_vars ] && source env_vars
    python visualize_story_graph.py
elif [ "$command" == "help" ] || [ "$command" == "" ]; then
    echo "Usage: ./manage.sh [command]"
    echo ""
    echo "Available commands:"
    echo "./manage.sh install - Install and Setup Server"
    echo "./manage.sh start - Start new Server instance"
    echo "./manage.sh kill - Kill running Server instance"
    echo "./manage.sh restart - Kill running Server instance and start a new one"
    echo "./manage.sh reset_db - Remove old database and initialize a new one"
    echo "./manage.sh log - Show Server log"
    echo "./manage.sh help - Display this text"
else
    echo "Unkown command, use ./manage.sh help to view available commands"
fi

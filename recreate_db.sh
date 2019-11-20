#! /usr/bin/env bash

source bin/activate
# Remove old db
rm app.db
rm -rf migrations
# Create new db
flask db init
flask db migrate
flask db upgrade
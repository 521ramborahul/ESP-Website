#!/bin/sh

# Pipe the output of "manage.py migrate --list" to this script.
# It will say whether there are unapplied django-south migrations.

MIGRATIONS="`grep -v '(\*)' | grep -1 '( )'`"

if [ -z "$MIGRATIONS" ]; then
    echo "Database migrations are up to date."
else
    printf "\033[1;33mThe following database migrations have not been applied:\033[m\n"
    echo "$MIGRATIONS"
fi

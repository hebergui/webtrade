#!/bin/bash
FILE="pid.django"

./stop-it.sh

nohup python manage.py runserver 0.0.0.0:8000 --insecure &

echo $! > $FILE

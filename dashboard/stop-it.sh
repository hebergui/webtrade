#!/bin/bash
FILE="pid.django"

if [[ -f "$FILE" ]]; then
	pid=`cat $FILE`
	echo "Killing pid $pid..."
	kill $pid 
	rm -f $FILE
else
	echo "No pid"
fi

echo "OK!"

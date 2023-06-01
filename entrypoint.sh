#!/bin/bash

python /app/lock.py

ret=$?
if [ $ret -ne 0 ]; then
    #Handle failure
    echo "success=0" >> "$GITHUB_OUTPUT"
    echo "start-date=" >> "$GITHUB_OUTPUT"
    echo "end-date=" >> "$GITHUB_OUTPUT"
    exit 1
fi

echo "success=1" >> "$GITHUB_OUTPUT"
echo "start-date=${OUTPUT_START_DATE}" >> "$GITHUB_OUTPUT"
echo "end-date=${OUTPUT_END_DATE}" >> "$GITHUB_OUTPUT"

exit 0

#!/bin/bash

# Run python script, capturing all stdout as we go
py_err=$( python /app/lock.py 2>&1 1>stdout.txt )

output=()
while read line ; do
    output+=("${line}")
done < stdout.txt

# Assign last two lines of output to vars
START_DATE="${output[-2]}"
END_DATE="${output[-1]}"
echo "start-date=${START_DATE}" >> "$GITHUB_OUTPUT"
echo "end-date=${END_DATE}" >> "$GITHUB_OUTPUT"

# echo out all but last 2 lines of output back to stdout
echo ""
echo "Script output:"
i=0
while [ $i -le $(( ${#output[@]} - 3 )) ]; do
    echo "> ${output[$i]}"
    ((i++))
done

# Handle return state
if [ -z "$py_err" ]; then
    echo "success=1" >> "$GITHUB_OUTPUT"
    echo "Script completed successfully"
    exit 0
else
    echo "success=0" >> "$GITHUB_OUTPUT"
    echo "error=$py_err" >> "$GITHUB_OUTPUT"
    echo "Script completed with error: $py_err"
    exit 1
fi

#!/bin/bash

# Run python script, capturing all stdout as we go
output=()
while read line ; do
  output+=("${line}")
done < <(python /app/lock.py)
ret=$?

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
if [ $ret -ne 0 ]; then
    echo "success=0" >> "$GITHUB_OUTPUT"
    exit 1
fi

echo "success=1" >> "$GITHUB_OUTPUT"
echo "Script completed successfully"
exit 0

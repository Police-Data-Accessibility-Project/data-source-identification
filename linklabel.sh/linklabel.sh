#!/bin/bash

# ensure 
cd "$(dirname "$0")"

# read a URL from stdin
while read url; do
    # output a properly formatted JSON object for each URL we get
    jo url="$url" labels="$(
        # iterate through all regexes
        find regexes -type f -print0 | while read -d $'\0' regexfile ; do
            # extract label name from filename
            labelname="$( basename "$regexfile" )"
            # extract content from file
            regex="$( cat "$regexfile" )"

            # try to match regex and add label if it matches
            echo "$url" | egrep -i "$regex" > /dev/null

            # if the regex matches the URL...
            if [[ $? -eq 0 ]]; then
                # print label
                echo "$labelname"
            fi
        done | jo -a
    )"
done

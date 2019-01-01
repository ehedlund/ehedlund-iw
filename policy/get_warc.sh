#!/bin/bash

i=1
while IFS=, read url
do
    echo $url
    wget "$url" --warc-file="warc/site_$i" -O /dev/null
    let i=i+1
done < final_sites.csv

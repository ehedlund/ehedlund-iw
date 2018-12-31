#!/bin/bash

# extract server names from pcap file
tshark -r $1 -T fields -e ssl.handshake.extensions_server_name -Y ssl.handshake.extensions_server_name | sort > input/server_names.txt

# generate lists of https sites
python compare_sites.py

# print site counts
wc -l output/https_sites.txt
wc -l output/non_https_sites.txt
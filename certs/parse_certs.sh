#!/bin/bash

# extract certs from pcap file
tshark -nr $1 -V "ssl.handshake.certificate" | grep "^\s*rdnSequence\|^\s*Certificates (\|RDNSequence item: 1 item" | sed "s/^[ \t]*//" > extracted_certs.txt

# parse certs into chains
python process_certs.py > output/certs_output.txt

# remove intermediate output file
rm extracted_certs.txt
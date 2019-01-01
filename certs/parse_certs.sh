#!/bin/bash

# extract certs from pcap file
tshark -nr $1 -V "ssl.handshake.certificate" | grep "^\s*issuer: rdnSequence\|^\s*subject: rdnSequence\|^\s*Certificates (\|RDNSequence item: 1 item" | sed "s/^[ \t]*//" > extracted_certs.txt

# parse certs into chains
python process_certs.py > output/certs_output.txt

# remove intermediate output file
rm extracted_certs.txt

# split certs into first/third party for analysis
python split_certs.py
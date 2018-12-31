use tcpdump to capture certificates while running OpenWPM:
sudo tcpdump -ni ens3 "tcp port 443 and (tcp[((tcp[12] & 0xf0) >> 2)] = 0x16)" -w $PCAP

parse_certs.sh takes as a command line argument the path to a PCAP input file to parse, and outputs a text file containing information about the certificate chains contained in the file (output/certs_output.txt)

check_https.sh takes as a command line argument the path to a PCAP input file to parse, and outputs text files containing lists of https enabled sites (output/https_sites.txt, output/non_https_sites.txt)
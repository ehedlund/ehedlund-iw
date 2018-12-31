import csv
from urlparse import urlparse

server_names = set()

with open('input/server_names.txt') as f:
	for line in f:
		url = line.replace("www.","").rstrip('\n')
		server_names.add(url)

https_sites = list()
non_https_sites = list()

with open('input/final_sites.csv') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
    	site = row[0]
    	if (urlparse(site).hostname in server_names):
    		https_sites.append(site)
    	else:
    		non_https_sites.append(site)

with open('output/https_sites.txt', 'w') as f:
    for item in https_sites:
        f.write("%s\n" % item)

with open('output/non_https_sites.txt', 'w') as f:
    for item in non_https_sites:
        f.write("%s\n" % item)
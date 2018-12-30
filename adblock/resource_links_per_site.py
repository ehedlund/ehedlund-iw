from adblockparser import AdblockRules
import csv
import sys

csv.field_size_limit(sys.maxsize)

# create list of sites with ads
with open('input/sites_with_ads.txt') as f:
	sites_with_ads = f.read().splitlines() 

# create AdblockRules from EasyList
with open('input/easylist.txt') as f:
    raw_rules = f.readlines()

rules = AdblockRules(raw_rules)

# check urls against AdblockRules
previous_top_level = ""

with open('input/http_requests_output.csv') as f:
	csv_reader = csv.reader(f)

	for row in csv_reader:
		request_url = row[0]
		top_level_url = row[1]

		# check if we should examine resources
		if (top_level_url in sites_with_ads):
			# check if we need to print the source
			if (top_level_url != previous_top_level):
				print("top level: " + top_level_url)
				previous_top_level = top_level_url

			if (rules.should_block(request_url)):
				print(request_url)
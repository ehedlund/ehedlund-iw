from adblockparser import AdblockRules
import csv
import sys

csv.field_size_limit(sys.maxsize)

# create AdblockRules from EasyList
with open('input/easylist.txt') as f:
    raw_rules = f.readlines()

rules = AdblockRules(raw_rules)

# check urls against AdblockRules
ads = dict()

with open('input/http_requests_output.csv') as f:
	csv_reader = csv.reader(f)

	for row in csv_reader:
		request_url = row[0]
		top_level_url = row[1]

		if (rules.should_block(request_url)):
			count = 0

			if top_level_url in ads:
				count = ads[top_level_url]

			ads[top_level_url] = count + 1

print(ads)

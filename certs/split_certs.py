first_party_subjects = list()

with open('input/first_party_subjects.txt') as f:
	for line in f:
		first_party_subjects.append(line.strip())

first_party_certs = list()
third_party_certs = list()

with open('output/certs_output.txt') as f:
	for line in f:
		subject = line.split('|')[0].strip()

		if (subject in first_party_subjects):
			first_party_certs.append(line.strip())
		else:
			third_party_certs.append(line.strip())

with open('output/first_party_certs.txt', 'w') as f:
	for item in first_party_certs:
	        f.write("%s\n" % item)

with open('output/third_party_certs.txt', 'w') as f:
	for item in third_party_certs:
	        f.write("%s\n" % item)
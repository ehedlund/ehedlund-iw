# print all issuer/subject pairs
def print_full_chains(cert_info):
	for i in xrange(0, len(cert_info) - 1, 2):
		print("Issuer: " + cert_info[i])
		print("Subject: " + cert_info[i + 1])
	print

# print all issuers, ending with ultimate subject
def print_chain_info(cert_info):
	# print issuers from top down
	for i in xrange(len(cert_info) - 2, -1, -2):
		print cert_info[i]

	# print ultimate subject
	print cert_info[1]

	print


with open('extracted_certs.txt') as f:
	org_info = list()
	cert_info = list()

	first_cert = True
	first_block = True

	for line in f:
		firstWord = line.split()[0]

		# 'Certificates' denotes the beginning of a chain
		if (firstWord == "Certificates"):
			# don't print empty line
			if (first_cert):
				first_cert = False

			else: 
				# # check for ending self cert
				# num_orgs = len(cert_info)

				# # sometimes the chain ends with just an issuer, so make sure we're examining an issuer/subject pair 
				# if (num_orgs % 2 == 0):
				# 	subject = cert_info[num_orgs - 1]
				# 	issuer = cert_info[num_orgs - 2]

				# 	# remove self cert
				# 	if (subject == issuer):
				# 		cert_info = cert_info[:len(cert_info) - 2]

				# print chain and reset cert_info (choose desired print method)
				print_full_chains(cert_info)
				#print_chain_info(cert_info)

				cert_info = list()

		# 'rdnSequence' denotes the beginning of issuer/subject information block within chain
		elif (firstWord == "rdnSequence:"):
			# don't print empty line
			if (first_block):
				first_block = False

			else:
				# add org to cert chain and reset org
				org_info_string = ', '.join(org_info)
				cert_info.append(org_info_string)
				org_info = list()

		# 'RDNSequence' denotes the beginning of issuer/subject information field
		elif (firstWord == "RDNSequence"):
			# extract value from field and save in info
			org_info.append(line[line.index('=') + 1:][:-2])

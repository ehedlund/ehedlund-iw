# print all issuer/subject pairs
def print_full_chains(cert_info):
	for i in xrange(0, len(cert_info)):
		if (i % 2 == 0):
			print("Issuer: " + cert_info[i])
		else:
			print("Subject: " + cert_info[i])
	print

# print ultimate subject, then all from bottom up
def print_chain_info(cert_info):
	# print ultimate subject
	print(cert_info[1])

	# print issuers from bottom up - issuers are at even indices
	prev_issuer = ""
	for i in xrange(0, len(cert_info)):
		if (i % 2 == 0):
			issuer = cert_info[i]
			
			# self-signed certificate, stop printing
			if (issuer == prev_issuer):
				break
			else:
				print("Issuer: " + issuer)
				prev_issuer = issuer

	print

# print chain on one line for later processing
def print_chain_oneline(cert_info):
	chain = list()

	# append ultimate subject
	chain.append(cert_info[1])

	# append issuers from bottom up - issuers are at even indices
	prev_issuer = ""
	for i in xrange(0, len(cert_info)):
		if (i % 2 == 0):
			issuer = cert_info[i]
			
			# self-signed certificate, stop appending
			if (issuer == prev_issuer):
				break
			else:
				chain.append(issuer)
				prev_issuer = issuer

	print(' | '.join(chain))

# print all cert info contents
def test_print(cert_info):
	for i in xrange(0, len(cert_info)):
		print cert_info[i]
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
				# add last org since there's no following info block to trigger its addition
				cert_info.append(', '.join(org_info))
				org_info = list()
				
				# print chain and reset cert_info (choose desired print method)

				#print_full_chains(cert_info)
				#print_chain_info(cert_info)
				#test_print(cert_info)
				print_chain_oneline(cert_info)

				cert_info = list()

			# starting new cert
			first_block = True

		# 'rdnSequence' denotes the beginning of issuer/subject information block within chain
		elif (firstWord == "rdnSequence:"):
			# don't print empty line
			if (first_block):
				first_block = False
			else:
				# add org to cert chain and reset org
				cert_info.append(', '.join(org_info))
				org_info = list()

		# 'RDNSequence' denotes the beginning of issuer/subject information field
		elif (firstWord == "RDNSequence"):
			# extract value from field and save in info
			org_info.append(line[line.index('=') + 1:][:-2])

	# add last certificate since there's no following certificate to trigger its addition
	cert_info.append(', '.join(org_info))

	#print_full_chains(cert_info)
	#print_chain_info(cert_info)
	#test_print(cert_info)
	print_chain_oneline(cert_info)
#!/usr/bin/python


org_to_abbrev = {'Drosophila melanogaster': "fly",
		'Saccharomyces cerevisiae': "yeast",
		'Rattus norvegicus': "rat",
		#'Mus musculus': "mouse",
		'Homo sapiens': "human",
}


def get_abbrev(org):
	return org_to_abbrev[org]
	
def get_name(abbrev):
	for org, name in org_to_abbrev.items():
		print 'org, name=', org, ',', name 
		if name == abbrev:
			return org
	return None	

def get_names():
	return org_to_abbrev.keys()

def get_abbrevs():
	return org_to_abbrev.values()

#!/usr/bin/python

from intermine.webservice import Service
from intermine.webservice import ServiceError
from collections import defaultdict
import org_util

class PathwayDemo(object):
	service_urls = {'Drosophila melanogaster': "http://www.flymine.org/query/service",
			'Saccharomyces cerevisiae': "http://yeastmine.yeastgenome.org/yeastmine/service",
			'Rattus norvegicus': "http://ratmine.mcw.edu/ratmine/service",
			'Mus musculus': "http://metabolicmine.org/test/service",
			'Homo sapiens': "http://metabolicmine.org/test/service",
	}

	def __init__(self):
		self.services = {}
		for (name, service_url) in self.service_urls.items():
			try:
				self.services[name] = Service(service_url)
				print "Connected to %s" % service_url
			except ServiceError:
				print "Failed to initialise: %s" % service_url
		 

	# returns a list of lists
	def find_gene(self, symbol, org_name):
		service = self.services[org_name]

		query = service.new_query()	
		query.add_view("Gene.symbol", "Gene.primaryIdentifier", "Gene.name", "Gene.organism.name")
		query.add_constraint("Gene", "LOOKUP", symbol)
		query.add_constraint("Gene.organism.name", "=", org_name)

		genes = []
		for row in query.results('tsv'):
			cols = row.split('\t')
			genes.append(cols)
		return genes
				

	def get_homologs_for_gene(self, symbol, org_name):
		# always use FlyMine for querying homologs
		service = self.services["Drosophila melanogaster"]
    	
		query = service.new_query()
		query.add_view(
			"Gene.symbol", "Gene.primaryIdentifier", "Gene.homologues.homologue.symbol",
			"Gene.homologues.homologue.primaryIdentifier",
			"Gene.homologues.homologue.organism.name",
			"Gene.homologues.dataSets.name"
			)
		query.add_constraint("Gene.homologues.homologue.organism.name", "ONE OF", org_util.get_names())
		query.add_constraint("Gene.organism.name", "=", org_name)
		query.add_constraint("Gene.symbol", "=", symbol)

		homologs = defaultdict(lambda: defaultdict(list))
		for row in query.results("tsv"):
			cols = row.split('\t')
			homolog_org = cols[4]
			homolog_symbol = cols[2]
			if homolog_symbol != '""':
				if len(cols) == 6:
					dataset = self.strip_suffix(cols[5])
					homologs[homolog_org][homolog_symbol].append(dataset)
				else:
					homologs[homolog_org][homolog_symbol].append(None)

		return homologs
 
	def get_pathways(self, symbol, org_name):
		service = self.services[org_name]
		query = service.new_query()
		query.add_view('Gene.symbol', 'Gene.pathways.name')
	
		# YeastMine doesn't have pathway.dataSets, check model first
		datasets_path = 'Gene.pathways.dataSets.name'
		if self.is_path_in_model(org_name, datasets_path):
			query.add_view(datasets_path)
			query.add_join('Gene.pathways.dataSets', 'OUTER')

		query.add_sort_order('Gene.pathways.name', 'asc')
		query.add_constraint('Gene.symbol', '=', symbol, 'A')
		query.add_constraint("Gene.organism.name", "=", org_name, "B")
	
		pathways = []
		for row in query.results("tsv"):
			cols = row.split('\t')
			pathway = cols[1]
			if len(cols) == 3:
				# If we know the data source add it in brackets
				pathway += ' (%s)' % cols[2].split(' ')[0]
			pathways.append([pathway, org_name, symbol])

		return pathways

	def is_path_in_model(self, org, path):
		service = self.services[org]	
		try:
			service.model.validate_path(path)
		except:
			return False
		return True

	def strip_suffix(self, dataset):
		if dataset.endswith('data set'):
			return dataset[0:dataset.find('data set')]

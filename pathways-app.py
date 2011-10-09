from flask import Flask, request, redirect, session, url_for, render_template, flash
from pathways import PathwayDemo
from collections import defaultdict
import org_util
import os

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = os.urandom(24)

pd = PathwayDemo()

@app.route('/')
def index():
	return redirect(url_for('search'))

@app.route('/search', methods=['GET', 'POST'])
def search():
	if request.method == 'POST':
		symbol = request.form['symbol']
		org = request.form['organism']
		if symbol:
			genes = pd.find_gene(symbol, org_util.get_name(org))
			if len(genes) == 1:
				symbol = genes[0][0]
				return redirect(url_for('view', symbol=symbol, organism=org))
		flash('Could not find gene: ' + symbol + ' in organism ' + org)
		return redirect(url_for('search'))
	else:
		orgs = org_util.get_abbrevs()
		return render_template('search.html', organisms=orgs)

@app.route('/view/<organism>/<symbol>')
def view(organism, symbol):
	# if we came from the search page then we know the symbol has been
	# found already, othwerise was entered in the URL so do search
	if not request.referrer or not request.referrer.endswith('search'):
		genes = pd.find_gene(symbol, org_util.get_name(organism))
		if len(genes) == 1:
			symbol = genes[0][0]
		else:
			flash('Could not find gene: ' + symbol + ' in organism ' + organism)
			return redirect(url_for('search'))

	org_full_name = org_util.get_name(organism)
	homologs = pd.get_homologs_for_gene(symbol, org_full_name)

	# include starting gene in search
	all_orgs = dict(homologs)
	if not org_full_name in all_orgs:
		all_orgs[org_full_name] = {}
	all_orgs[org_full_name][symbol] = None

	# fetch pathways 
	pathways = []
	for org in all_orgs:
		for gene in all_orgs[org]:
			for gene_pathways in pd.get_pathways(gene, org):
				pathways.append(gene_pathways)

	# re-organise for display:  {pathway:  {organisms: [genes]}}
	table = defaultdict(lambda: defaultdict(list))
	for row in pathways:
		table[row[0]][row[1]].append(row[2])
	return render_template('view.html', symbol=symbol, organism=org_full_name, org_abbrev=organism, orgs=all_orgs, homologs=homologs, table=table)
	

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)


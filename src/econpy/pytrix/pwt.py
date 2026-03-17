"""Provides a simple class to extract data from the
Penn World Tables, which must be available in CSV format.
(E.g., download the Excel file from http://pwt.econ.upenn.edu/,
open it, and save as CSV.)
"""
import csv

class DataSet(object):
	"""Creates a dataset from the PWT (input as a CSV file).
	A data set is a collection of countries,
	where each country maps year(s) to the requested variable values
	(in the order requested).
	:requires: Python 2.6+ (tuples don't have an index method until 2.6)
	"""
	def __init__(self, pwt_csv, country_names=None, years=None, vnames=None):
		self.country_names = country_names
		self._countries = list()
		self.years = years
		self.vnames = vnames
		names2countries = dict()  #temporary variable to help data set construction
		with open(pwt_csv, "rb") as fh:
			reader = csv.reader(fh)
			headers = list( h.strip() for h in next(reader) )
			nitems = len(headers)
			vars_idx = tuple( headers.index(vname) for vname in vnames )
			name_idx = headers.index('country')
			try:
				iso_idx = headers.index('isocode')
			except ValueError: #must be an older PWT
				iso_idx = headers.index('country isocode')
			year_idx = headers.index('year')
			for line in reader:
				assert len(line)==nitems
				name = line[name_idx].strip() 
				iso = line[iso_idx].strip() 
				year = int( line[year_idx] )
				cond1 = years is None or year in years
				cond2 = country_names is None or name in country_names
				if cond1 and cond2:
					data =  tuple( line[i] for i in vars_idx )
					if ('' not in data) and ('na' not in data):  #use complete records only
						#add country to data set (if needed)
						country = names2countries.setdefault(name, Country(name, iso, self) )
						# add year to country's data
						country[year] = map(float, data)
					else:
						print "%s %d discarded (missing data)"%(name,year)
		self._countries = list( names2countries.values() )
	def get_iso(self, alpha3):
		"""Get country by ISO 3166-1 alpha-3 (three letter)
		country code.
		"""
		if len(alpha3) != 3:
			raise ValueError('See http://en.wikipedia.org/wiki/ISO_3166-1_alpha-3')
		for ctry in self.countries:
			if ctry.alpha3 == alpha3:
				return ctry
		raise ValueError('ISO code {0} not available.'.format(alpha3))
	def get_index(self, vname):
		return self.vnames.index(vname)
	@property
	def countries(self):
		return self._countries


class Country(dict):
	"""Provides individual country data storage,
	mapping year(s) to requested variable values
	(in the order requested at dataset construction).
	"""
	def __init__(self, name, alpha3, dataset=None):
		dict.__init__(self)
		self.name = name
		self.alpha3 = alpha3
		self.dataset = dataset
		"""
		self.rgdpwok = dict()
		self.rgdpch = dict()
		self.POP = dict()
		self.y = dict()
		"""
	def __str__(self):  # chk wise??
		return "%s (%s)"%(self.name,self.alpha3)
	def get_observation(self, year, vname):
		data = self[year]
		vname_idx = self.dataset.get_index(vname)
		return self[year][vname_idx]
	@property
	def vnames(self):
		return self.dataset.vnames


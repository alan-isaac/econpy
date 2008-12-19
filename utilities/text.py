"""
Simple text utilities.
- SimpleTable
- WordFreq

:contact: alan dot isaac at gmail dot com
:date: 2008-08-28
"""
from __future__ import division, with_statement
import sys, string, itertools
from collections import defaultdict

class SimpleTable:
	"""Produce a simple ASCII or LaTeX table from a 2D array of data.
	`data` is 2D rectangular iterable: lists of lists of text.
	At most one header row, which is length of data[0] (+1 if stubs)
	At most one stubs column, which must have length of data.
	See methods `default_txt_fmt` and `default_ltx_fmt` for formatting options.
	Sample use::

		mydata = [[11,12],[21,22]]
		myhdrs = "Column 1", "Column 2"
		mystubs = "Row 1", "Row 2"
		tbl = SimpleTable(mydata, myhdrs, mystubs)
		print( tbl.as_csv() )
		tbl = SimpleTable(mydata, myhdrs, mystubs, title="Title")
		print( tbl.as_text() )
		print( tbl.as_latex_tabular() )
	"""
	def __init__(self, data, headers=(), stubs=(), title='',
	csv_fmt=None, txt_fmt=None, ltx_fmt=None):
		"""
		:Parameters:
			data : list of lists
				R rows by K columns of table data
			headers: tuple
				sequence of K strings, one per header
			stubs: tuple
				sequence of R strings, one per stub
			txt_fmt : dict
				text formatting options
			ltx_fmt : dict
				latex formatting options
			csv_fmt : dict
				csv formatting options
		"""
		self.data = data
		self.headers = headers
		self.stubs = tuple(str(stub) for stub in stubs)
		self.title = title
		#start with default formatting
		self.txt_fmt = self.default_txt_fmt()
		self.ltx_fmt = self.default_ltx_fmt()
		self.csv_fmt = self.default_csv_fmt()
		#substitute any user specified formatting
		self.csv_fmt.update(csv_fmt or dict())
		self.txt_fmt.update(txt_fmt or dict())
		self.ltx_fmt.update(ltx_fmt or dict())
	def __str__(self):
		return self.as_text()
	def calc_colwidths(self, data):
		return [max(len(d) for d in c) for c in itertools.izip(*data)]
	def format_rows(self, data, colwidths, colaligns, colsep, pre='', post=''):
		"""Return: list of list of strings,
		the formatted data with headers and stubs.
		"""
		rows = []
		for row in data:
			cols = []
			for k in xrange(len(row)):
				align = colaligns[k]
				width = colwidths[k]
				d = str(row[k])  #convert to string if nec
				d = self.pad(d, width, align)
				cols.append(d)
			rows.append( pre + colsep.join(cols) + post )
		return rows
	def pad(self, s, width, align):
		if align == 'l':
			s = s.ljust(width)
		elif align == 'r':
			s = s.rjust(width)
		else:
			s = s.center(width)
		return s
	def format_data(self, fmt_dict):
		"""Return list of lists,
		the formatted data (without headers or stubs).
		Note: does *not* replace `self.data`."""
		data_fmt = fmt_dict.get('data_fmt','%s')
		return [[(data_fmt%drk).strip() for drk in dr] for dr in self.data] #is the 'strip' wise?
	def format_headers(self, fmt_dict, headers=None):
		"""Return list, the formatted headers."""
		header_fmt = fmt_dict.get('header_fmt','%s')
		headers2fmt = headers or self.headers
		return [header_fmt%header for header in headers2fmt]
	def format_stubs(self, fmt_dict, stubs=None):
		"""Return list, the formatted stubs."""
		stub_fmt = fmt_dict.get('stub_fmt','%s')
		stubs2fmt = stubs or self.stubs
		return [stub_fmt%stub for stub in stubs2fmt]
	def merge_table_parts(self, data, headers, stubs): #avoids copy but too implicit ...
		#insert stubs and headers
		for i in range(len(stubs)):
			data[i].insert(0,stubs[i])
		if headers:
			data.insert(0,headers)
		if stubs and headers:
			data[0].insert(0,'')
	def default_csv_fmt(self):
		dcf = dict(colsep=',', table_dec_above='', table_dec_below='', header_dec_below='', title_align='')
		colaligns = "l"*(len(self.data[0]))
		if self.stubs:
			colaligns = "l" + colaligns
		dcf['colaligns'] = colaligns
		dcf['data_fmt'] = '%s'
		dcf['header_fmt'] = '"%s"'
		dcf['stub_fmt'] = '"%s"'
		return dcf
	def default_txt_fmt(self):
		dtf = dict(colsep=' ', table_dec_above='=', table_dec_below='-', header_dec_below='-', title_align='c')
		colaligns = "c"*(len(self.data[0]))
		if self.stubs:
			colaligns = "l" + colaligns
		dtf['colaligns'] = colaligns
		dtf['data_fmt'] = "%s"
		return dtf
	def default_ltx_fmt(self):
		dlf = dict(colsep=' & ', table_dec_above=r'\toprule', table_dec_below=r'\bottomrule', header_dec_below=r'\midrule')
		colaligns = "c"*(len(self.data[0]))
		if self.stubs:
			colaligns = "l" + colaligns
		dlf['colaligns'] = colaligns
		dlf['strip_backslash'] = True
		dlf['data_fmt'] = "%s"
		dlf['header_fmt'] = "\\textbf{%s}"
		dlf['stub_fmt'] = "\\textbf{%s}"
		return dlf
	def as_csv(self, **fmt):
		#fetch the format, which may just be default_csv_format
		fmt_dict = self.csv_fmt.copy()
		#update format using `fmt`
		fmt_dict.update(fmt)
		return self.as_text(**fmt_dict).replace(' ','')
	def as_text(self, **fmt):  #allow changing fmt here?
		fmt_dict = self.txt_fmt.copy()
		fmt_dict.update(fmt)
		#data_fmt="%s", header_fmt="%s", stub_fmt="%s", colsep=" ", colaligns='', colwidths=(), header_dec=''):
		#format the 3 table parts (data, headers, stubs) and merge
		txt_data = self.format_data(fmt_dict)
		txt_headers = self.format_headers(fmt_dict)
		txt_stubs = self.format_stubs(fmt_dict)
		self.merge_table_parts(txt_data, txt_headers, txt_stubs)
		try:
			colwidths = fmt_dict['colwidths']
			assert len(colwidths)==len(txt_data[0])
		except:
			colwidths = self.calc_colwidths(txt_data)
		colaligns = fmt_dict['colaligns']
		colsep = fmt_dict['colsep']
		rows = self.format_rows(txt_data, colwidths, colaligns, colsep)
		headerlen = len(rows[0])
		begin = ''
		if self.title:
			begin += self.pad(self.title, headerlen, fmt_dict['title_align'])
		above = fmt_dict['table_dec_above']
		if above:
			begin += "\n" + above*headerlen
		if txt_headers:
			hdec = fmt_dict['header_dec_below']
			if hdec:
				rows[0] = rows[0] + "\n" + hdec*headerlen
		end = ''
		below = fmt_dict['table_dec_below']
		if below:
			end = below*headerlen + "\n" + end
		return begin + "\n" + '\n'.join(rows) + "\n" + end
	def as_latex_tabular(self, **fmt):
		'''Requires the booktabs package'''
		fmt_dict = self.ltx_fmt.copy()
		fmt_dict.update(fmt)
		ltx_data = self.format_data(fmt_dict)
		if fmt_dict['strip_backslash']:
			ltx_headers = [header.replace("\\","$\\backslash$") for header in self.headers]
			ltx_stubs = [stub.replace("\\","$\\backslash$") for stub in self.stubs]
		ltx_headers = self.format_headers(fmt_dict, ltx_headers)
		ltx_stubs = self.format_stubs(fmt_dict, ltx_stubs)
		try:
			colaligns = fmt_dict['colaligns']
		except:
			colaligns = "c"*(len(ltx_data[0]))
			if ltx_stubs:
				colaligns = "l" + colaligns
		self.merge_table_parts(ltx_data, ltx_headers, ltx_stubs)
		#this just formats output; add real colwidths?
		try:
			colwidths = fmt_dict['colwidths']
			assert len(colwidths)==len(ltx_data[0])
		except:
			colwidths = self.calc_colwidths(ltx_data)
		colsep = fmt_dict['colsep']
		rows = self.format_rows(ltx_data, colwidths, colaligns, colsep, post=r'  \\')
		begin = r'\begin{tabular}{%s}'%colaligns
		above = fmt_dict['table_dec_above']
		if above:
			begin += "\n" + above + "\n"
		if ltx_headers:
			hdec = fmt_dict['header_dec_below']
			if hdec:
				rows[0] = rows[0] + "\n" + hdec
		end = r'\end{tabular}'
		below = fmt_dict['table_dec_below']
		if below:
			end = below + "\n" + end
		return begin + '\n'.join(rows) + "\n" + end


class WordFreq:
	"""Summarize text file word counts.
	"""
	def __init__(self, filename, **kw):
		self.filename = filename
		self.params = kw
		self.result = self.describe()
	def describe(self):
		"""
		might want, e.g.,
		START_AFTER = ".. begin wordcount",
		"""
		params = dict(
		start_after = '',
		wordsize_min = 3,
		freq_min = 2
		)
		params.update(self.params)
		self.params = params
		start_after = params['start_after']
		wordsize_min = params['wordsize_min']
		chars2strip = string.punctuation
		ct_words = 0
		ct_longwords = 0
		word_hash = defaultdict(int)
		with open(self.filename,'r') as fh:
			for line in fh:
				while start_after:
					if line.startswith(START_AFTER):
						start_after = False
					continue
				line.strip()
				for word in line.split():
					word = word.strip(chars2strip)
					if word:
						ct_words += 1
					if len(word) >= wordsize_min:
						ct_longwords += 1
						word_hash[word] += 1
		result = dict(word_hash=word_hash,
		ct_words=ct_words,
		ct_longwords=ct_longwords
		)
		return result
	def summarize(self):
		freq_min = self.params['freq_min']
		result = self.result
		fmt = "%24s %6d"
		print "Results for 'longer' words (length >= %(wordsize_min)d)."%self.params
		print """
		=================================================
		=============== WORD COUNT ======================
		=================================================
		Total number of words: %(ct_words)d
		Total number of 'longer' words : %(ct_longwords)d
		"""%result

		print """
		=================================================
		=============== ALPHA ORDER =====================
		=================================================
		"""
		for k,v in sorted( result['word_hash'].iteritems() ):
			if v >= freq_min:
				print fmt%(k,v)
		print """
		=================================================
		============ OCCURRENCE ORDER ===================
		=================================================
		"""
		for k,v in sorted( result['word_hash'].iteritems(), key = lambda x: (-x[1], x[0]) ):
			if v >= freq_min:
				print fmt%(k,v)


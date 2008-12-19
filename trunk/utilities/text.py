"""
Simple text utilities.
- SimpleTable
- WordFreq

Note that this module depends only on the Python standard library.
You can "install" it just by dropping it into your working directory.

:contact: alan dot isaac at gmail dot com
:date: 2008-12-19
:requires: Python 2.5.1+
"""
from __future__ import division, with_statement
import sys, string
from itertools import izip
from collections import defaultdict

class SimpleTable:
	"""Produce a simple ASCII, CSV, or LaTeX table from a
	rectangular array of data, presumed to be numerical. 
	Supports at most one header row,
	which must be the length of data[0] (or +1 if stubs).
	Supports at most one stubs column, which must be the length of data.
	See methods `default_txt_fmt`, `default_csv_fmt`,
	and `default_ltx_fmt` for formatting options.

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
			data : list of lists or 2d array
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
	#def _format_rows(self, data, colwidths, datacols_align, colsep, pre='', post=''):
	def _format_rows(self, data, fmt_dict):
		"""Return: list of strings,
		the formatted data with headers and stubs.
		"""
		colwidths = self.get_colwidths(data, fmt_dict)
		cols_align = self.get_cols_aligns(fmt_dict)
		datacols_align = fmt_dict['datacols_align']
		colsep = fmt_dict['colsep']
		pre = fmt_dict.get('pre','')
		post = fmt_dict.get('post','')
		rows = []
		for row in data:
			cols = []
			for k in xrange(len(row)):
				align = datacols_align[k]
				width = colwidths[k]
				d = str(row[k])  #convert to string if nec
				d = self.pad(d, width, align)
				cols.append(d)
			rows.append( pre + colsep.join(cols) + post )
		return rows
	def pad(self, s, width, align):
		"""Return string padded with spaces,
		based on alignment parameter."""
		if align == 'l':
			s = s.ljust(width)
		elif align == 'r':
			s = s.rjust(width)
		else:
			s = s.center(width)
		return s
	def _format_data(self, fmt_dict):
		"""Return list of lists,
		the formatted data (without headers or stubs).
		Note: does *not* change `self.data`."""
		data_fmt = fmt_dict.get('data_fmt','%s')
		return [[(data_fmt%drk) for drk in dr] for dr in self.data]
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
	def merge_table_parts(self, data, headers, stubs): #avoids copy; too implicit?
		"""Return None. Insert stubs and headers into `data`."""
		for i in range(len(stubs)):
			data[i].insert(0,stubs[i])
		if headers:
			data.insert(0,headers)
		if stubs and headers:
			data[0].insert(0,'')
	def as_csv(self, **fmt):
		"""Return string, the table in CSV format.
		Currently only supports comma separator."""
		#fetch the format, which may just be default_csv_format
		fmt_dict = self.csv_fmt.copy()
		#update format using `fmt`
		fmt_dict.update(fmt)
		return self.as_text(**fmt_dict)
	def as_text(self, **fmt):  #allow changing fmt here?
		"""Return string, the table as text."""
		fmt_dict = self.txt_fmt.copy()
		fmt_dict.update(fmt)
		#data_fmt="%s", header_fmt="%s", stub_fmt="%s", colsep=" ", datacols_align='', colwidths=(), header_dec=''):
		#format the 3 table parts (data, headers, stubs) and merge in list of lists
		# first get data as 2d list of strings (no headers or stubs)
		txt_data = self._format_data(fmt_dict)
		txt_headers = self.format_headers(fmt_dict)
		txt_stubs = self.format_stubs(fmt_dict)
		self.merge_table_parts(txt_data, txt_headers, txt_stubs)
		#do a column width check before formatting
		rows = self._format_rows(txt_data, fmt_dict)
		headerlen = len(rows[0])
		begin = ''
		if self.title:
			begin += self.pad(self.title, headerlen, fmt_dict['title_align'])
		#decoration above the table, if desired
		table_dec_above = fmt_dict['table_dec_above']
		if table_dec_above:
			begin += "\n" + table_dec_above*headerlen
		if txt_headers:
			hdec = fmt_dict['header_dec_below']
			if hdec:
				rows[0] = rows[0] + "\n" + hdec*headerlen
		end = ''
		below = fmt_dict['table_dec_below']
		if below:
			end = below*headerlen + "\n" + end
		return begin + "\n" + '\n'.join(rows) + "\n" + end
	def get_colwidths(self, datastrings, fmt_dict):
		"""Return list of int, the column widths.
		Ensure comformable colwidths in `fmt_dict`.
		Other, compute as the max width for each column of `datastrings`.
		Note that `datastrings` is a rectangular iterable of strings.
		"""
		colwidths = fmt_dict.get('colwidths')
		if colwidths is None or len(colwidths) != len(ltx_data[0]):
			if fmt_dict.get('fmt') in ('txt', 'ltx'):
				colwidths = [max(len(d) for d in c) for c in izip(*datastrings)]
			else:
				colwidths = [0] * len( datastrings[0] )
		return colwidths
	def get_cols_aligns(self, fmt_dict):
		"""Return string, sequence of column alignments.
		Ensure comformable datacols_align in `fmt_dict`."""
		ncols = len(self.data[0])
		cols_aligns = fmt_dict.get('cols_aligns')
		if cols_aligns is None or len(cols_aligns) != ncols:
			if self.stubs:
				ncols -= 1
				stubs_align = fmt_dict.get('stubs_align')
				if stubs_align is None:
					stubs_align = 'l'
			else:
				stubs_align = ''
			datacols_align = fmt_dict.get('datacols_align')
			if datacols_align is None:
				datacols_align = 'c'
			cols_aligns = stubs_align + datacols_align*(ncols)
		return cols_aligns
	def as_latex_tabular(self, **fmt):
		'''Return string, the table as a LaTeX tabular environment.
		Note: will equire the booktabs package.'''
		fmt_dict = self.ltx_fmt.copy()
		fmt_dict.update(fmt)
		ltx_data = self._format_data(fmt_dict)
		if fmt_dict['strip_backslash']:
			ltx_headers = [header.replace("\\","$\\backslash$") for header in self.headers]
			ltx_stubs = [stub.replace("\\",r'$\backslash$') for stub in self.stubs]
		ltx_headers = self.format_headers(fmt_dict, ltx_headers)
		ltx_stubs = self.format_stubs(fmt_dict, ltx_stubs)
		#check column alignments *before* data merge
		self.merge_table_parts(ltx_data, ltx_headers, ltx_stubs)
		#this just formats output; add real colwidths?
		fmt_dict['post'] = r'  \\'
		#rows = self._format_rows(ltx_data, datacols_align, colsep, post=)
		rows = self._format_rows(ltx_data, fmt_dict)
		datacols_align = fmt_dict['datacols_align']
		begin = r'\begin{tabular}{%s}'%datacols_align
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
	#########  begin: default formats  ##############
	def default_csv_fmt(self):
		dcf = dict(
			data_fmt = '%s',
			colsep = ',',
			table_dec_above = '',
			table_dec_below = '',
			header_dec_below = '',
			title_align = '',
			header_fmt = '"%s"',
			stub_fmt = '"%s"',
			fmt = 'csv',
			)
		datacols_align = "l"*(len(self.data[0]))
		if self.stubs:
			datacols_align = "l" + datacols_align
		dcf['datacols_align'] = datacols_align
		return dcf
	def default_txt_fmt(self):
		dtf = dict(
			data_fmt = "%s",
			colsep=' ',
			table_dec_above='=',
			table_dec_below='-',
			header_dec_below='-',
			title_align='c',
			stubs_align = 'l',
			fmt = 'txt',
			)
		datacols_align = "c"*(len(self.data[0]))
		if self.stubs:
			datacols_align = "l" + datacols_align
		dtf['datacols_align'] = datacols_align
		return dtf
	def default_ltx_fmt(self):
		dlf = dict(
			data_fmt = "%s",
			colsep=' & ',
			table_dec_above = r'\toprule',
			table_dec_below = r'\bottomrule',
			header_dec_below = r'\midrule',
			strip_backslash = True,
			header_fmt = "\\textbf{%s}",
			stub_fmt = "\\textbf{%s}",
			fmt = 'ltx',
			)
		datacols_align = "c"*(len(self.data[0]))
		if self.stubs:
			datacols_align = "l" + datacols_align
		dlf['datacols_align'] = datacols_align
		return dlf
	#########  end: default formats  ##############


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


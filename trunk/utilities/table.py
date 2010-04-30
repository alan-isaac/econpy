"""
Simple table class.
Note that this module depends only on the Python standard library.
You can "install" it just by dropping it into your working directory.

Potential problems for Python 3: calls ``next`` instead of ``__next__``.

:contact: alan dot isaac at gmail dot com
:requires: Python 2.5.1+
:note: HTML data format currently specifies tags
:todo: add support for recarray to SimpleTable
:todo: support a bit more of http://www.oasis-open.org/specs/tr9503.html
:date: 2008-12-21
"""
from __future__ import division, with_statement
import sys, string
from itertools import cycle, ifilter, izip
from collections import defaultdict
import csv

def csv2st(csvfile, headers=False, stubs=False, title=None):
	"""Return SimpleTable instance,
	created from the data in `csvfile`,
	which is in comma separated values format.
	The first row may contain headers: set headers=True.
	The first column may contain stubs: set stubs=True.
	Can also supply headers and stubs as tuples of strings.
	"""
	rows = list()
	with open(csvfile,'r') as fh:
		reader = csv.reader(fh)
		if headers is True:
			headers = reader.next()
		elif headers is False:
			headers=()
		if stubs is True:
			stubs = list()
			for row in reader:
				if row:
					stubs.append(row[0])
					rows.append(row[1:])
		else: #no stubs, or stubs provided
			for row in reader:
				if row:
					rows.append(row)
		if stubs is False:
			stubs = ()
	nrows = len(rows)
	ncols = len(rows[0])
	if any(len(row)!=ncols for row in rows):
		raise IOError('All rows of CSV file must have same length.')
	return SimpleTable(data=rows, headers=headers, stubs=stubs)

class SimpleTable(list):
	"""Produce a simple ASCII, CSV, HTML, or LaTeX table from a
	*rectangular* array of data, not necessarily numerical. 
	Supports at most one header row,
	which must be the length of data[0] (or +1 if stubs).
	Supports at most one stubs column, which must be the length of data.
	See globals `default_txt_fmt`, `default_csv_fmt`, `default_html_fmt`,
	and `default_latex_fmt` for formatting options.

	Sample uses::

		mydata = [[11,12],[21,22]]
		myheaders = "Column 1", "Column 2"
		mystubs = "Row 1", "Row 2"
		tbl = text.SimpleTable(mydata, myheaders, mystubs, title="Title")
		print( tbl )
		print( tbl.as_html() )
		# set column specific data formatting
		tbl = text.SimpleTable(mydata, myheaders, mystubs,
			fmt={'data_fmt':["%3.2f","%d"]})
		print( tbl.as_csv() )
		with open('c:/temp/temp.tex','w') as fh:
			fh.write( tbl.as_latex_tabular() )
	"""
	def __init__(self, data, headers=(), stubs=(), title='', formatter=None,
		fmt=None, csv_fmt=None, txt_fmt=None, ltx_fmt=None, html_fmt=None):
		"""
		Parameters
		----------
		data : list of lists or 2d array (not matrix!)
			R rows by K columns of table elements
		headers: tuple
			sequence of K strings, one per header
		stubs : tuple
			sequence of R strings, one per stub
		fmt : dict
			formatting options
		txt_fmt : dict
			text formatting options
		ltx_fmt : dict
			latex formatting options
		csv_fmt : dict
			csv formatting options
		hmtl_fmt : dict
			hmtl formatting options
		"""
		#self._raw_data = data
		self.headers = headers
		self.stubs = tuple(str(stub) for stub in stubs)
		self.title = title
		#start with default formatting
		self.txt_fmt = default_txt_fmt.copy()
		self.ltx_fmt = default_latex_fmt.copy()
		self.csv_fmt = default_csv_fmt.copy()
		self.html_fmt = default_html_fmt.copy()
		#substitute any user specified formatting
		if fmt:
			self.csv_fmt.update(fmt)
			self.txt_fmt.update(fmt)
			self.ltx_fmt.update(fmt)
			self.html_fmt.update(fmt)
		self.csv_fmt.update(csv_fmt or dict())
		self.txt_fmt.update(txt_fmt or dict())
		self.ltx_fmt.update(ltx_fmt or dict())
		self.html_fmt.update(html_fmt or dict())
		self.output_formats = dict(
			text=self.txt_fmt,
			txt=self.txt_fmt,
			csv=self.csv_fmt,
			html=self.html_fmt,
			latex=self.ltx_fmt)
		rows = self._make_rows(data)  # a list of Row instances
		list.__init__(self, rows)
	def __str__(self):
		return self.as_text()
	def _make_rows(self, raw_data):
		rows = self._data2rows(raw_data)
		headers = self.headers
		stubs = self.stubs
		for i, stub in enumerate(stubs):
			row = rows[i]
			cell = Cell(data=stub, datatype='stub')
			cell.row = row
			row.insert_stub(cell)
		if headers:
			headers = Row([Cell(h) for h in headers])
			headers.datatype = 'header'
			headers.table = self
			if stubs:
				headers.insert_stub(Cell('','stub'))
			rows.insert(0,headers)
			for cell in headers:
				cell.datatype = 'header'
				cell.row = headers
		return rows
	def _data2rows(self, raw_data):
		rows = []
		for datarow in raw_data:
			newrow = Row([Cell(datum) for datum in datarow])
			newrow.table = self  #row knows its SimpleTable
			for cell in newrow:
				cell.datatype = 'data'
				cell.row = newrow  #a cell knows its row
			rows.append( newrow)
		return rows
	def _format_rows(self, tablestrings, fmt_dict):
		"""Return: list of strings,
		the formatted table data *including* headers and stubs.
		Note that `tablestrings` is a *rectangular* iterable of strings.
		"""
		#fmt = fmt_dict['fmt']
		colwidths = self.get_colwidths(tablestrings, fmt_dict)
		cols_aligns = self.get_cols_aligns(fmt_dict)
		colsep = fmt_dict['colsep']
		row_pre = fmt_dict.get('row_pre','')
		row_post = fmt_dict.get('row_post','')
		rows = []
		for row in tablestrings:
			cols = []
			for content, width, align in izip(row, colwidths, cols_aligns):
				content = pad(content, width, align)
				cols.append(content)
			rows.append( row_pre + colsep.join(cols) + row_post )
		return rows
	def pad(self, s, width, align):
		"""DEPRECATED: just use the pad function"""
		return pad(s, width, align)
	'''
	def merge_table_parts(self, fmt_dict=dict()):
		"""Return list of lists of strings,
		all table parts merged.
		Inserts stubs and headers into `data`."""
		data = self.format_data(fmt_dict)
		headers = self.format_headers(fmt_dict)
		stubs = self.format_stubs(fmt_dict)
		for i in range(len(stubs)):
			data[i].insert(0,stubs[i])
		if headers:
			data.insert(0,headers)
		return data
	def format_data(self, fmt_dict):
		"""Return list of lists,
		the formatted data (without headers or stubs).
		Note: does *not* change `self._raw_data`."""
		data_fmt = fmt_dict.get('data_fmt','%s')
		if isinstance(data_fmt, str):
			result = [[(data_fmt%datum) for datum in row] for row in self._raw_data]
		else:
			fmt = cycle( data_fmt )
			result = [[(fmt.next()%datum) for datum in row] for row in self._raw_data]
		return result
	def format_headers(self, fmt_dict, headers=None):
		"""Return list, the formatted headers."""
		dcols = len(self._raw_data[0])
		headers2fmt = list(headers or self.headers)
		header_fmt = fmt_dict.get('header_fmt') or '%s'
		if self.stubs and len(headers2fmt)==dcols:
			headers2fmt.insert(0,'')
		return [header_fmt%(header) for header in headers2fmt]
	def format_stubs(self, fmt_dict, stubs=None):
		"""Return list, the formatted stubs."""
		stub_fmt = fmt_dict.get('stub_fmt','%s')
		stubs2fmt = stubs or self.stubs
		return [stub_fmt%stub for stub in stubs2fmt]
	'''
	def get_colwidths_from_cells(self, output_format):
		colwidths = []
		for col in izip(*self):
			colwidths.append(max(len(c.as_string(output_format)) for c in col))
		return colwidths
	def get_colwidths(self, tablestrings, fmt_dict):
		"""Return list of int, the column widths.
		Ensure comformable colwidths in `fmt_dict`.
		Other, compute as the max width for each column of `tablestrings`.
		Note that `tablestrings` is a rectangular iterable of strings.
		"""
		ncols = len(tablestrings[0])
		request_widths = fmt_dict.get('colwidths')
		if request_widths is None:
			result = [0] * ncols
		else:
			min_widths = [max(len(d) for d in c) for c in izip(*tablestrings)]
			if isinstance(request_widths, int):
				request_widths = cycle([request_widths])
			elif len(request_widths) != ncols:
				request_widths = min_widths
			result = [max(m,r) for m,r in izip(min_widths, request_widths)]
		return result
	def get_cols_aligns(self, fmt_dict):
		"""Return string, sequence of column alignments.
		Ensure comformable data_aligns in `fmt_dict`."""
		has_stubs = bool(self.stubs)
		dcols = len(self[0]) - has_stubs  # number of data columns
		cols_aligns = fmt_dict.get('cols_aligns')
		if cols_aligns is None or len(cols_aligns) != dcols + has_stubs:
			if has_stubs:
				stubs_align = fmt_dict.get('stubs_align') or 'l'
				assert len(stubs_align)==1
			else:
				stubs_align = ''
			data_aligns = fmt_dict.get('data_aligns') or 'c'
			if len(data_aligns) != dcols:
				c = cycle(data_aligns)
				data_aligns = ''.join(c.next() for _ in range(dcols))
			cols_aligns = stubs_align + data_aligns
		return cols_aligns
	def as_csv(self, **fmt_dict):
		"""Return string, the table in CSV format.
		Currently only supports comma separator."""
		#fetch the format, which may just be default_csv_format
		fmt = self.output_formats['csv'].copy()
		#update format using `fmt`
		fmt.update(fmt_dict)
		return self.as_text(**fmt)
	def as_text(self, **fmt_dict):
		"""Return string, the table as text."""
		#fetch the format, which may just be default_csv_format
		fmt = self.output_formats['text'].copy()
		#update format using `fmt`
		fmt.update(fmt_dict)
		#format table body, including header and header decoration (if any)
		#colwidths = self.get_colwidths_from_cells(output_format='html') #chk
		#cols_aligns = self.get_cols_aligns(fmt)
		formatted_rows = [] #list of strings
		for row in self:
			formatted_rows.append( row.as_string('text', **fmt) )
		formatted_table_body = '\n'.join(formatted_rows)

		"""
		#format the 3 table parts (data, headers, stubs) and merge in list of lists
		txt_data = self.merge_table_parts(fmt)
		rows = self._format_rows(txt_data, fmt)
		"""
		rowlen = len(formatted_rows[-1]) #don't use header row
		begin = ''
		if self.title:
			begin += pad(self.title, rowlen, fmt.get('title_align','c'))
		#decoration above the table, if desired
		table_dec_above = fmt.get('table_dec_above','=')
		if table_dec_above:
			begin += "\n" + (table_dec_above * rowlen)
		below = fmt.get('table_dec_below','-')
		end = (below*rowlen + "\n") if below else ''
		return begin + '\n' + formatted_table_body + '\n' + end
	def as_html(self, **fmt_dict):
		"""Return string.
		This is the default formatter for HTML tables.
		An HTML table formatter must accept as arguments
		a table and a format dictionary.
		"""
		fmt = self.output_formats['html'].copy()
		fmt.update(fmt_dict)

		#format table body, including header and header decoration (if any)
		#colwidths = self.get_colwidths_from_cells(output_format='html') #chk
		#cols_aligns = self.get_cols_aligns(fmt)
		formatted_rows = [] #list of strings
		for row in self:
			formatted_rows.append( row.as_string('html', **fmt) )
		formatted_table_body = '\n'.join(formatted_rows)

		begin = "<table class='simpletable'>"
		if self.title:
			begin += "<caption>%s</caption>\n"%(self.title,)
		end = r'</table>'
		return begin + '\n' + formatted_table_body + "\n" + end
	def as_latex_tabular(self, **fmt_dict):
		'''Return string, the table as a LaTeX tabular environment.
		Note: will equire the booktabs package.'''
		fmt = self.output_formats['latex'].copy()
		fmt.update(fmt_dict)
		"""
		if fmt_dict['strip_backslash']:
			ltx_stubs = [stub.replace('\\',r'$\backslash$') for stub in self.stubs]
			ltx_headers = [header.replace('\\',r'$\backslash$') for header in self.headers]
			ltx_headers = self.format_headers(fmt_dict, ltx_headers)
		else:
			ltx_headers = self.format_headers(fmt_dict)
		ltx_stubs = self.format_stubs(fmt_dict, ltx_stubs)
		"""
		formatted_rows = [] #list of strings
		for row in self:
			formatted_rows.append( row.as_string('latex', **fmt) )
		formatted_table_body = '\n'.join(formatted_rows)

		begin = r'\begin{tabular}{%s}'%(self.get_cols_aligns(fmt))
		above = fmt['table_dec_above']
		if above:
			begin += "\n" + above
		end = r'\end{tabular}'
		below = fmt['table_dec_below']
		if below:
			end = below + "\n" + end
		return begin + '\n' + formatted_table_body + "\n" + end
	def extend_right(self, table):
		for row1, row2 in izip(self, table):
			row1.extend(row2)
	@property
	def data(self):
		return [row.data for row in self]
#END: class SimpleTable

def pad(s, width, align):
	"""Return string padded with spaces,
	based on alignment parameter."""
	if align == 'l':
		s = s.ljust(width)
	elif align == 'r':
		s = s.rjust(width)
	else:
		s = s.center(width)
	return s

class Cell(object):
	def __init__(self, data='', datatype='data', row=None):
		self.data = data
		self.datatype = datatype
		self.row = row
	def as_string(self, output_format='txt', **fmt_dict):
		"""Return string.
		This is the default formatter for cells.
		Override this to get different formating.
		A cell formatter must accept as arguments
		a cell (self) and an output format,
		one of ('html', 'txt', 'csv', 'latex').
		It will generally respond to the datatype,
		one of ('data', 'header', 'stub').
		"""
		try:
			fmt = default_fmts[output_format].copy()
		except KeyError:
			raise ValueError('Unknown format: %s' % output_format)
		fmt.update(fmt_dict)

		datatype = self.datatype
		data = self.data
		if datatype == 'data':
			data_fmt = fmt.get('data_fmt','%s')
			result = data_fmt % data
		elif datatype == 'header':
			data_fmt = fmt.get('header_fmt','%s')
			result = data_fmt % data
		elif datatype == 'stub':
			data_fmt = fmt.get('stub_fmt','%s')
			result = data_fmt % data
		else:
			raise ValueError('Unknown cell type: %s'%datatype)
		return result




class Row(list):
	"""A Row is a list of cells;
	a row can belong to a SimpleTable.
	"""
	def __init__(self, cells, datatype='', table=None, formatter=None):
		"""
		Parameters
		----------
		table : SimpleTable
		"""
		list.__init__(self, cells)
		self.datatype = datatype # data or header
		self.table = table
		self.formatter = formatter
	def insert_stub(self, stub):
		self.insert(0, stub)
	@property
	def data(self):
		return [cell.data for cell in self]
	def as_string(self, output_format='txt', **fmt_dict):
		"""Return string.
		This is the default formatter for rows.
		Override this to get different formatting.
		A row formatter must accept as arguments
		a row (self) and an output format,
		one of ('html', 'txt', 'csv', 'latex').
		"""
		try:
			fmt = default_fmts[output_format].copy()
		except KeyError:
			raise ValueError('Unknown format: %s' % output_format)
		fmt.update(fmt_dict)

		#:TODO: find better approach to this?
		colwidths = fmt.get('colwidths')
		cols_aligns = fmt.get('cols_aligns')
		if colwidths is None:
			try:
				colwidths = self.table.get_colwidths_from_cells(output_format=output_format)
			except AttributeError:
				colwidths = (0,) * len(self)
		if cols_aligns is None:
			try:
				cols_aligns = self.table.get_cols_aligns(fmt)
			except AttributeError:
				cols_aligns = 'c' * len(self)

		colsep = fmt['colsep']
		row_pre = fmt.get('row_pre','')
		row_post = fmt.get('row_post','')
		formatted_cells = []
		for cell, width, align in izip(self, colwidths, cols_aligns):
			content = cell.as_string(output_format=output_format)
			content = pad(content, width, align)
			formatted_cells.append(content)
		header_dec_below = fmt.get('header_dec_below')
		formatted_row = row_pre + colsep.join(formatted_cells) + row_post
		if self.datatype == 'header' and header_dec_below:
			formatted_row = self.decorate_header(formatted_row, output_format, header_dec_below)
		return formatted_row
	def decorate_header(self, header_as_string, output_format, header_dec_below):
		"""This really only makes sense for the text and latex output formats."""
		if output_format in ('text','txt'):
			row0len = len(header_as_string)
			result = header_as_string + "\n" + (header_dec_below * row0len)
		elif output_format == 'latex':
			result = header_as_string + "\n" + header_dec_below
		else:
			raise ValueError("I can't decorate a %s header."%output_format)
		return result
		
			

#########  begin: default formats for SimpleTable  ##############
default_csv_fmt = dict(
		data_fmt = '%s',
		colwidths = None,
		colsep = ',',
		row_pre = '',
		row_post = '',
		table_dec_above = '',
		table_dec_below = '',
		header_dec_below = '',
		header_fmt = '"%s"',
		stub_fmt = '"%s"',
		title_align = '',
		stubs_align = "l",
		data_aligns = "l",
		fmt = 'csv',
		)
	
default_html_fmt = dict(
		data_fmt = "<td>%s</td>",
		colwidths = None,
		colsep=' ',
		row_pre = '<tr>\n  ',
		row_post = '\n</tr>',
		table_dec_above=None,
		table_dec_below=None,
		header_dec_below=None,
		header_fmt = '<th>%s</th>',
		stub_fmt = '<th>%s</th>',
		title_align='c',
		data_aligns = "c",
		stubs_align = "l",
		fmt = 'html',
		)

default_txt_fmt = dict(
		data_fmt = "%s",
		colwidths = None,
		colsep=' ',
		row_pre = '',
		row_post = '',
		table_dec_above='=',
		table_dec_below='-',
		header_dec_below='-',
		header_fmt = '%s',
		stub_fmt = '%s',
		title_align='c',
		data_aligns = "c",
		stubs_align = "l",
		fmt = 'txt',
		)

default_latex_fmt = dict(
		data_fmt = "%s",
		colwidths = None,
		colsep=' & ',
		table_dec_above = r'\toprule',
		table_dec_below = r'\bottomrule',
		header_dec_below = r'\midrule',
		strip_backslash = True,
		header_fmt = "\\textbf{%s}",
		stub_fmt = "\\textbf{%s}",
		data_aligns = "c",
		stubs_align = "l",
		fmt = 'ltx',
		row_post = r'  \\'
		)
default_fmts = dict(
html= default_html_fmt,
htm= default_html_fmt,
txt=default_txt_fmt,
text=default_txt_fmt,
latex=default_latex_fmt,
ltx=default_latex_fmt,
csv=default_csv_fmt
)
#########  end: default formats  ##############



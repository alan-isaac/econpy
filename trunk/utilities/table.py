"""
Simple table class.
Note that this module depends only on the Python standard library.
You can "install" it just by dropping it into your working directory.

A SimpleTable is inherently (but not rigidly) rectangular.
A SimpleTable can be concatenated with another SimpleTable
or extended by another SimpleTable. ::

	table1.extend_right(table2)
	table1.extend(table2)

Although a SimpleTable only allows one column (the first) of stubs,
concatenation allows you to produce tables with interior stubs.
(You can also assign the datatype 'stub' to the cells in any column.)

Potential problems for Python 3
-------------------------------

- Calls ``next`` instead of ``__next__``.
  The 2to3 tool should handle that no problem.
- from __future__ import division, with_statement
- from itertools import izip as zip
- Let me know if you find other problems.

:contact: alan dot isaac at gmail dot com
:requires: Python 2.5.1+
:note: HTML data format currently specifies tags
:todo: support a bit more of http://www.oasis-open.org/specs/tr9503.html
:todo: add colspan support to Cell
:date: 2008-12-21
"""
from __future__ import division, with_statement
import sys, string
try: #accommodate Python 3
	from itertools import izip as zip
except ImportError:
	pass
from itertools import cycle, ifilter
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
	def __init__(self, data, headers=(), stubs=(), title='', 
		datatypes=None,
		csv_fmt=None, txt_fmt=None, ltx_fmt=None, html_fmt=None,
		celltype= None, rowtype=None,
		**fmt_dict):
		"""
		Parameters
		----------
		data : list of lists or 2d array (not matrix!)
			R rows by K columns of table elements
		headers: tuple
			sequence of K strings, one per header
		stubs : tuple
			sequence of R strings, one per stub
		title: string
			title of the table
		datatypes : list of int
			indexes to `data_fmts`
		txt_fmt : dict
			text formatting options
		ltx_fmt : dict
			latex formatting options
		csv_fmt : dict
			csv formatting options
		hmtl_fmt : dict
			hmtl formatting options
		fmt_dict : dict
			general formatting options
		"""
		#self._raw_data = data
		self.headers = headers
		self.stubs = tuple(str(stub) for stub in stubs)
		self.title = title
		self._datatypes = datatypes or range(len(data[0]))
		#start with default formatting
		self._text_fmt = default_txt_fmt.copy()
		self._latex_fmt = default_latex_fmt.copy()
		self._csv_fmt = default_csv_fmt.copy()
		self._html_fmt = default_html_fmt.copy()
		#substitute any general user specified formatting
		#:note: will be overridden by output specific arguments
		self._csv_fmt.update(fmt_dict)
		self._text_fmt.update(fmt_dict)
		self._latex_fmt.update(fmt_dict)
		self._html_fmt.update(fmt_dict)
		#substitute any output-type specific formatting
		self._csv_fmt.update(csv_fmt or dict())
		self._text_fmt.update(txt_fmt or dict())
		self._latex_fmt.update(ltx_fmt or dict())
		self._html_fmt.update(html_fmt or dict())
		self.output_formats = dict(
			text=self._text_fmt,
			txt=self._text_fmt,
			csv=self._csv_fmt,
			htm=self._html_fmt,
			html=self._html_fmt,
			latex=self._latex_fmt,
			ltx=self._latex_fmt)
		self._Cell = celltype or Cell
		self._Row = rowtype or Row
		rows = self._make_rows(data)  # a list of Row instances
		list.__init__(self, rows)
	def __str__(self):
		return self.as_text()
	def _make_rows(self, raw_data):
		_Cell = self._Cell
		_Row = self._Row
		rows = self._data2rows(raw_data)
		headers = self.headers
		stubs = self.stubs
		for i, stub in enumerate(stubs):
			row = rows[i]
			cell = _Cell(data=stub, datatype='stub')
			cell.row = row
			row.insert_stub(cell)
		if headers:
			headers = _Row([_Cell(h,datatype='header') for h in headers])
			headers.datatype = 'header'
			headers.table = self
			if stubs:
				headers.insert_stub(_Cell('','stub'))
			rows.insert(0,headers)
			for cell in headers:
				cell.datatype = 'header'
				cell.row = headers
		return rows
	def _data2rows(self, raw_data):
		_Cell = self._Cell
		_Row = self._Row
		rows = []
		for datarow in raw_data:
			dtypes = cycle(self._datatypes)
			newrow = _Row([_Cell(datum) for datum in datarow])
			newrow.table = self  #row knows its SimpleTable
			for cell in newrow:
				cell.datatype = dtypes.next()
				cell.row = newrow  #a cell knows its row
			rows.append(newrow)
		return rows
	def pad(self, s, width, align):
		"""DEPRECATED: just use the pad function"""
		return pad(s, width, align)
	def get_colwidths(self, output_format, **fmt_dict):
		fmt = self.output_formats[output_format].copy()
		fmt.update(fmt_dict)
		ncols = max(len(row) for row in self)
		request = fmt.get('colwidths')
		if request is 0: #assume no extra space desired (e.g, CSV)
			return [0] * ncols
		elif request is None: #assume no extra space desired (e.g, CSV)
			request = [0] * ncols
		elif isinstance(request, int):
			request = [request] * ncols
		elif len(request) < ncols:
			request = [request[i%len(request)] for i in range(ncols)]
		min_widths = []
		for col in zip(*self):
			maxwidth = max(len(c.as_string(output_format,**fmt)) for c in col)
			min_widths.append(maxwidth)
		result = map(max, min_widths, request)
		return result
	def get_cols_aligns(self, output_format, **fmt_dict):
		"""Return string, sequence of column alignments.
		Ensure comformable data_aligns in `fmt_dict`."""
		fmt = self.output_formats[output_format].copy()
		fmt.update(fmt_dict)

		has_stubs = bool(self.stubs)
		dcols = max(len(row) for row in self) - has_stubs  # number of data columns
		cols_aligns = fmt_dict.get('cols_aligns')
		if cols_aligns is None or len(cols_aligns) != dcols + has_stubs:
			if has_stubs:
				stubs_align = fmt_dict.get('stubs_align','l')
				assert len(stubs_align)==1
			else:
				stubs_align = ''
			data_aligns = fmt_dict.get('data_aligns', 'c')
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
		#get rows formatted as strings
		formatted_rows = [ row.as_string('text', **fmt) for row in self ]
		formatted_table_body = '\n'.join(formatted_rows)

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

		begin = '<table class="simpletable">'
		if self.title:
			begin += '<caption>%s</caption>\n'%(self.title,)
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

		begin = r'\begin{tabular}{%s}'%(self.get_cols_aligns('latex', **fmt))
		above = fmt['table_dec_above']
		if above:
			begin += "\n" + above
		end = r'\end{tabular}'
		below = fmt['table_dec_below']
		if below:
			end = below + "\n" + end
		return begin + '\n' + formatted_table_body + "\n" + end
	def extend_right(self, table):
		for row1, row2 in zip(self, table):
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


class Row(list):
	"""A Row is a list of cells;
	a row can belong to a SimpleTable.
	"""
	def __init__(self, cells, datatype='', table=None, celltype=None, **fmt_dict):
		"""
		Parameters
		----------
		table : SimpleTable
		"""
		list.__init__(self, cells)
		self.datatype = datatype # data or header
		self.table = table
		if celltype is None:
			try:
				celltype = table._Cell
			except AttributeError:
				celltype = Cell
		self._Cell = celltype
		self._fmt = fmt_dict
	def insert_stub(self, stub, loc=0):
		_Cell = self._Cell
		if not isinstance(stub, _Cell):
			stub = str(stub)
			stub = _Cell(stub, datatype='stub', row=self)
		self.insert(loc, stub)
	@property
	def data(self):
		return [cell.data for cell in self]
	def as_string(self, output_format='txt', **fmt_dict):
		"""Return string: the formatted row.
		This is the default formatter for rows.
		Override this to get different formatting.
		A row formatter must accept as arguments
		a row (self) and an output format,
		one of ('html', 'txt', 'csv', 'latex').
		"""
		#first get the default formatting
		try:
			fmt = default_fmts[output_format].copy()
		except KeyError:
			raise ValueError('Unknown format: %s' % output_format)
		#second get table specific formatting (if possible)
		try:
			fmt.update(self.table.output_formats[output_format])
		except AttributeError:
			pass
		#finally, add formatting for this cell and this call
		fmt.update(self._fmt)
		fmt.update(fmt_dict)

		#get column widths
		try:
			colwidths = self.table.get_colwidths(output_format, **fmt)
		except AttributeError:
			colwidths = fmt.get('colwidths')
		if colwidths is None:
			colwidths = (0,) * len(self)

		#get column alignments
		try:
			cols_aligns = self.table.get_cols_aligns(output_format, **fmt)
		except AttributeError:
			cols_aligns = fmt.get('cols_aligns')
		if cols_aligns is None:
			cols_aligns = 'c' * len(self)

		colsep = fmt['colsep']
		row_pre = fmt.get('row_pre','')
		row_post = fmt.get('row_post','')
		formatted_cells = []
		for cell, width, align in zip(self, colwidths, cols_aligns):
			content = cell.as_string(output_format=output_format, **fmt)
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

class Cell(object):
	def __init__(self, data='', datatype=0, row=None, **fmt_dict):
		self.data = data
		self.datatype = datatype
		self.row = row
		self._fmt = fmt_dict
	def __str__(self):
		return self.as_string()
	def as_string(self, output_format='txt', **fmt_dict):
		"""Return string.
		This is the default formatter for cells.
		Override this to get different formating.
		A cell formatter must accept as arguments
		a cell (self) and an output format,
		one of ('html', 'txt', 'csv', 'latex').
		It will generally respond to the datatype,
		one of (int, 'header', 'stub').
		"""
		#first get the default formatting
		try:
			fmt = default_fmts[output_format].copy()
		except KeyError:
			raise ValueError('Unknown format: %s' % output_format)
		#then get any table specific formtting
		try:
			fmt.update(self.row.table.output_formats[output_format])
		except AttributeError:
			pass
		#then get any row specific formtting
		try:
			fmt.update(self.row._fmt)
		except AttributeError:
			pass
		#finally add formatting for this instance and call
		fmt.update(self._fmt)
		fmt.update(fmt_dict)

		data = self.data
		datatype = self.datatype
		data_fmts = fmt.get('data_fmts')
		if data_fmts is None:
			#chk allow for deprecated use of data_fmt
			data_fmt = fmt.get('data_fmt')
			if data_fmt is None:
				data_fmt = '%s'
			data_fmts = [data_fmt]
		if isinstance(datatype, int):
			datatype = datatype % len(data_fmts) #constrain to indexes
			result = data_fmts[datatype] % data
		elif datatype == 'header':
			print fmt.get('header_fmt','%s') % data
			result = fmt.get('header_fmt','%s') % data
		elif datatype == 'stub':
			result = fmt.get('stub_fmt','%s') % data
		else:
			raise ValueError('Unknown cell datatype: %s'%datatype)
		return result


		
			

#########  begin: default formats for SimpleTable  ##############
"""
A SimpleTable can be initialized with `datatypes`:
a list of ints that are indexes into `data_fmts`.
These control formatting.
"""
default_csv_fmt = dict(
		data_fmts = ['%s'],
		data_fmt = '%s',  #deprecated; use data_fmts
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
		data_fmts = ['<td>%s</td>'],
		data_fmt = "<td>%s</td>",  #deprecated; use data_fmts
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
		data_fmts = ["%s"],
		data_fmt = "%s",  #deprecated; use data_fmts
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
		data_fmts = ["%s"],
		data_fmt = "%s",  #deprecated; use data_fmts
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



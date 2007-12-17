class SimpleTable:
	'''Produce a simple ASCII or LaTeX table from a 2D array of data.
	`data` is 2D rectangular iterable: lists of lists of text.
	At most one header row, which is length of data[0] (+1 if stubs)
	At most one stubs column, which must have length of data.
	'''
	def __init__(self, data, headers=(), stubs=(), title='', txt_fmt={}, ltx_fmt={}):
		self.data = data
		self.headers = headers
		self.stubs = stubs
		self.title = title
		self.txt_fmt = self.default_txt_fmt()
		self.txt_fmt.update(txt_fmt)
		self.ltx_fmt = self.default_ltx_fmt()
		self.ltx_fmt.update(ltx_fmt)
	def __str__(self):
		return self.as_text()
	def calc_colwidths(self, data):
		return [max(len(d) for d in c) for c in izip(*data)]
	def format_rows(self, data, colwidths, colaligns, colsep, pre='', post=''):
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
		data_fmt = fmt_dict.get('data_fmt','%s')
		return [[(data_fmt%drk).strip() for drk in dr] for dr in self.data] #is the 'strip' wise?
	def format_headers(self, fmt_dict, headers=None):
		header_fmt = fmt_dict.get('header_fmt','%s')
		headers2fmt = headers or self.headers
		return [header_fmt%header for header in headers2fmt]
	def format_stubs(self, fmt_dict, stubs=None):
		stub_fmt = fmt_dict.get('stub_fmt','%s')
		stubs2fmt = stubs or self.stubs
		return [stub_fmt%stub for stub in stubs2fmt]
	def merge_table_parts(self, data, headers, stubs): #avoids copy but too implicit ...
		#insert stubs and headers
		for i in range(len(stubs)):
			data[i].insert(0,stubs[i])
		if headers:
			data.insert(0,headers)
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
	def as_text(self, **fmt):  #allow changing fmt here?
		fmt_dict = self.txt_fmt.copy()
		fmt_dict.update(fmt)
		#data_fmt="%s", header_fmt="%s", stub_fmt="%s", colsep=" ", colaligns='', colwidths=(), header_dec=''):
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



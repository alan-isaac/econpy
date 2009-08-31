"""A collection input-output utilities.
These are intended a lightweight supplements to those in SciPy_,
not to provide a full set of service.

:author: Alan G. Isaac, except where otherwise specified.
:copyright: 2005 Alan G. Isaac, except where otherwise specified.
:license: `MIT license`_
:see: pytrix.py
:see: pyGAUSS.py
:see: tseries.py

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
.. _`SciPy`: http://www.scipy.org/
"""
__docformat__ = "restructuredtext en"

import csv
import types
import urllib
import datetime
import re, glob  #just for grep
import logging
logging.getLogger().setLevel(logging.WARN) #sets root logger level
#see http://www.python.org/doc/2.3.5/lib/node304.html to log to a file
#(after Python 2.4 can use basicConfig)

# for other IO options see:
#	pylab.load()
#	scipy.io.read_array()

import matplotlib.dates
from matplotlib.dates import date2num, MONTHLY, YEARLY
try: from scipy import nan
except ImportError: nan=1e300*1e300-1e300*1e300
#see http://www.cs.ucla.edu/classes/winter04/cs131/hw/hw4.html for problems w this ^

def fetch(file_name,file_type='databank'):
	if file_type=='databank':
		fp = open(file_name,'r')
		data,smpl,label = read_db(fp) #need to change comments to label
		return data, smpl, label
	else:
		raise ValueError, "Unsupported file type"


def read_odb(fp):
	line = fp.readline().strip()
	if line.startswith('"'):
		fp.seek(0)
		data,smpl,comments = read_db(fp)
		dates = None  #maybe ...
	#elif line[0].isalpha(): pass #read FRED
	else:
		msg = "File does not appear to be a databank."
		raise ValueError(msg)
	return data,smpl,comments,dates


def next_stripped_notempty(fp):  #ignore blank lines
	while True:
		line = fp.readline().strip()
		if line: break
	return line

def read_db(fp):
	"""Return tuple: data, smpl, comments.
	Reads an open-database file.
	"""
	#fp may be a string instead of a file handle
	if isinstance(fp,str):
		fp = file(fp,'r')
	assert isinstance(fp,file), "%s not recognized as a file"%(fp)
	#empty dict to hold comments
	comments = dict()
	ckey = ''
	cval = ''
	#empty list to hold data
	data = []
	#get the first non-empty line
	line = next_stripped_notempty(fp)
	while line.startswith('"'):   #it's a comment
		if line.endswith('"'):
			line=line[:-1].rstrip()
		if line.startswith('"c'):   #it's a new comment
			line=line[2:].lstrip() #strip comment marker and white space
			try:
				idx = line.index(':') #check new comment for label
				ckey = line[:idx].rstrip()
				cval = line[idx+1:].strip()
			except:
				ckey = 'Remarks'
				cval = line
		else: #comment continuation line
			cval = line
		if ckey in comments:
			comments[ckey] += '\n'+cval
		else:
			comments[ckey] = cval
		line = next_stripped_notempty(fp)
	if line.startswith('-'):  #fixed frequency series
		freq = -int(line)
		line = next_stripped_notempty(fp)
	else: # undated series
		freq = 'u'
	start = line
	end = next_stripped_notempty(fp)
	if freq in [1,4,12]:
		start = datestr2date(start,freq)
		end = datestr2date(end,freq)
	elif freq == 'u':
		start, end = int(start), int(end)
	else:
		raise ValueError("Unrecognized frequency.")
	smpl = Sample(start, end, freq)
	for line in fp.readlines():  #TODO: work with multifile
		if line.startswith('"'):
			logging.warn("comment in data discarded")
			continue #ignore comments in data
		else:
			try:
				data.append(float(line))
			except ValueError:
				logging.warn("corrupt data discarded:"+line)
	#logging.info(str(comments))
	return data, smpl, comments

def write_db(file_name, data, smpl=None, comments=None, freq=None, start=None, end=None):
	"""Return None. Write data to an opendatabank file.
	Priority to smpl if provided.

	Although other comments are harmless,
	many readers only recognize three labels:
	"Last updated", "Display Name", and "Modified".
	The last of these is automatically set to the
	current date by this writer.

	:see: http://www.american.edu/econ/pytrix/opendatabank.txt
	"""
	logging.debug("\n\tEntering write_db...")
	if smpl is None:
		try:
			smpl = Sample(start, end, freq)
		except:
			logging.debug("No sample provided: treating as undated data.")
			smpl = (1,len(data))
	if isinstance(smpl, tuple):
		freq = None
		start = smpl[0]
		end = smpl[1]
		freq_smpl = str(start)+"\n"+str(end)+"\n"
		data_type = ' undated '
	elif isinstance(smpl, Sample):
		freq = smpl.freq
		start = date2dbdate(smpl.start, freq)
		end = date2dbdate(smpl.end, freq)
		freq_smpl = str(-freq)+"\n"+str(start)+"\n"+str(end)+"\n"
		data_type = ' dated '
	else:
		raise TypeError('Unknown sample type.')
	logging.debug("Writing data with"+data_type+"sample:\n%s"%(freq_smpl,))
	try:
		fp = open(file_name,'w')
	except:
		msg = """Cannot write to %s;
		invalid file or directory name?"""%(file_name)
		logging.error(msg)
		raise IOError
	comments['Last updated'] = str(datetime.date.today())
	for key in comments:
		fp.write('"c'+key+': '+comments[key]+'\n')
	fp.write(freq_smpl)
	for datum in data:
		fp.write(str(datum)+'\n')
	fp.close()

def parse_date(dt, freq=None):
	"""Return: datetime.date,
	as implied by `dt` and `freq`.
	"""
	logging.debug("\n\tEntering parse_date...")
	if isinstance(dt, datetime.date):
		new_dt = dt   #is a copy wanted?
	elif isinstance(dt, list):
		new_dt = datetime.date(dt[0],dt[1],1)
	elif isinstance(dt, str):
		new_dt = datestr2date(dt, freq)
	else:
		raise ValueError('parse_date: Unsupported date type.')
	return new_dt

def date2bop(dt, freq):
	"""Returns beginning of the period in which dt falls, based on freq.

	:param dt: datetime.date object
	:param freq: int, representaton of frequency
	"""
	logging.debug("\n\tEntering date2bop...")
	freq = freq2num(freq)
	if isinstance(dt, str):
		dt = datestr2date(dt, freq)
	if not isinstance(dt, datetime.date):
		raise ValueError('`date2bop` requires datetime.date input.')
	if freq==1:
		new_dt = datetime.date(dt.year,1,1)
	elif freq==4:
		new_dt = datetime.date(dt.year,1+((dt.month-1)//3)*3,1)
	elif freq==12:
		new_dt = datetime.date(dt.year,dt.month,1)
	else:
		raise ValueError('Unsupported frequency: %s'%(freq))
	if new_dt != dt:
		logging.info("Date changed to start of period for frequency of %s times per year."%(freq))
	return new_dt
	
def parse_datestr(datestr):
	"""Return dict containing year, quarter, month, day, freq.

	Allowable input formats:

	- Annual: yyyy
	- Quarterly: yyyy.q, yyyyQq,
	- Monthly: yyyy.mm, yyyyMmm, yyyy-mm, Mmm yyyy

	:param datestr: string, representation of a date
	:param freq: int, representaton of frequency

	:note: Also handles some hyphenated dates: e.g., 2005-10-01.
	"""
	datestr = datestr.strip()
	monthly = re.compile('^\d\d\d\d[Mm.-]\d\d$')
	monthly_ifs = re.compile('^[Mm](\d{1,2})\s+(\d\d\d\d)$')
	quarterly = re.compile('^\d\d\d\d[Qq.-]\d$')
	annual = re.compile('^\d\d\d\d$')
	result = dict()
	if not isinstance(datestr, str):
		raise ValueError("parse_datestr only converts strings.")
	if monthly.match(datestr):
		year, month = map(int, re.split('[Mm.-]', datestr) )
		result['month'] = month
		result['freq'] = 12
	elif monthly_ifs.match(datestr):
		month, year = map( int, monthly_ifs.match(datestr).groups() )
		result['month'] = month
		result['freq'] = 12
	elif quarterly.match(datestr):
		year, quarter = map(int, re.split('[Qq.-]', datestr))
		result['quarter'] = quarter
		result['freq'] = 4
	elif annual.match(datestr):
		year = int(datestr)
		result['freq'] = 1
	else:
		raise ValueError('Unrecognized date format: '+datestr)
	result['year'] = year
	return result

def datestr2date(datestr, freq=None, month4yearly=1, month4quarterly=1, day=15):
	"""Return datetime.date instance,
	representing datestr.

	Allowable input formats: see `parse_datestr`

	:param datestr: string, representation of a date
	:param freq: int, representaton of frequency
	"""
	parsed = parse_datestr(datestr)
	implied_freq = parsed['freq']
	if freq and freq != implied_freq:
		raise ValueError('`freq` must match date format')
	year = parsed['year']
	if implied_freq == 12:
		month = parsed['month']
	elif implied_freq == 4:
		quarter = parsed['quarter']
		month = (quarter-1)*3 + month4quarterly
	elif implied_freq == 1:
		#set month = 1 for consistency and nice graphs?
		month = month4yearly
	else:
		raise ValueError('Unrecognized frequency: %s'%implied_freq)
	return datetime.date(year,month,day)

def date2dbdate(dtdate,freq):
	"""Convert datetime.date to opendatabank format.
	
	:see: http://www.american.edu/econ/pytrix/opendatabank.txt
	"""
	freq = freq2num(freq)
	dtstr = str(dtdate.year)
	if freq==12:
		dtstr = dtstr + '.' + str(date.month)
	if freq==4:
		dtstr = dtstr + '.' + str((2+dtdate.month)//3)
	logging.info("dtstr: "+dtstr)
	return dtstr


class ReadFRED(object):
	"""Read data from `FRED2`_ files.
	Example use::

		fredbase = "http://research.stlouisfed.org/fred2/data/"
		currency = ReadFRED(fredbase+'CURRENCY.txt')
		print currency.data

	:requires: logging module (in standard library)
	:note: logs errors to root log

	.. _`FRED2`: http://research.stlouisfed.org/fred2/
	"""
	#convenience declarations
	header = None
	comments = None
	dates = None
	data = None
	_sample = None
	def __init__(self, source):
		#source is a URL, a path, or a file handle
		self.source = source
		#parse the source
		fh = self.get_fh()
		self.parse_source(fh)
		self.parse_header()
	def get_fh(self):
		source = self.source
		if isinstance(source,str):
			if source.startswith('http'):
				try: fh = urllib.urlopen(source)
				except IOError:
					logging.error("Cannot open URL.")
					return
			else:
				try: fh = open(source,'r')
				except IOError:
					logging.error("Cannot open file %s."%(source))
					return
		else:
			fh = filehandle
		return fh
	def parse_source(self, fh):
		"""Parse source into header, dates, and data.
		"""
		header_lines = []
		dates = []
		data = []
		header = True
		for line in fh:
			if header:
				if line.startswith('DATE'):
					header = False
					self.header = ''.join(header_lines)
					continue #do not process this line
				else:
					header_lines.append(line)
			else: #no longer header -> process the date&datum lines
				line = line.strip().split()
				try:
					thedate=[int(xi) for xi in line[0].split('-')]  #e.g. 2005-09-11 -> [2005,09,11]
					dates.append(datetime.date(*thedate))
				except:
					if not line:
						logging.info("Empty line skipped.")
					else:
						logging.warn("Date field not a date; line skipped. Contents:\n%s"%(line))
					continue
				try:
					data.append(float(line[1]))
				except: 
					logging.warn("Missing value set to nan.")
					data.append(nan)
			self.dates = dates
			self.data = data
	def parse_header(self):
		"""Parse header into individual comments.
		Skips blank lines.
		"""
		keyval = ['','']
		comments = dict()
		for line in self.header.split("\n"):
			if line and line[0].isalpha(): #shd start a new comment
				try:
					idx = line.index(':')
					if keyval[0]:  #flush comment in progress
						comments[keyval[0]]=keyval[1]
					keyval = [ s.strip() for s in line.split(':',1) ]
				except: #must be a badly formatted comment continuation
					if keyval[0]:
						keyval[1] = keyval[1] + ' ' + line.strip()
					else:
						logging.warn("Orphan comment line discarded.")
			elif line: #continue an old comment
				keyval[1] += ' ' + line.strip()
		self.comments = comments
	def write_db(self, file_name):
		smpl = self.get_sample()
		write_db(file_name,self.data,smpl=smpl,comments={},freq=None,start=None,end=None)
	@property
	def sample(self):
		if self._sample is None:
			start = self.dates[0]
			end = self.dates[-1]
			freq = self.comments['Frequency']
			self._sample = Sample(start, end, freq=freq, dates=None, condition=None)
		return self._sample
		

def read_ifs_csv(filename, commentlines=10):
	"""Return tuple: data (by obs), dates, comments.
	Very basic reader for IFS CSV files.
	Only reads sequential valid observations.
	"""
	reader = csv.reader(open(filename))
	#get comments
	commentdict = dict()
	for _ in range(commentlines):
		row = reader.next()
		key = row[0]
		commentdict[key] = row[1:]
	#get data and dates
	data = list()
	dates = list()
	startdata = False
	for row in reader:
		if "n.a." in row:
			if not startdata: continue
			else: break
		startdata = True
		date, vals = row[0], map(float,row[1:])
		dates.append( datestr2date(date) )
		data.append(vals)
	#make comments by series
	nseries = len(data[0])
	comments = [dict() for _ in range(nseries)]
	for key in commentdict:
		if len(commentdict[key]) == nseries:
			for i in range(nseries):
				comments[i][key] = commentdict[key][i]
		else:
			logging.info("Missing comments?"+commendict[key])
	return data, dates, comments

def read_fred(source):
	"""Return data, dates, comments.
	Read data from `FRED2`_ files.
	Example use::

		fredbase = "http://research.stlouisfed.org/fred2/data/"
		data, dates, comments = read_fred(fredbase+'CURRENCY.txt')

	:note: deprecated in favor of ReadFRED class

	.. _`FRED2`: http://research.stlouisfed.org/fred2/
	"""
	series = ReadFRED(source)
	data = series.data
	dates = series.dates
	comments = series.comments
	return data, dates, comments

 
def read_odbmulti(fname):
	"""Read data from opendatabank multi files.

	:see: http://www.american.edu/econ/pytrix/opendatabank.txt
	"""
	import multifile
	fp = open(fname,'r')
	mfp = multifile.MultiFile(fp)
	mfp.push('series-boundary')
	comments = mfp.read()
	#print comments
	while mfp.next():
		try: data,smpl,comments = read_db(mfp)
		except multifile.Error:
			break
			fp.close()
		print data
	fp.close()

class Sample:
	"""A 'sample' (i.e., date range) class for tseries.series objects.

	:note: each observation is dated to first day of its period
	"""
	def __init__(self, start, end, freq=None, dates=None, condition=None):
		self.freq = freq2num(freq)
		if freq:
			#get *beginning* of period in which `start` falls
			self.start = date2bop(start, freq)
			#get *beginning* of period in which `end` falls
			self.end = date2bop(end, freq)
			self._dates = dates
			self.condition = condition
		else:
			self.start, self.end = int(start), int(end)
			self._dates = dates or list(range(start,end+1))
			self.condition = condition
		logging.info("Class Sample: "+str(self))
		logging.info("Class Sample: freq = "+str(freq))
	def __str__(self):
		return str(self.start)+' to '+str(self.end)
	#define equality comparison
	def __eq__(self, smpl):
		return (self.start == smpl.start)and(self.end==smpl.end)and(self.freq==smpl.freq)
	def __ne__(self, smpl):
		return (self.start != smpl.start)or(self.end!=smpl.end)or(self.freq!=smpl.freq)
	def __len__(self):
		return len(self.dates)
	def copy(self):
		return Sample(self.start,self.end,self.freq,self.condition)
	def set_start(self,dt):
		self.start = date2bop(dt,freq)
	def set_end(self,dt):
		self.end = date2bop(dt,freq)  #chk bop?
	def get_rrule(self):
		"""Convert sample `smpl` dates to rrule.  """
		if self.freq == 12:
			return matplotlib.dates.rrule(MONTHLY,dtstart=self.start,until=self.end)
		elif self.freq == 4:
			return matplotlib.dates.rrule(MONTHLY,interval=3,dtstart=self.start,until=self.end)
		elif self.freq == 1:
			return matplotlib.dates.rrule(YEARLY,dtstart=self.start,until=self.end)
		else:
			raise ValueError('class Sample: unknown frequency')
	def get_date_index(self,dt):
		assert isinstance(dt,datetime.date), "class Sample: Requires datetime.date instance as argument."
		if self.dates is None:
			self.set_dates()
		assert self.dates[0]<=dt<=self.dates[-1], "class Sample: %s outside sample."%(dt)
		#logging.info("Sample: dates = "+str(self.dates))
		logging.debug("Class Sample: seeking index for dt = "+str(dt))
		try:
			date_idx = self.dates.index(dt)
		except ValueError:
			new_dt = date2bop(dt,self.freq)
			logging.warning("Sample: "+str(dt)+ "within sample but not in dates. Seeking "+str(new_dt)+" instead.")
		return self.dates.index(dt)
	def intersect(self,smpl):
		assert (self.freq == smpl.freq), "Cannot intersect samples of different frequency."
		start = max(self.start,smpl.start)
		end = min(self.end,smpl.end)
		if start > end:
			logging.warning("class Sample: empty intersection.")
			return None
		else:
			return Sample(start,end,self.freq)
	def get_dates(self):
		logging.warn('Deprecated method get_dates; use the dates property')
		return self.dates
	def set_dates(self,dates=None):  #TODO: use for date checking of supplied dates
		if dates is None:
			self._dates =  [xi.date() for xi in self.get_rrule()]
	@property
	def dates(self):
		"""Return list of datetime.date objects corresponding to sample."""
		if self._dates is None:
			self.set_dates()
		return self._dates


def freq2num(freq):
	if freq in (1,4,12,52) or freq is None:
		result = freq
	elif isinstance(freq, str):
		key = freq[0].upper()
		try:
			result = dict(A=1,Q=4,M=12,W=52,U=None)[key]
		except KeyError:
			raise ValueError('Unsupported frequency: %s'%(freq))
	return result

def col2list(fname='stdin',colnum=1,commentchar='#'):
	"""Read vector from stdin (keyboard) or file.  
	Read 1 number per line from stdin or from 'file' if specified.
	Lines beginning with a hash mark '#' are considered comment-
	lines and are skipped.

	:Parameters:
		`fname`: string
			optional filename
		`colnum`: integer
			column number for vector
		`commentchar`: string
			comment-line marker
	:rtype: list
	:note: White space is stripped.
		Blank lines are ignored.
	:requires: import sys
	:see: `cols2lists`
	:see: getv http://www.phys.uu.nl/~haque/computing/WPark_recipes_in_python.html
	:author: Alan G. Isaac
	:since: 2005-08-19
	"""
	if fname == 'stdin':
		fp = sys.stdin
	else:
		fp = open(fname,'r')
	return [float(a.split()[colnum-1])
	        for a in fp
	        if (a.strip() and not a[0].startswith(commentchar))]


def cols2tuples(fname='stdin', colnum=(1,2), commentchar='#'):
	"""Read vectors from stdin or file.  
	Vectors are stored as columns.
	Read len(colnum) numbers per line.
	Default is 2 numbers, from first two columns.
	Read from stdin or from 'file' if specified.
	Lines beginning with a hash mark '#'
	are considered comment lines and are skipped.

	:Parameters:
		`fname` : string
			optional filename
		`colnum` : tuple
			column numbers for vectors
		`commentchar` : string
			comment-line marker
	:rtype: list
	:return: list of tuples,
		where each tuple contains a vector
	:note: White space is stripped.
		Blank lines are ignored.
	:requires: import sys
	:see: `col2list`
	:see: getv2 http://www.phys.uu.nl/~haque/computing/WPark_recipes_in_python.html
	:author: Alan G. Isaac
	:since: 2005-08-19
	"""
	x = []
	if fname == 'stdin':
		fp = sys.stdin
	else:
		fp = open(fname,'r')
	for a in fp:
		#skip blank and commented lines
		if (a and not a.startswith(commentchar)):
			a=a.split()
			x.append([float(a[cn-1]) for cn in colnum])
	return zip(*x)


def printv(x, outfile='', sep='\n'):
	"""Print vector to stdout or file. 
	Default separator is new line
	-> write 1 number per line.
	Write to stdout or 'outfile' if specified.

	:param `x`: list of numbers
	"""
	import sys
	out = sep.join(str(xi) for xi in x)
	if not outfile:
		sys.stdout.write(out)
	else:
		open(outfile, 'w').write(out)











def readcol(fname,comments='%',columns=None,delimiter=None,dep=0,arraytype='list'):
	"""Load ASCII data from fname into an array and return the array.

	The data must be regular, same number of values in every row 
	fname can be a filename or a file handle.

	Input:

	- Fname : the name of the file to read

	Optionnal input:

	- comments : a string to indicate the charactor to delimit the domments.
the default is the matlab character '%'.

	- columns : list or tuple ho contains the columns to use.

	- delimiter : a string to delimit the columns

	- dep : an integer to indicate from which line you want to begin

		   to use the file (useful to avoid the descriptions lines)

	- arraytype : a string to indicate which kind of array you want to 
				have: numeric array (numeric) or character array 
				(numstring) or list (list). By default it's the list mode used 

				matfile data is not currently supported, but see
				Nigel Wade's matfile ftp://ion.le.ac.uk/matfile/matfile.tar.gz

	Example usage::

		x,y = transpose(readcol('test.dat'))  # data in two columns
		X = readcol('test.dat')    # a matrix of data
		x = readcol('test.dat')    # a single column of data
		x = readcol('test.dat,'#') # the character use like a comment delimiter is '#'

	:author: Hu Mufr
	:comment: initial function from pylab, improve by myself for my need 
	"""
	from numarray import array,transpose

	fh = file(fname)

	X = []
	numCols = None
	nline = 0
	if columns is None:
		for line in fh:
			nline += 1
			if dep is not None and nline <= dep: continue
			line = line[:line.find(comments)].strip()
			if not len(line): continue
			if arraytype=='numeric':
				row = [float(val) for val in line.split(delimiter)]
			else:
				row = [val.strip() for val in line.split(delimiter)]
			thisLen = len(row)
			if numCols is not None and thisLen != numCols:
				raise ValueError('All rows must have the same number of columns')
			X.append(row)
	else:
		for line in fh:
			nline +=1
			if dep is not None and nline <= dep: continue
			line = line[:line.find(comments)].strip()
			if not len(line): continue
			row = line.split(delimiter)
			if arraytype=='numeric':
				row = [float(row[i-1]) for i in columns]
			elif arraytype=='numstring':
				row = [row[i-1].strip() for i in columns]
			else:
				row = [row[i-1].strip() for i in columns]
		thisLen = len(row)
	
		if numCols is not None and thisLen != numCols:
			raise ValueError('All rows must have the same number of columns')
		X.append(row)

	if arraytype=='numeric':
		X = array(X)
		r,c = X.shape
		if r==1 or c==1:
			X.shape = max([r,c]),
	elif arraytype == 'numstring':
		import numarray.strings			# pb si numeric+pylab
		X = numarray.strings.array(X)
		r,c = X.shape
		if r==1 or c==1:
			X.shape = max([r,c]),
		
	return X



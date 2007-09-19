'''A collection input-output utilities.
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
'''
__docformat__ = "restructuredtext en"

import types
import urllib
import datetime
import matplotlib.dates
from matplotlib.dates import date2num, MONTHLY, YEARLY
import re, glob  #just for grep
try: from scipy import nan
except ImportError: nan=1e300*1e300-1e300*1e300
#see http://www.cs.ucla.edu/classes/winter04/cs131/hw/hw4.html for problems w this ^
import logging
logging.getLogger().setLevel(logging.DEBUG) #sets root logger level
#see http://www.python.org/doc/2.3.5/lib/node304.html to log to a file
#(after Python 2.4 can use basicConfig)
# for other IO options see:
#	pylab.load()
#	scipy.io.read_array()

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
	elif line[0].isalpha():
		pass #read fred
	return data,smpl,comments,dates


def next_stripped_notempty(fp):  #ignore blank lines
	while True:
		line = fp.readline().strip()
		if line: break
	return line

def read_db(fp):
	if isinstance(fp,str):
		fp = file(fp,'r')
	assert isinstance(fp,file), "%s not recognized as a file"%(fp)
	comments = dict()
	ckey = ''
	cval = ''
	data = []
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
		if comments.has_key(ckey):
			cval = comments[ckey]+'\n'+cval
		comments.update({ckey:cval})
		line = next_stripped_notempty(fp)
	# need to change next to allow undated series
	try: assert '-'==line[0]  #freq specifier starts w '-'
	except IndexError:
		print fp.tell()
		exit
	freq = -int(line)
	assert freq in [1,4,12]
	start, freq_implied = datestring2date(next_stripped_notempty(fp),freq)
	end, freq_implied = datestring2date(next_stripped_notempty(fp),freq)
	smpl = Sample(start,end,freq)
	for line in fp.readlines():  #needs to work with multifile
		if line.startswith('"c'):
			logging.warn("comment in data discarded")
			continue #ignore comments in data
		else:
			try:
				data.append(float(line))
			except ValueError:
				logging.warn("corrupt data discarded")
	#logging.info(str(comments))
	return data,smpl,comments

def write_db(file_name,data,smpl=None,comments={},freq=None,start=None,end=None):
	'''Write data to an opendatabank file.
	Priority to smpl if provided.

	:see: http://www.american.edu/econ/pytrix/opendatabank.txt
	'''
	logging.debug("\n\tEntering write_db...")
	if smpl is None:
		try:
			smpl = Sample(start,end,freq)
		except:
			logging.debug("No sample provided: treating as undated data.")
			smpl = (1,len(data))
	if isinstance(smpl,tuple):
		freq = None
		start = smpl[0]
		end = smpl[1]
		freq_smpl = str(start)+"\n"+str(end)+"\n"
		data_type = ' undated '
	elif isinstance(smpl,Sample):
		freq = smpl.freq
		start = date2dbdate(smpl.start,freq)
		end = date2dbdate(smpl.end,freq)
		freq_smpl = str(-freq)+"\n"+str(start)+"\n"+str(end)+"\n"
		data_type = ' dated '
	else:
		raise TypeError('Unknown sample type.')
	logging.debug("Writing data with"+data_type+"sample:\n%s"%(freq_smpl,))
	try:
		fp = file(file_name,'w')
	except:
		logging.error("Cannot write to %s; invalid file name?"%(file_name))
		raise IOError
	comments['Last updated'] = str(datetime.date.today())
	for key in comments:
		fp.write('"c'+key+': '+comments[key]+'\n')
	fp.write(freq_smpl)
	for datum in data:
		fp.write(str(datum)+'\n')
	fp.close()

def parse_date(dt,freq=None):
	'''Determine date and return beginning-of-period equivalent,
	as implied by `freq`.
	'''
	logging.debug("\n\tEntering parse_date...")
	if isinstance(dt,datetime.date):
		new_dt = dt
	elif isinstance(dt,list):
		new_dt = datetime.date(dt[0],dt[1],1)
	elif isinstance(dt,str):
		new_dt, freq_implied = datestring2date(dt,freq)
		if freq is None:
			freq = freq_implied
		else:
			assert (freq == freq_implied), "Stated frequency does not match format"
	else:
		raise ValueError('parse_date: Unsupported date type.')
	return date2periodstart(new_dt,freq)

def date2periodstart(dt,freq=None):
	'''Returns beginning of the period in which dt falls, based on freq.

	:param dt: datetime.date object
	:param freq: int, representaton of frequency
	'''
	logging.debug("\n\tEntering date2periodstart...")
	assert isinstance(dt,datetime.date), "Requires datetime.date input."
	freq = freq2num(freq)
	if freq is None: new_dt = dt
	elif freq==1: new_dt = datetime.date(dt.year,1,1)
	elif freq==4: new_dt = datetime.date(dt.year,1+((dt.month-1)//3)*3,1)
	elif freq==12: new_dt = datetime.date(dt.year,dt.month,1)
	else: raise ValueError('Unsupported frequency: %s'%(freq))
	if new_dt != dt:
		logging.warning("Date changed to start of period for frequency of %s times per year."%(freq))
	return new_dt
	
def datestring2date(date_str,freq=None):
	'''Return yyyy or yyyy.q or yyyy.mm as datetime.date object.
	Also return implied `freq`.

	:param date_str: string, representation of a date
	:param freq: int, representaton of frequency

	:note: Also handles some hyphenated dates: e.g., 2005-10-01.
	'''
	assert isinstance(date_str,str), "datestring2date only converts strings."
	date_str = date_str.replace(':','.').replace('-','.')
	date_parts = date_str.split('.')
	logging.debug('date_parts: '+str(date_parts))
	year = int(date_parts[0])
	if len(date_parts) == 1:   #implies annual data
		if freq:
			assert freq == 1, "frequency %s does not match format"%(freq)
		else:
			freq = 1
		month = 1        #set month = 1 for consistency and nice graphs
	if len(date_parts) >= 2:
		if len(date_parts[1]) == 1:  #implies quarterly data
			if freq:
				assert freq==4, "frequency must match format"
			else:
				freq = 4
			month = int(date_parts[1])*3-2  #better to subtract 2 for quarterly graphs??
		else:
			month = int(date_parts[1])
	return datetime.date(year,month,1),freq

def date2dbdate(dtdate,freq):
	'''Convert datetime.date to opendatabank format.
	
	:see: http://www.american.edu/econ/pytrix/opendatabank.txt
	'''
	freq = freq2num(freq)
	dtstr = str(dtdate.year)
	if freq==12:
		dtstr = dtstr + '.' + str(date.month)
	if freq==4:
		dtstr = dtstr + '.' + str((2+dtdate.month)//3)
	logging.info("dtstr: "+dtstr)
	return dtstr


class ReadFred(object):
	'''Read data from `Fred2`_ files.
	Example use::

		fredbase = "http://research.stlouisfed.org/fred2/data/"
		currency = ReadFred(fredbase+'CURRENCY.txt')
		print currency.data

	:requires: logging module (in standard library)
	:note: logs errors to root log

	.. _`FRED2`: http://research.stlouisfed.org/fred2/
	'''
	def __init__(self, source):
		#source is a URL, a path, or a file handle
		self.source = source
		#convenience declarations
		self.header = None
		self.comments = None
		self.dates = None
		self.data = None
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
		'''Parse source into header, dates, and data.
		'''
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
		'''Parse header into individual comments.
		Skips blank lines.
		'''
		keyval = ['','']
		comments = {}
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
	def get_sample(self):
		start = self.dates[0]
		end = self.dates[-1]
		freq = self.comments['Frequency']
		sample = Sample(start,end,freq=freq,dates=None,condition=None)
		return sample
	def write_db(self, file_name):
		smpl = self.get_sample()
		write_db(file_name,self.data,smpl=smpl,comments={},freq=None,start=None,end=None)
		

def read_fred(source):
	'''Return data, dates, comments.
	Read data from `Fred2`_ files.
	Example use::

		fredbase = "http://research.stlouisfed.org/fred2/data/"
		data, dates, comments = read_fred(fredbase+'CURRENCY.txt')

	:note: deprecated in favor of ReadFred class

	.. _`FRED2`: http://research.stlouisfed.org/fred2/
	'''
	series = ReadFred(source)
	data = series.data
	dates = sereis.dates
	comments = series.comments
	return data, dates, comments

 
def read_odbmulti(fname):
	'''Read data from opendatabank multi files.

	:see: http://www.american.edu/econ/pytrix/opendatabank.txt
	'''
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
	'''A 'sample' (i.e., date range) class for tseries.series objects.

	:note: each observation is dated to first day of its period
	'''
	def __init__(self,start,end,freq=None,dates=None,condition=None):
		self.start = parse_date(start,freq) #gets *beginning* of period in which `start` falls
		self.end = parse_date(end,freq) #gets *beginning* of period in which `end` falls
		logging.info("Class Sample: "+str(self))
		logging.info("Class Sample: freq = "+str(freq))
		self.freq = freq2num(freq)
		self.dates = dates
		self.condition = condition
	def __str__(self):
		return str(self.start)+' to '+str(self.end)
	#define equality comparison
	def __eq__(self,smpl):
		return (self.start == smpl.start)and(self.end==smpl.end)and(self.freq==smpl.freq)
	def __ne__(self,smpl):
		return (self.start != smpl.start)or(self.end!=smpl.end)or(self.freq!=smpl.freq)
	def __len__(self):
		return len(self.get_dates())
	def copy(self):
		return Sample(self.start,self.end,self.freq,self.condition)
	def set_start(self,dt):
		self.start = parse_date(dt,freq)
	def set_end(self,dt):
		self.end = parse_date(dt,freq)
	def get_rrule(self):
		'''Convert sample `smpl` dates to rrule.  '''
		if self.freq == 12:
			return matplotlib.dates.rrule(MONTHLY,dtstart=self.start,until=self.end)
		elif self.freq == 4:
			return matplotlib.dates.rrule(MONTHLY,interval=3,dtstart=self.start,until=self.end)
		elif self.freq == 1:
			return matplotlib.dates.rrule(YEARLY,dtstart=self.start,until=self.end)
		else:
			raise ValueError('class Sample: unknown frequency')
	def set_dates(self,dates=None):  #TODO: use for date checking of supplied dates
		if dates is None:
			self.dates =  [xi.date() for xi in self.get_rrule()]
	def get_dates(self):
		'''Return list of datetime.date objects corresponding to sample.'''
		if self.dates is None:
			self.set_dates()
		return self.dates
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
			new_dt = date2periodstart(dt,self.freq)
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


def freq2num(freq):
	if freq in (1,4,12,52) or freq is None:
		return freq
	elif isinstance(freq,str):
		if freq.upper().startswith('A'): return 1
		if freq.upper().startswith('Q'): return 4
		if freq.upper().startswith('M'): return 12
		if freq.upper().startswith('W'): return 52
	else:
		raise ValueError('Unsupported frequency: %s'%(freq))

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



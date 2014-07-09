'''Provide some iterative process related classes.

:date: 2007-07-12
:since: 2007-06-25
:copyright: Alan G. Isaac, except where another author is specified.
:license: `MIT license`_

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
'''
from __future__ import absolute_import
from __future__ import division

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'
__lastmodified__ = '2007-07-04'



class IterativeProcess(object):
	'''General description of iterative process.

	Needs a criterion.
	The stop criterion must be a function or callable class,
	which takes as an argument an IterativeProcess.
	'''
	def __init__(self, criterion=None, reportfreq=0): #TODO
		'''Return: None.
		Usually overrriden by user.
		Initialize the iterator.
		Must set a criterion.
		`reportfreq` is frequency of printed output
		'''
		self.set_criterion(criterion)
		self.iteration = 0
		self.history = []
		self.reportfreq = reportfreq
	def __iter__(self):
		return self
	def set_criterion(self, criterion):
		if criterion is None:
			self.criterion = self.default_criterion()
		else:
			self.criterion = criterion
	def run(self):
		criterion = self.criterion
		reportfreq = self.reportfreq #printed output
		#iterate while criterion not satisfied
		for badvalue in self:
			self.value = badvalue
			self.record_history(value=badvalue)
			if (reportfreq and not self.iteration%reportfreq):
				print self.report()
	def report(self):
		'''Return: string.
		Comment: can condition on whether optimized.'''
		value = getattr(self, 'value', None)
		optimized = getattr(self.criterion, 'optimized', "Undefined")
		iterations = self.iteration
		report = '''
		Value:                %s
		Optimized:            %s
		Number of iterations: %d
		'''%(value, optimized, iterations)
		return report
	#users usually override the following methods
	def default_criterion(self):
		return lambda ip, value, iteration: ip.iteration >= 100
	def record_history(self, value=None):
		'''Should return: None.
		Must be able to handle initial state.
		'''
		if value is not None:
			self.history.append(value)
	def finalize(self, value=None):
		'''Return: None.
		Should set self.value to final value!
		'''
		self.record_history(value=value)
		self.value = value
		#if printing reports, print a final report
		if self.reportfreq:
			print self.report()
	def next(self):
		value = self.iterate()
		self.iteration += 1
		if self.criterion(self, value=value, iteration=self.iteration):
			self.finalize(value=value)
			raise StopIteration
		return value
	#users must implement the following methods
	def iterate(self):
		'''Return value or None.
		Do one iteration.
		Used by `next`.
		'''
		raise NotImplementedError
	def get_testinfo(self, value=None, iteration=0):
		'''Should return: values
		as needed by `criterion`.
		'''
		raise NotImplementedError



#TODO: make this a subclass of IterativeProcess
class Picard:
	'''Compute fixed point, function iteration sequence,
	and number of iterations (Picard function iteration).

	:author:    Alan G. Isaac
	:since:     2006-01-08
	:contact:   mailto:aisaac AT american.edu
	'''
	def __init__(self,fn,p,itermax=100,toltest=None,tol=1e-6):
		if toltest is None:
			self.toltest = self.default_scalar_toltest
		else:
			self.toltest = toltest
		self.tol = tol
		(self.fp,
		self.pseq,
		self.itertotal) = self.picard(fn,p,itermax,self.toltest)
		self.warning = None 
		if self.fp is None:
			if self.itertotal==itermax:
				self.warning = "Convergence failed:\
				                maximum iteration reached."
			else:
				self.warning = "Convergence failed:\
				                reason unknown."
	@staticmethod
	def default_scalar_toltest(p1,p2,tol=1e-6):
		return abs(p2-p1)<tol
	# Picard algorithm (function iteration)
	@staticmethod
	def picard(fn,p,itermax=100,toltest=default_scalar_toltest):
		pseq = [p]
		for iternum in xrange(itermax):
			p_1, p = p, fn(p)
			pseq.append(p)
			if toltest(p_1,p):
				return p,pseq,iternum+1
		return None,pseq,itermax

 
def abisect(a, i1=0, i2=-1):
	"""Return int, the insertion index for a 0
	when there is a single sign change in sequence `a`.
	If a 0 exists, it may return that index (even if the
	sign is not different on each side of it.)
	Assumes `i1` and `i2` are valid indexes for `a`.
	"""
	n = len(a)
	if (i1 < 0): i1 += n
	if (i2 < 0): i2 += n
	if (i1 < 0 or i2 < 0): raise IndexError()
	if a[i1]*a[i2] >= 0:
		raise ValueError("Sign changing interval required.")
	while abs(i1-i2) > 1:
		midpt = (i1+i2) // 2
		if a[midpt] == 0:
			return midpt
		if a[midpt]*a[i1] > 0:
			i1 = midpt
		else:
			i2 = midpt
	return max(i1,i2)

class Bisect(IterativeProcess):
	def __init__(self, func, x1, x2, criterion=None):
		'''Return: None.
		Initialize the bisection iterative process.

		Example use::

			b1 = Bisect(f, x1, x2)
			b1.run()
			print b1.report()
			

		:Parameters:
			f : function (or callable object)
			  real-valued function of a real variable
			x1 : float
			  one side of a sign changing interval
			x2 : float
			  one side of a sign changing interval
			criterion : StopIter
			  convergence criterion
		'''
		IterativeProcess.__init__(self, criterion)  #TODO
		self.func = func
		f1, f2 = func(x1), func(x2)
		if f1 < 0 < f2:
			self.x_neg, self.x_pos = x1, x2
		elif f2 < 0 < f1:
			self.x_neg, self.x_pos = x2, x1
		else:
			raise ValueError("[%f,%f] is not a sign changing interval."%(x1,x2))
		self.history = [x1, x2]
	#overriding the following methods
	def default_criterion(self):
		return (lambda x, value, iteration: abs(x[1] - x[0]) < 1e-9) #TODO
	def finalize(self, value=None):
		self.value = (self.x_neg + self.x_pos)/2.0
	#implementing the following methods
	def iterate(self):
		midpt = (self.x_neg + self.x_pos)/2.0
		if self.func(midpt) > 0:
			self.x_pos = midpt
		else:
			self.x_neg = midpt
		return midpt
	def get_testinfo(self, value=None, iteration=0):
		#return (self.x_neg , self.x_pos)
		return self.history[-1], value






#BEGIN cx:optimize.bisect
def bisect(f, x1, x2, eps=1e-8):
	'''Return: a zero of `f`.
	(Simple implementation of bisection algorithm.)

	:parameters:
		f : real-valued function
		x1, x2 : sign changing interval
		eps : convergence criterion
	'''
	#require: sign change over initial interval
	f1, f2 = f(x1), f(x2)
	if f1*f2 > 0:
		raise ValueError('supply a sign changing interval')
	#initialize xneg, xpos
	xneg, xpos = (x1,x2) if(f2>0) else (x2,x1)
	while xpos-xneg > eps:
		xmid = (xneg+xpos)/2
		if f(xmid) > 0:
			xpos = xmid
		else:
			xneg = xmid
	return (xneg+xpos)/2
#END cx:optimize.bisect



#BEGIN: stop criteria #########################################################
class StopIter(object):
	def __init__(self, precision, maxiter = 100, testfreq=1):
		if (maxiter<1 or not precision>0):
			raise ValueError
		self.precision = precision
		self.maxiter = maxiter
		self.testfreq = testfreq
		self.optimized = False
	def __call__(self, ip, value=None, iteration=0):
		iteration = iteration or ip.iteration
		stop = False
		if not iteration%self.testfreq:
			if self.test(ip, value=value, iteration=iteration):
				stop = self.optimized = True
			elif iteration >= self.maxiter:
				stop = True
		return stop
	def test(self, ip, value=None, iteration=0):
		'''User must override this method.'''
		return NotImplemented

class AbsDiff(StopIter):
	"""
	True when the *absolute difference* of the test values is below a certain level
	"""
	def test(self, ip, value=None, iteration=0):
		val1, val2 =  ip.get_testinfo(value=value, iteration=iteration)
		return abs(val1 - val2) < self.precision


class RelDiff(StopIter):
	"""
	True when the *relative difference* of the test values is below a certain level
	"""
	def test(self, ip, value=None, iteration=0):
		val1, val2 =  ip.get_testinfo(value=value, iteration=iteration)
		return abs(val1 - val2) < self.precision * max(abs(val1), abs(val2))

#END: stop criteria #####################################################################

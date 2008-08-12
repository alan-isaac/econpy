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
	def __init__(self, criterion=None): #TODO
		'''Return: None.
		Usually overrriden by user.
		Initialize the iterator.
		Must set a criterion.
		'''
		self.set_criterion(criterion)
		self.iteration = 0
		self.history = []
	def set_criterion(self, criterion):
		if criterion is None:
			self.criterion = self.default_criterion
		else:
			self.criterion = criterion
	def run(self):
		#record initial state
		self.record_history()
		#iterate until criterion satisfied
		while True:
			self.iterate()
			self.iteration += 1
			self.record_history()
			if self.criterion(self):
				break
		self.finalize()
	def report(self):
		'''Return: string.'''
		final_value = getattr(self, 'value',None)
		optimized = getattr(self.criterion, 'optimized', "Undefined")
		iterations = self.iteration
		report = '''
		Final value:          %s
		Optimized:            %s
		Number of iterations: %d
		'''%(final_value, optimized, iterations)
		return report
	#users usually override the following methods
	def default_criterion(self, ip):
		return self.iteration >= 100
	def record_history(self):
		'''Should return: None.
		Must be able to handle initial state.
		'''
		pass
	def finalize(self):
		'''Should return: None.
		Should set self.value
		'''
		pass
	#users must implement the following methods
	def iterate(self):
		'''Should return: None.
		Do one iteration.
		Used by `run`.
		'''
		raise NotImplementedError
	def get_testval(self):
		'''Should return: testval.
		The testval must be usable by the criterion.
		Used by `run`.
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
	#overriding the following methods
	def default_criterion(self):
		return (lambda x: abs(x[1] - x[0]) < 1e-9) #TODO
	def record_history(self):
		self.history.append(self.get_testval())
	def finalize(self):
		self.value = (self.x_neg + self.x_pos)/2.0
	#implementing the following methods
	def iterate(self):
		midpt = (self.x_neg + self.x_pos)/2.0
		if self.func(midpt) > 0:
			self.x_pos = midpt
		else:
			self.x_neg = midpt
	def get_testval(self):
		return (self.x_neg , self.x_pos)






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
		raise ValueError
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
	def __init__(self, precision, maxit = 100):
		if (maxit<1 or not precision>0):
			raise ValueError
		self.precision = precision
		self.maxit = maxit
		self.optimized = False
	def __call__(self, ip):
		if self.test(ip):
			stop = True
			self.optimized = True
		elif ip.iteration >= self.maxit:
			stop = True
		else:
			stop = False
		return stop
	def test(self, ip):
		'''User must override this method.'''
		return NotImplemented

class AbsDiff(StopIter):
	"""
	True when the *absolute difference* of the test values is below a certain level
	"""
	def test(self, ip):
		val1, val2 =  ip.get_testval()
		return abs(val1 - val2) < self.precision


class RelDiff(StopIter):
	"""
	True when the *relative difference* of the test values is below a certain level
	"""
	def test(self, ip):
		val1, val2 =  ip.get_testval()
		return abs(val1 - val2) < self.precision * max(abs(val1), abs(val2))

#END: stop criteria #####################################################################

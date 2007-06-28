'''Some iterative process related classes.

:copyright: Alan G. Isaac, except where another author is specified.
:license: `MIT license`_

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
'''
from __future__ import absolute_import
from __future__ import division

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'
__lastmodified__ = '20070622'


class IterativeProcess(object):
	'''General description of iterative process.

	Requires an iterator and a criterion.
	Iterator must have `initialize` and `iterate` methods.
	The stop criterion must be a function or callable class;
	Criterion may have `state` attribute; if so, `state` is recorded.
	'''
	def __init__(self, iterator, criterion, **kwargs):
		self.iterator = iterator
		self.criterion = criterion
		self.history = []
		self.record = hasattr(iterator, 'state')
		self.iterations = 0
	def run(self):
		iterator, criterion = self.iterator, self.criterion
		record, history = self.record, self.history
		record_history = self.record_history
		iterations = 0
		#iterator.initialize()  #is this redundant to the __init__ method?
		if record:
			record_history(iterator)
			history.append(iterator.state)
		while not criterion(iterator, iterations):
			iterator.iterate()
			if record:
				record_history(iterator)
			iterations += 1
		self.iterations = iterations
		self.finalize()
	def record_history(self):
		self.history.append(self.iterator.state)
	def finalize(self):
		pass

		
class FunctionIterator(IterativeProcess):
	def __init__(self, func, x0):
		self.result = None
		self.func = func
		self.intial_value = x0

class Bisect(object):
	def __init__(self, func, x1, x2):
		self.func = func
		f1, f2 = func(x1), func(x2)
		if f1 < 0 < f2:
			self.x_neg, self.x_pos = x1, x2
		elif f2 < 0 < f1:
			self.x_neg, self.x_pos = x2, x1
		else:
			raise ValueError("[%f,%f] is not a sign changing interval."%(x1,x2))
	def iterate(self):
		midpt = (self.x_neg + self.x_pos)/2.0
		if self.func(midpt) > 0:
			self.x_pos = midpt
		else:
			self.x_neg = midpt
	def get_testvals(self):
		return (self.x_neg , self.x_pos)


#simple implementation of bisection
def bisect(f, x1, x2):
	#comment: set small number for convergence test
	eps = 1e-9
	#require: sign change over initial interval
	f1, f2 = f(x1), f(x2)
	if f1*f2 > 0:
		return #(error)
	xneg, xpos = (x1,x2) if(f2>0) else (x2,x1)
	while xpos-xneg > eps:
		midpt = (xneg+xpos)/2
		if f(midpt) > 0:
			xpos = midpt
		else:
			xneg = midpt
	return (xneg, xpos)


#BEGIN: stop criteria #####################################################################
class StopIter(object):
	def __init__(self, precision, maxit = 100):
		self.precision = precision
		self.maxit = maxit
		self.optimized = False
	def __call__(self, iterator, iterations):
		if iterations >= self.maxit:
			stop = True
		elif self.test_iterator(iterator):
			stop = True
			self.optimized = True
		else:
			stop = False
		return stop
	def test_iterator(self, iterator):
		'''User must override this method.'''
		return NotImplemented

class AbsDiff(StopIter):
	"""
	True when the *absolute difference* of the test values is below a certain level
	"""
	def test_iterator(self, iterator):
		val1, val2 = iterator.get_testvals()
		return abs(val1 - val2) < self.precision


class RelDiff(StopIter):
	"""
	True when the *relative difference* of the test values is below a certain level
	"""
	def test_iterator(self, iterator):
		val1, val2 = iterator.get_testvals()
		return abs(val1 - val2) < self.precision * max(abs(val1), abs(val2))

#END: stop criteria #####################################################################

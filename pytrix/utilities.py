"""
Provides an uncategorized collection of possibly useful utilities.
(The primary use is pedagogical.  For more sophisticated
implementations, see the NumPy library for numerical Python.)
As of 2021, Python 3.8+ is assumed and numpy is required.

:copyright: 2005-2021 Alan G. Isaac, except where another author is specified.
:license: `MIT license`_
:author: Alan G. Isaac (and others where specified)

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
"""
__docformat__ = "restructuredtext en"

import logging, random, itertools, operator
from collections import defaultdict
from typing import Any, Callable, List, Generator, Iterable, Sequence
from numbers import Real

import numpy as np

have_scipy = False
try:
    import scipy as sp
    have_scipy = True
    logging.info("have_scipy is True")
except ImportError:
    logging.info("SciPy not available.")


def colon(start, increment, end):
    """Return array of float64.  Uses numpy to
    approximate the behavior of Matlab's `colon`.
    :note: see numpy.arange, which is usually preferable
    """
    if np.iscomplex((start,increment,end)).any():
        raise ValueError("colon does not accept complex arguments")
    if increment==0 or increment*(start - end)>0:
        return np.array([])
    m = int( np.fix((end-start) / float(increment)) )
    return start + increment * np.arange(m+1)

def unique(x, key=None, reverse=False):
    """Return sorted list of unique items in `x`.
    If you don't need `key`, use `np.unique` instead,
    reversing if needed. Also, consider 
    `dict.fromkeys(x).keys()` to retain order of encounter.
    """
    return sorted(set(x), key=key, reverse=reverse)

def ireduce(
    func: Callable[[Any,Any],Any],
    iterable: Iterable[Any],
    init=None
    ) -> Generator:
    """Return generator of sequential reductions by `func`,
    which must be a bivariate function.
    Does *not* yield init for empty iterable.

    Example use:
    >>> list(ireduce(operator.mul, range(1,5),init=1))
    [1, 2, 6, 24]
    >>>    

    :thanks: Peter Otten and Michael Spencer
    :see: Bryn Keller's scanl (for a different approach)
        http://www.xoltar.org/languages/python/datastruct.py
    :since: 2005-11-23
    """
    iterable = iter(iterable)
    if init is None:
        init = next(iterable)
        yield init
    else:
        init = func(init, iterable.next())
        yield init
    for item in iterable:
        init = func(init, item)
        yield init

def cumreduce(func, seq, init = None):
    """Return list of length len(seq),
    the sequential reductions of seq.
    An empty seq always returns empty list

    Example use:
    >>> cumreduce(operator.mul, range(1,5), init=1)
    [1, 2, 6, 24]
    >>>    

    :since: 2005-11-19
    :calls: ireduce
    :note: Used by cumsum and cumprod.
    """
    return list( ireduce(func, seq, init) )

def cumsum(
    xs: Sequence[Real]
    ) -> List[Real]:
    """Return the accumulated sum of the xs,
    as a list.
    :note: use np.cumsum when possible, for speed.
    """
    return cumreduce(operator.add, xs)

def cumprod(seq):
    return cumreduce(operator.mul, seq)


def safe_iter(obj):
    """Returns iterator.
    Returns iter((,)) when obj is None.
    Returns iter(obj) when obj is iterable and not "atomic".
    Returns iter((obj,)) when obj is "atomic" or not iterable.
    Based *very* closely on Michael Spencer's `safe_iter`.
    
    :thanks: Michael Spencer <mahs telcopartners.com>
    :since:  2006-01-11
    """
    iter2atomic = (basestring,)
    if obj is None:
        obj = ()
    elif isinstance(obj, iter2atomic):
        obj = (obj,)
    try:
        result = iter(obj)
    except TypeError:
        result = iter((obj,))
    return result

def test_safe_iter():
    """
    :author: Michael Spencer <mahs telcopartners.com>
    """
    assert list(safe_iter(1)) == [1]
    assert list(safe_iter("string")) == ["string"]
    assert list(safe_iter(range(10))) == range(10)
    assert list(safe_iter(xrange(10))) == list(xrange(10))
    assert list(safe_iter((1,2,3))) == [1,2,3]
    assert list(safe_iter(1.0)) == [1.0]
    assert list(safe_iter(1+2j)) == [1+2j]
    xiter = iter(range(10))
    assert safe_iter(xiter) is xiter
    xiter = (a for a in range(10))
    assert safe_iter(xiter) is xiter
    assert list(safe_iter(None)) == []

#all the Gini calculations include the 1/N correction
# TODO: speed comparison


def gini( #follow transformed formula
    xs: Sequence[Real],
    isSorted=False
    ) -> Real:
    """Return Gini coefficient computed with transformed formula.
    :note: includes the 1/N "bessel" correction
    """
    if not isSorted:
        xs = np.sort(xs)  # increasing order
    N = len(xs)
    ys = np.cumsum(xs)
    B = ys.sum() / N / ys[-1]
    return 1.0 - 2*B + 1.0/N

def alt_gini(
    xs: Sequence[Real],
    isSorted=False
    ) -> Real:
    """Return Gini coefficient computed with standard formula.
    :note: includes the 1/N "bessel" correction
    """
    if not isSorted:
        xs = np.sort(xs)  # increasing order
    N = len(xs)
    B = np.dot(xs, np.arange(N,0,-1)) / N / xs.sum()
    return 1.0 - 2.0*B + 1.0/N

def py_gini(
    xs: Sequence[Real],
    isSorted=False
    ) -> Real:
    """Return Gini coefficient computed with standard formula.
    :note: does not require numpy.
    """
    if not isSorted:
        xs = sorted(xs)  # increasing order
    N = len(xs)
    B = sum(xi * (N-i) for i,xi in enumerate(xs)) / N / sum(xs)
    return 1.0 - 2.0*B + 1.0/N

def py_gini2(x): #follow transformed formula
    """Return computed Gini coefficient.

    :note: follows transformed formula, like R code in 'ineq'
    :see: `calc_gini`
    """
    x = sorted(x)  # increasing order
    n = len(x)
    G = sum(xi * (i+1) for i,xi in enumerate(x))
    G = 2.0*G/(n*sum(x)) #2*B
    return G - 1 - (1./n)

def ginis(xss, bessel=False):
    """Return 1d array, the Gini coefficient for each row of xss.
    A NaN element means computation was impossible for that series.

    xss: [[float]]
      2d array (accepts only nonnegative real values); *rows* are series.
    bessel: bool
      False (default): normalize by series length (k); True: normalize by `k-1`

    NOTE:
      Requires numpy.
      Gini is not computed for those series containing NaNs or negatives.
      Thereby lacks some features of the ginicoeff code by Oleg Komarov:
      https://www.mathworks.com/matlabcentral/fileexchange/26452-okomarov-ginicoeff
    
      The Gini coefficient ranges from 0 (total equality) to 0 (total in equality).
      A standard Gini formula for K (ascending) sorted incomes xi:
      with n = Sum[(n+1-i)*x[[i]],{i,K}]   and   d = Sum[xi,{i,K}]
      without correction (DEFAULT) | with correction (bessel=True)
      G = (K+1-2*(n/d))/K          | G = (K+1-2*(n/d))/(K-1)
      
    EXAMPLE::
      xss =  [[5, 2, 3, 4, 1],[3, 2, 1, 5, np.nan]];
      gs  =  ginis(xss)
    """
    #test preconditions:
    assert bessel in (True,False), 'ginis: bessel has invalid format'
    xss = np.asarray(xss)
    r,k = xss.shape
    assert k == len(xss[0]), "bad series length"

    #True -> row has no negatives and all numeric, False ow
    oks = np.logical_and((xss >= 0).all(axis=1), np.isfinite(xss).all(axis=1))
    xss = np.sort(xss[oks], axis=1)
    totals = xss.sum(axis=1)
    assert (totals > 0).all(), "all-zero series forbidden"

    # Gini coefficient before scaling:
    wts = k - np.arange(len(xss[0]))
    gs = k + 1 - 2*(np.dot(xss,wts) / totals);

    #Add sample correction if requested
    if bessel:
        gs /= (k-1);
    else: #default
        gs /= k;
    result = np.empty(r)
    result.fill(np.nan)
    result[oks] = gs
    return result


def groupsof(seq,n):
    """Return len(self)//n groups of n, discarding last len(self)%n players."""
    #use itertools to avoid creating unneeded lists
    return itertools.izip(*[iter(seq)]*n)


def gatherby(seq, key):
    """Return map from key values `k` to list
    of items such `k=key(item)`
    """
    groups = defaultdict(list)
    for item in seq:
        groups[key(item)].append(item)
    return groups



def n_each_rand(n,itemtuple=(True,False)):
    """Yield: n of each of two items,
    one at a time, in random order.

    :since:  2006-06-20
    :date:   2007-07-11
    """
    item0, item1 = itemtuple
    ct0, ct1 = 0, 0
    while ct0+ct1<2*n:
        if random.random() < ((n-ct0)/(2.0*n-ct0-ct1)):
            next_item = item0
            ct0 += 1
        else:
            next_item = item1
            ct1 += 1
        yield next_item


def permute(x):
    """Return one permutation of a sequence or array.

    :since:  2005-06-20
    :date:   2007-06-22
    """
    #use numpy if available
    try:
        x = numpy.array(x,copy=True)
        numpy.random.shuffle(x.flat)
    except NameError:
        x = list(x) #1d only!
        random.shuffle(x)
    return x

def permutations(lst):
    """Return all permutations of `lst`.
    
    :type lst:  sequence
    :rtype:     list of lists
    :return:    all permutations of `lst`
    :since:     2005-06-20
    :date:      2007-06-22
    :note:      recursive
    """
    lst = list(lst)
    return [ [lst[i]] + x
                    for i in range(len(lst))
                    for x in permutations(lst[:i]+lst[i+1:])
            ] or [[]]


def permutationsg(lst):
    """Return generator of all permutations of a list.

    :type `lst`: sequence
    :rtype:      list of lists
    :return:     all permutations of `lst`
    :requires:   Python 2.4+
    :note:       recursive
    :since:      2005-06-20
    :date:       2006-12-18
    :see:        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/190465
    :contact:    mailto:aisaac AT american.edu
    """
    if len(lst)>1:
        for i in range(len(lst)):
            for x in permutationsg(lst[:i]+lst[i+1:]):
                yield [lst[i]]+x
    else:
        yield lst

def combinations(n,t) :
    """Return all t-combinations (as indices).

    :type `lst`: sequence
    :rtype:      list of lists
    :return:     all t-combinations of n elements (by index)
    :requires:   Python 2.4+ (for generators)
    :since:      2007-09-19
    :see:        Knuth vol.4 ch.3
    :author:     Charles Harris (using Knuth's algorithm)
    """
    c = range(t + 2)  #use range not arange because it is faster and ...
    c[-2] = n
    c[-1] = 0
    while 1 :
        yield c[:t]  #... a slice of a list is a copy!
        j = 0
        while c[j] + 1 == c[j+1] :
            c[j] = j
            j += 1
        if j >= t :
            return
        c[j] += 1

def pascal_row(n):
    """Yield elements of row n of Pascal's triangle
    the coefficients of (x+y)**n.
    :see: http://www.bedroomlan.org/coding/pascals-triangle-python
          for a different approach
    """
    Cnk = 1
    yield Cnk
    for k in range(0, n):
        Cnk *= (n - k)
        Cnk /= (k + 1)
        yield Cnk


###### set utilities ###########################################
#BEGIN subsetid
def subsetid(length):
    """Return: binary representations of all subsets
    of a set of length `length`.
    """
    if length==0:
        return ['']
    else:
        result0 = subsetid(length-1)
        return ['0'+id for id in result0]+['1'+id for id in result0]
#END subsetid

#:see: http://mail.python.org/pipermail/python-list/2001-May/085964.html
#BEGIN PowerSet
class PowerSet:
    """
    All 2**n subsets are available by index in range(2**n).
    Binary representation of index is used for element selection.
    """
    def __init__(self, s):
        """
        :note: to know order ex ante, `s` shd be a sequence
        """
        self.s = s
        self.scard = len(s)  #cardinality of set s
        self.pscard = 2**self.scard #cardinality of powerset
    def __getitem__(self, idx):
        if idx < 0:
            idx += self.pscard
        if idx < 0 or idx >= self.pscard:
            raise IndexError("%i is out of range"%(i))
        result = set( si for i,si in enumerate(self.s) if (idx>>i)&1 )
        return result
#END PowerSet

#########  marginally relevant utilities  ######################
def int2binary(i, strlen=None, reverse=False):
    """Return binary string representation of nonnegative integer.
    `i` is the integer.
    `strlen` is number of 'bits' in the representation.
    """
    assert i>=0, "Nonnegative integers only"
    if strlen is None:
        strlen = 4  #set a minumu string length
        n = i>>4
        while n:
            n >>= 4
            strlen += 4
        strlen = max(1,strlen) #to handle 0
    else:
        assert i<2**strlen, "Inadequate string length."
    if reverse:
        result = "".join( str((i>>y)&1) for y in range(strlen) )
    else:
        result = "".join( str((i>>y)&1) for y in range(strlen-1, -1, -1) )
    return result

def grep(pattern, *files):
    """Usage: grep("grep", *glob.glob("*.py"))

    :author: Fredrik Lundh
    :since: 2005-10-25
    """
    try:
        search = re.compile(pattern).search
    except NameError:
        import re
        search = re.compile(pattern).search
    for file in files:
        for index, line in enumerate(open(file)):
            if search(line):
                print(":".join((file, str(index+1), line[:-1])))


# vim: set expandtab:ts=4:sw=4

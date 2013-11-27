from ..pytrix.utilities import permutations, calc_gini
import logging
from itertools import izip

import random
rng = random.Random()
rng.seed(314)

import numpy as np

def match_exclude(group1, group2, exclude):
	"""Return list of matched pairs meeting an exclusion criterion.

	:Parameters:
	  group1 : sequence
	    first group for matches
	  group2 : sequence
	    second group for matches
	  exclude : function
	    should return True if pairing is excluded else False
	:rtype:      list of tuples
	:return:     pairs meeting exclusion criterion
	:requires:   Python 2.5+ (uses `any`)
	:requires:   permutations from econpy.pytrix.utilities
	:since:      2005-06-20
	:date:       2007-12-05
	:contact:    mailto:aisaac AT american.edu
	"""
	#one group may be larger; call it group2
	success = False
	#get all the permutations of the larger group
	# TODO: use k-permuations
	if len(group1) <= len(group2):
		biggroup_permutations = permutations(group2)
		for g in biggroup_permutations:
			result = zip(group1, g)
			if not any( exclude(m,f) for (m,f) in result ):
				success = True
				break
	else:
		biggroup_permutations = permutations(group1)
		for g in biggroup_permutations:
			result = zip(g, group2)
			if not any( exclude(m,f) for (m,f) in result ):
				success = True
				break
	if success:
		return result

def sexer_mf(n):
	"""Yield str: M, F n times each."""
	for i in range(n):
		yield 'M'
		yield 'F'

def sexer_random2(n, rng=rng):
	"""Yield str: 'M' or 'F' randomly,
	holding overall sex ratio constant.
	
	n : int
		number of each sex
	rng : Random instance
		random number generator
	:note: wasteful if cohorts are very large,
	       use n_each_rand instead
	"""
	sexes = list('MF'*n)
	rng.shuffle(sexes)
	for s in sexes:
		yield s



def n_each_rand(n, kindtuple=('M','F'), rng=rng):
	"""Yields n of each of two (immutable) objects,
	in random order.

	If we still need to generate
	ct0 of kind0 and ct1 of kind1
	then we will yield
	a kind0 object with probability ct0/(ct0+ct1)

	Parameters
	----------

	n : int
		number of *each* kind to generate
	kindtuple : tuple
		2-tuple contains the two immutable objects

	:requires:   Python 2.4+
	:since:      2005-06-20
	:date:       2007-12-05
	"""
	assert (n>0), "n shd be a positive integer"
	kind0, kind1 = kindtuple
	ct0, total = n, n+n
	while (total > 0):
		if rng.random() * total < ct0:
			next_kind = kind0
			ct0 -= 1
		else:
			next_kind = kind1
		total -= 1
		yield next_kind
	assert (ct0 == 0)



def gini2sharesPareto(gini, nbrackets):
	"""Return generator of floats: the incremental
	income share implied by `gini` for each bracket.
	(Brackets are evenly spaced.)

	Write he Lorenz curve for the Pareto distribution as
	$F(p) = 1 - (1 - p)^\delta$,
	where $p$ is the cumulative proportion of the population,
	$\delta=(1-G)/(1+G)$, and $G$ is the Gini.
	With $N$ brackets, let $p_i= i/N$ ($i=1,\dots,N$)
	and set the share of the $i/N$ proportion of agents to
	$F(p_i) = 1 - (1 - p_i)^\delta$.
	The incremental share is the $i$-th bracket is therefore
	F(p_i) - F(p_{i-1})$ and $p_{i}-p_{i-1} = 1/N$, so
	$(1 - (i- 1)/N)^\delta - (1 - i/N)^\delta$.
	or
	$[(N - (i- 1))^\delta - (N - i)^\delta](1/N)^\delta$.

	:note: roughly based on Eswaran & Kotwal (1986)
	:note: uses a right sum, so resulting Gini slightly low
	:since:   2013-10-19
	"""
	if not (0 <= gini < 1):
		raise ValueError('gini must be in (0,1)')
	if nbrackets != int(abs(nbrackets)):
		raise ValueError('nbrackets should be a positive integer')
	d = (1-gini)/(1+gini) #delta = B/(2A+B)  
	sb = 1.0/nbrackets  #width of brackets
	fpc1 = 1   # 1-F(0)
	i = 0.0
	for _ in range(nbrackets):
		i += 1
		#complement of i-th cumulative share
		fpc2 = (1 - i/nbrackets)**d  #1-F(p_i)
		yield fpc1 - fpc2
		fpc1 = fpc2

def gini2shares01(gini, nbrackets):
	"""Return generator of floats:
	income share implied by `gini` for each bracket.

	:note: based on Yunker 1999, p.238
	:note: uses a right sum, so resulting Gini slightly low
	:note: consider Lorenz curve function representation
	       y=x**g for g>1
	       B = \int_0^1 x**g dx = x**(g+1)/(g+1) | = 1/(g+1)
	       So G = 1-2B = (g-1)/(g+1) is the implied Gini
	       Note (1+G)/(1-G) = 2g/2 = g. (Used below.)
	:since:  2006-06-20
	:date:   2013-10-19
	"""
	if not (0 <= gini < 1):
		raise ValueError('gini must be in (0,1)')
	if nbrackets != int(abs(nbrackets)):
		raise ValueError('nbrackets should be a positive integer')
	g = (1+gini)/(1-gini) # (2A+B)/B
	sb = 1.0/nbrackets  #width of brackets
	sbg = sb**g
	ig = 0
	for i in range(nbrackets):
		#i-th cumulative share is (1+i)**g * sb**g
		ig2 = (1+i)**g
		yield (ig2-ig) * sbg
		ig = ig2


#Use of gini2shares is deprecated
gini2shares = gini2shares01


def impose_gini(wtotal, units, gini, shuffle=False):
	"""Return None.
	Distribute resources `wtotal` among members of `units` based on `gini`,
	imposing a `gini` based distribution.

	:Parameters:
	  wtotal : number
	    total resources to distribute
	  units : list
	    units (households) to share `wtotal`, must have `payin` method
	  gini : float
	    Gini coefficient that should result from distribution
	  shuffle : bool
	    if False, first unit receives least resources, etc.
	:note: lots of copying! (not good for very large number of households)
	:note: need to compute number of units *before* distributing.
	:todo: eliminate redundant error checks
	:comment: uses Indiv methods ...
	:comment: was named `distribute` long ago
	"""
	units = list(units)
	logging.debug("""Enter utilities.impose_gini.
	wtotal: %f
	units: %s
	gini: %f
	shuffle: %s"""%(wtotal,units[:5],gini, shuffle) )
	nb = len(units)  #number of brackets 
	shares = list( gini2shares(gini, nb) )
	if shuffle:   #enforce Gini but distribute randomly
		rng.shuffle(shares)
	w = ( wtotal*share for share in shares )
	ct = 0
	units2 = set()  #this is just for error check
	for i, w_i in izip(units, w):
		i.payin(w_i)   #ADD to individual wealth
		units2.add(i)
	assert len(units2)==nb, "`units` shd not contain duplicates"
	logging.debug( "Desired gini: %4.2f,  Achieved Gini: %4.2f"%( gini,calc_gini( i.networth for i in units2 )))
 

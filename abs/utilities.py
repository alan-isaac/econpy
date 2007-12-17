from ..pytrix.utilities import permutations

def match_exclude(group1, group2, exclude):
	'''Return list of matched pairs meeting an exclusion criterion.

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
	'''
	#one group may be larger; call it group2
	success = False
	if len(group1) <= len(group2):
		#get all the permutations of the larger group
		# TODO: use k-permuations
		biggroup_permutations = permutations(group2)
		for g in biggroup_permutations:
			result = zip(group1,g)
			if not any( exclude(m,f) for (m,f) in result ):
				success = True
				break
	else:
		biggroup_permutations = permutations(group1)
		for g in biggroup_permutations:
			result = zip(g,group2)
			if not any( exclude(m,f) for (m,f) in result ):
				success = True
				break
	if success:
		return result



def n_each_rand(n,kindtuple=('M','F')):
	'''Yields n of each of two (immutable) objects,
	in random order.

	If we still need to generate
	ct0 of kind0 and ct1 of kind1
	then we will yield
	a kind0 object with probability ct0/(ct0+ct1)

	:Parameters:
	  n : int
	    number of *each* kind to generate
	  kindtuple : tuple
	    tuple contains the two immutable objects
	:requires:   Python 2.4+
	:since:      2005-06-20
	:date:       2007-12-05
	:contact:    mailto:aisaac AT american.edu
	'''
	assert (n>0), "n shd be a positive integer"
	kind0, kind1 = kindtuple
	ct0, total = n, n+n
	while (total > 0):
		if random.random() * total < ct0:
			next_kind = kind0
			ct0 -= 1
		else:
			next_kind = kind1
		total -= 1
		yield next_kind
	assert (ct0 == 0)


def gini2shares(gini, nbrackets):
	'''Return: income share for each bracket implied by `gini`.

	:note: based on Yunker 1999, p.238
	:todo: improve computation accuracy
	:note: consider Lorenz curve function representation
	       y=x**g for 0<g<1.
	       B = \int_0^1 x**g dx = x**(g+1)/(g+1) | = 1/(g+1)
	       So G = 1-2B = (g-1)/(g+1)
	       Note (1+G)/(1-G) = 2g/2 = g. (Used below.)
	:since:  2006-06-20
	:date:   2007-07-11
	:contact: aisaac AT american.edu
	'''
	assert (0 <= gini < 1)
	g = (1+gini)/(1-gini) # (2A+B)/B
	sb = 1.0/nbrackets  #width of brackets
	#cum prop =  ((i+1)*sb)**g = (i+1)**g * sb**g
	#change prop = [(1+i)**g-(i)**g]*sb**g
	#cumulative_proportions = list( ((i+1)*sb)**g for i in range(nbrackets) )
	shares = [ ((1+i)**g-(i)**g)*sb**g for i in range(nbrackets)]  #chk TODO
	return shares

def distribute(wtotal, units, gini, shuffle=False):
	units = list(units)
	nb = len(units)  #number of brackets 
	units2 = set(units)
	assert len(units2)==nb
	g = (1+gini)/(1-gini) # (2A+B)/B
	shares = gini2shares(gini, nb)
	if shuffle:   #enforce Gini but distribute randomly
		random.shuffle(shares)
	w = ( wtotal*share for share in shares )
	for wi in w:
		units.pop().receive_income(wi)   #ADD to individual wealth
	assert (not units),  "Length shd now be zero."
	script_logger.info( "Desired gini: %4.2f,  Achieved Gini: %4.2f"%( gini,utilities.calc_gini( i.calc_wealth() for i in units2 )))


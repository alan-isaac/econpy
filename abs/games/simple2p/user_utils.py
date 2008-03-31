# File: user_utils.py 
from collections import defaultdict
 



############# alternative approach to grid population #######################
########### (a bit faster but more obscure for reading) #####################
import itertools
def groupsof(lst,n): #used to populate SimpleTorus by row
	"""Return len(self)//n groups of n, discarding last len(self)%n players."""
	#use itertools to avoid creating unneeded lists
	return itertools.izip(*[iter(lst)]*n)

def alt_populate(nrows, ncols, players):
	assert len(players)==nrows*ncols
	#fill a 2d grid with players
	players2d = list( list(g) for g in groupsof(players, ncols) )
	return players2d


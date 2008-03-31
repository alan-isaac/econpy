'''
Provide objects for simple 2-person game simulations with arbitrary payoff matrix.
This module emphasizes simplicity and readability over generality or speed.
Includes spatial (torus) games with specifiable neighborhood.

:contact: http://www.american.edu/academic.depts/cas/econ/faculty/isaac/isaac1.htm
:license: `MIT license`_

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php 
'''
from __future__ import division, with_statement
__docformat__ = "restructuredtext en"
__author__  =   "Alan G. Isaac"
__version__ = "1.0"
__needs__ = '2.5'

from itertools import izip
import random
from collections import defaultdict

#############################################################
###########  simple utilities  ##############################
#############################################################
#BEGIN user_utils
def mean(seq):  #simplest computation of mean
	"""Return mean of values in `seq`."""
	n = len(seq)
	return sum(seq)/float(n)

def transpose(seqseq): #simple 2-dimensional transpose
	"""Return transpose of `seqseq`."""
	return zip(*seqseq)

def topscore_playertypes(player):
	"""Return list of best (maximum payoff) player types."""
	best_types = [player.playertype]
	best_payoff = player.get_payoff()
	for opponent in player.players_played:
		payoff = opponent.get_payoff()
		if payoff > best_payoff:
			best_payoff = payoff
			best_types = [opponent.playertype]
		elif payoff == best_payoff:
			best_types.append(opponent.playertype)
	return best_types

def maxmin_playertypes(player):
	"""Return list of best (maxmin payoff) player types."""
	# initialize mapping (playertypes -> payoffs)
	pt2po = dict()
	# find minimum payoff for each encountered playertype
	pt2po[ player.playertype ] = player.get_payoff()
	for n in player.get_neighbors():
		pt, po = n.playertype, n.get_payoff()
		try:
			if pt2po[pt] > po:
				pt2po[pt] = po
		except KeyError:
			pt2po[pt] = po
	# find best playertype (max of minimum payoffs)
	maxmin = max( pt2po.itervalues() )
	best_playertypes = [ pt for pt in pt2po if pt2po[pt]==maxmin ]
	return best_playertypes

def random_pairs_of(players):
	"""Return all of players as random pairs."""
	# copy player list
	players = list( players )
	# shuffle the new player list in place
	random.shuffle(players)
	# yield the shuffled players, 2 at a time
	player_iter = iter(players)
	return izip(player_iter, player_iter)

def compute_neighbors(player, grid):
	"""Return neighbors of `player` on `grid`."""
	player_row, player_col = player.gridlocation
	nrows, ncols = grid.nrows, grid.ncols
	players2d = grid.players2d
	# initialize list of neighbors
	neighbors = list()
	# append all neighbors to list
	for offset in grid.neighborhood:
		dc, dr = offset      #note: x,y neighborhood
		r = (player_row + dr) % nrows
		c = (player_col + dc) % ncols
		neighbor = players2d[r][c]
		neighbors.append(neighbor)
	return neighbors

def count_player_types(players):
	"""Return map (playertype -> frequency) for `players`."""
	ptype_counts = defaultdict(int) #empty dictionary, default count is 0
	for player in players:
		ptype_counts[ player.playertype ] += 1
	return ptype_counts

#END user_utils
#############################################################


#note: using player *list* so that index method available
#BEGIN SimpleGame
class SimpleGame:
	def __init__(self, player1, player2, payoffmat):
		# initialize instance attributes
		self.players = [ player1, player2 ]
		self.payoffmat = payoffmat
		self.history = list()
	def run(self, game_iter=4):
		# unpack the two players
		player1, player2 = self.players
		# each iteration, get new moves and append these to history
		for iteration in range(game_iter):
			newmoves = player1.move(self), player2.move(self)
			self.history.append(newmoves)
		# prompt players to record the game played (i.e., 'self')
		player1.record(self); player2.record(self)
	def payoff(self):
		# unpack the two players
		player1, player2 = self.players
		# generate a payoff pair for each game iteration
		payoffs = (self.payoffmat[m1][m2] for (m1,m2) in self.history)
		# transpose to get a payoff sequence for each player
		pay1, pay2 = transpose(payoffs)
		# return a mapping of each player to its mean payoff
		return { player1:mean(pay1), player2:mean(pay2) }
#END SimpleGame 


#BEGIN CDIGame
class CDIGame(SimpleGame):
	def __init__(self, player1, player2, payoffmat):
		# begin initialization with `__init__` from `SimpleGame`
		SimpleGame.__init__(self, player1, player2, payoffmat)
		# initialize the new data attribute
		self.opponents = {player1:player2, player2:player1}
	def get_last_move(self, player):
		# if history not empty, return prior move of `player`
		if self.history:
			player_idx = self.players.index(player)
			last_move = self.history[-1][player_idx]
		else:
			last_move = None
		return last_move
#END CDIGame

#formerly SimpleCDIType
#BEGIN CDIPlayerType
class CDIPlayerType:
	def __init__(self, p_cdi=(0.5,0.5,0.5)):
		self.p_cdi = p_cdi
	def move(self, player, game):
		# get opponent and learn her last move
		opponent = game.opponents[player]
		last_move = game.get_last_move(opponent)
		# respond to opponent's last move
		if last_move is None:
			p_defect = self.p_cdi[-1]
		else:
			p_defect = self.p_cdi[last_move]
		return random.uniform(0,1) < p_defect
#END CDIPlayerType

#BEGIN SimplePlayer
class SimplePlayer:
	def __init__(self, playertype):
		self.playertype = playertype
		self.reset()
	def reset(self):
		self.games_played = list()   #empty list
		self.players_played = list()  #empty list
	def move(self,game):
		# delegate move to playertype
		return self.playertype.move(self, game)
	def record(self, game):
		self.games_played.append(game)
		opponent = game.opponents[self]
		self.players_played.append(opponent)
#END SimplePlayer

#########################################################################
###################### Begin: Soup Classes ##############################
#########################################################################

#Note: eliminated selection_pressure class variable => changed evolve
#Note: returns *total* payoff, not average payoff!
#BEGIN SoupPlayer
class SoupPlayer(SimplePlayer):
	def evolve(self):
		self.playertype = self.next_playertype
	def get_payoff(self):
		return sum( game.payoff()[self] for game in self.games_played )
	def choose_next_type(self):
		# find the playertype(s) producing the highest score(s)
		best_playertypes = topscore_playertypes(self)
		# choose randomly from these best playertypes
		self.next_playertype = random.choice(best_playertypes)
	#END SoupPlayer


#BEGIN SoupRound
class SoupRound:
	def __init__(self, players, payoffmat):
		self.players = players
		self.payoffmat = payoffmat
	def run(self):
		payoff_matrix = self.payoffmat
		for player1, player2 in random_pairs_of(self.players):
			game = CDIGame(player1, player2, payoff_matrix)
			game.run()
		#END SoupRound
		print self.average_payoff()
	def average_payoff(self): #average player payoff for the round
		players = self.players
		payoff = 0
		for player in players:
			payoff += player.get_payoff()
		payoff /= len(players)
		return payoff
	''' old version:
	def run(self):
		players = list( self.players ) #copy player list
		random.shuffle(players)
		while len(players) > 1:
			player1, player2 = players.pop(), players.pop()
			game = CDIGame(player1, player2, self.payoffmat)
			game.run()
	'''

#########################################################################
###################### End: Soup Classes ################################
#########################################################################

#########################################################################
###################### Begin: Spatial Classes ###########################
#########################################################################
#BEGIN GridPlayer
class GridPlayer(SoupPlayer):
	def set_grid(self, grid, row, column):
		self.grid = grid
		self.gridlocation = row, column
	def get_neighbors(self): #delegate to the grid
		return self.grid.get_neighbors(self)
#END GridPlayer

#BEGIN MaxminGridPlayer
class MaxminGridPlayer(GridPlayer):
	def choose_next_type(self):
		# find playertype(s) with the highest minimum score
		best_playertypes = maxmin_playertypes(self)
		# choose randomly from these best playertypes
		self.next_playertype = random.choice(best_playertypes)
#END MaxminGridPlayer

#BEGIN GridRound
class GridRound(SoupRound):
	def run(self):
		payoff_matrix = self.payoffmat
		# each player plays each of its neighbors once
		for player in self.players:
			for neighbor in player.get_neighbors():
				if neighbor not in player.players_played:
					# create and run a new game
					game = CDIGame(player, neighbor, payoff_matrix)
					game.run()
#END GridRound

#############################################################
############## very simple grid class  ######################
#############################################################
#BEGIN SimpleTorus
class SimpleTorus:
	def __init__(self, nrows, ncols, neighborhood):
		self.nrows, self.ncols = nrows, ncols
		self.neighborhood = neighborhood
		# empty dict (will eventually map players to neighbors)
		self.players2neighbors = dict()
		# create 2d grid (each element is None until populated)
		self.players2d = [[None]*ncols for i in range(nrows)]
	def populate(self, players1d):   # fill grid with players
		players = iter(players1d)
		# put a player in each grid location (row, column)
		for row in range(self.nrows):
			for column in range(self.ncols):
				player = players.next()
				self.players2d[row][column] = player
				player.set_grid(self, row, column)
	def get_neighbors(self, player):
		if player in self.players2neighbors: # neighbors precomputed
			neighbors = self.players2neighbors[ player ]
		else:                        # neighbors not yet computed
			neighbors = compute_neighbors(player, self)
			# map player to computed neighbors (for later use)
			self.players2neighbors[ player ] = neighbors
		return neighbors
#END SimpleTorus
#########################################################################
###################### End: Spatial Classes #############################
#########################################################################

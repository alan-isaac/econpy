'''
Provide objects for simple 2-person game simulations with arbitrary payoff matrix.
This module emphasizes simplicity and readability over generality or speed.
Includes spatial (torus) games with specifiable neighborhood.
Python 2.7 users shd retrive Version 1.

:contact: https://subversion.american.edu/aisaac/isaac1.htm
:license: `MIT license`_

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php 
'''
__docformat__ = "restructuredtext en"
__author__  =   "Alan G. Isaac"
__version__ = "1.1"
__needs__ = '3.8'

import sys
if sys.version_info.major < 3 or sys.version_info.minor < 8:
    sys.exit("Python version 3.8+ required")

import random
from typing import List, Sequence
from statistics import mean
from collections import defaultdict

#note: initialize player *list* so that index method available
#  (which is needed by subclasses)
#BEGIN SimpleGame
class SimpleGame(object):
    def __init__(self, player1, player2, payoffMatrix, gameIter=4):
        # initialize instance attributes
        self.players = [ player1, player2 ]
        self.payoffMatrix = payoffMatrix
        self.gameIter = gameIter
        self.history = list()  #list of move *pairs*
    def run(self):
        player1, player2 = self.players # unpack the players
        # each iteration, get moves and append to history
        for iteration in range(self.gameIter):
            newmoves = player1.move(self), player2.move(self)
            self.history.append(newmoves)
        # ask players to record this game as played (i.e., 'self')
        player1.record(self); player2.record(self)
    #BEGIN SimpleGame::payoff
    def payoff(self) -> dict:
        player1, player2 = self.players # unpack the players
        # generate a payoff *pair* for each game iteration
        payoffs = (self.payoffMatrix[m1][m2] for (m1,m2) in self.history)
        # payoff sequence for each player:
        pay1, pay2 = zip(*payoffs) # 2-dimensional transpose
        # return a mapping of each player to its mean payoff
        return {player1: mean(pay1), player2: mean(pay2)}
#END SimpleGame 

#A CDIGame extends SimpleGame (inherits run with default of 4 iters).
#BEGIN CDIGame
class CDIGame(SimpleGame):
    def __init__(self, player1, player2, payoffMatrix, gameIter):
        # begin initialization with `__init__` from `SimpleGame`
        SimpleGame.__init__(self, player1, player2, payoffMatrix, gameIter=gameIter)
        # initialize the new data attribute
        self.opponents = {player1:player2, player2:player1}
    def get_last_move(self, player):
        """Return prior move of `player` if history not empty,
        else None."""
        if (0 < len(self.history)):
            player_idx = self.players.index(player)
            last_move = self.history[-1][player_idx]
        else:
            last_move = None
        return last_move
#END CDIGame

#########################################################################
##################### Begin: Player Classes #############################
#########################################################################

#BEGIN CDIPlayerType
class CDIPlayerType(object):
    def __init__(self, p_cdi=(0.5,0.5,0.5), prng=None):
        self.p_cdi = p_cdi
        try:
            self.uniform = prng.uniform
        except AttributeError:
            self.uniform = random.uniform
    def move(self, player, game):
        """Return bool, True for defect."""
        # get opponent and learn her last move
        opponent = game.opponents[player]
        last_move = game.get_last_move(opponent)
        # respond to opponent's last move
        if last_move is None:
            p_defect = self.p_cdi[-1]
        else:
            p_defect = self.p_cdi[last_move]
        return int(self.uniform(0,1) < p_defect)
#END CDIPlayerType
    def __repr__(self):
        return str(self.p_cdi)
    def __str__(self):
        return str(self.p_cdi)

#BEGIN SimplePlayer
class SimplePlayer(object):
    def __init__(self, playertype):
        self.playertype = playertype
        self.reset()
    def reset(self):
        self.games_played = list()
        self.players_played = list()
    def move(self, game):
        # delegate move to playertype
        return self.playertype.move(self, game)
    def record(self, game):
        self.games_played.append(game)
        opponent = game.opponents[self]
        self.players_played.append(opponent)
#END SimplePlayer

#Note: no selection_pressure class variable
#SoupPlayer extends SimplePlayer, which provides `move` via playertype.
#A SoupPlayer can imitate observed 'good' (i.e., high payoff) strategies.
#BEGIN:SoupPlayer;
class SoupPlayer(SimplePlayer):
    def roundPayoff(self) -> float:
        """Return *total* across game payoffs (not average payoff), where
        each game payoff is a mean across game iterations.
        """
        return sum(game.payoff()[self] for game in self.games_played)
    def choose_next_type(self) -> None:
        # Select a playertype(s) producing the highest score(s)
        best_playertypes = topscore_playertypes(self)
        # choose randomly from these best playertypes
        self.next_playertype = random.choice(best_playertypes)
    def evolve(self) -> None:
        self.playertype = self.next_playertype
#END:SoupPlayer;

def topscore_playertypes(player) -> List[CDIPlayerType]:
    """Return list of best (maximum payoff) player types."""
    best_types = [player.playertype]
    best_payoff = player.roundPayoff()
    for opponent in player.players_played:
        payoff = opponent.roundPayoff()
        if payoff > best_payoff:
            best_payoff = payoff
            best_types = [opponent.playertype]
        elif payoff == best_payoff:
            best_types.append(opponent.playertype)
    return best_types

#BEGIN GridPlayer
class GridPlayer(SoupPlayer):
    def set_grid(self, grid, row, column) -> None:
        self.grid = grid
        self.gridlocation = row, column
        self._neighbors = None #temporary initialization
    @property  #read-only attribute
    def neighbors(self) -> Sequence[SimplePlayer]:
        """This uses lazy evaluation so we can first populate a grid
        with players and later retrieve neighbors.
        """
        if self._neighbors is None: #memoize
            self._neighbors = grid.compute_neighbors(self)
        return self._neighbors
#END GridPlayer

#BEGIN MaxminGridPlayer
class MaxminGridPlayer(GridPlayer):
    def choose_next_type(self) -> None:
        # find playertype(s) with the highest minimum score
        best_playertypes = maxmin_playertypes(self)
        # choose randomly from these best playertypes
        self.next_playertype = random.choice(best_playertypes)
#END MaxminGridPlayer

#########################################################################
###################### End: Player Classes ##############################
#########################################################################

#########################################################################
###################### Begin: Spatial Classes ###########################
#########################################################################

############## very simple grid class
class Grid(object):
    def __init__(self, nrows: int, ncols: int, hoodOffsets):
        self.nrows, self.ncols = nrows, ncols
        self.hoodOffsets = hoodOffsets
        self.players2neighbors = dict() # will map players to neighbors
        # create 2d grid (each element is None until populated)
        self.players2d = [[None]*ncols for i in range(nrows)]
    def compute_neighbors(self, player):
        """Return neighbors of `player` on `self`."""
        player_row, player_col = player.gridlocation
        nrows, ncols = self.nrows, self.ncols
        players2d = self.players2d
        # initialize list of neighbors
        neighbors = list()
        # append all neighbors to list
        for offset in self.hoodOffsets -> List[SimplePlayer]:
            dc, dr = offset      #note: x,y hoodOffsets
            r = (player_row + dr) % nrows
            c = (player_col + dc) % ncols
            neighbor = players2d[r][c]
            neighbors.append(neighbor)
        return neighbors

#BEGIN SimpleTorus
class SimpleTorus(Grid):
    def populate(self, players1d) -> None:   # fill grid with players
        players = iter(players1d)
        # put a player in each grid location (row, column)
        for row in range(self.nrows):
            for column in range(self.ncols):
                player = players.next()
                self.players2d[row][column] = player
                player.set_grid(self, row, column)
    """
    def get_neighbors(self, player):
        if player in self.players2neighbors: # neighbors precomputed
            neighbors = self.players2neighbors[ player ]
        else:                        # neighbors not yet computed
            neighbors = self.compute_neighbors(player)
            # map player to computed neighbors (for later use)
            self.players2neighbors[ player ] = neighbors
        return neighbors
    """
#END SimpleTorus
#########################################################################
###################### End: Spatial Classes #############################
#########################################################################


#########################################################################
###################### BEGIN: Round Classes #############################
#########################################################################


class GameRound(object):
    """Provides an abstract class for a round.
    :note: subclasses must implement `run`
    """
    def __init__(self, players, payoffMatrix, gameIter=4):
        self.players = players
        self.payoffMatrix = payoffMatrix
        self.gameIter = gameIter
    def average_payoff(self) -> float:
        """Return average player payoff for the round.
        """
        players = self.players
        payoff = 0
        for player in players:
            payoff += player.roundPayoff()
        payoff /= len(players)
        return payoff
    def resetPlayers(self) -> None:
        for player in self.players:
            player.reset()   #clear games_played and players_played
    def run(self) -> None:
        raise NotImplementedError

#BEGIN:SoupRound;
class SoupRound(GameRound):
    """Provides a round runner that randomly pairs players and runs one game (4 iter) per pair.
    """
    def run(self):
        #Players record the game and the opponent (see game.run)
        payoffs = self.payoffMatrix
        for (player1, player2) in random_pairs_of(self.players):
            game = CDIGame(player1, player2, payoffs, gameIter=self.gameIter)
            game.run() #also -> players record game!!
#END:SoupRound;

#BEGIN GridRound
class GridRound(GameRound):
    """Provides a grid round for networked agents,
    where each player plays each of its neighbors once.
    """
    def run(self) -> None:  #
        paymat = self.payoffMatrix  #the 2x2x2 payoff matrix
        players = self.players
        for player in players:  #order is irrelevant; all pairs play before update
            for nbr in player.neighhbors:
                if nbr not in player.players_played:
                    game = CDIGame(player, nbr, paymat, gameIter=self.gameIter)
                    game.run() #also -> players record game!!
#END GridRound

#########################################################################
###################### END: Round Classes ###############################
#########################################################################


#############################################################
##################  utilities  ##############################
#############################################################
#BEGIN user_utils

def maxmin_playertypes(player):
    """Return list of best (maxmin payoff) player types."""
    # initialize mapping (playertypes -> payoffs)
    pt2po = dict()
    # find minimum payoff for each encountered playertype
    pt2po[ player.playertype ] = player.roundPayoff()
    for n in player.neighhbors:
        pt, po = n.playertype, n.roundPayoff()
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
    return zip(player_iter, player_iter)


def ptypeCounts(players):
    """Return map (playertype -> frequency) for `players`."""
    ptype_counts = defaultdict(int) #empty dictionary, default count is 0
    for player in players:
        ptype_counts[ player.playertype ] += 1
    return ptype_counts

#END user_utils
#############################################################


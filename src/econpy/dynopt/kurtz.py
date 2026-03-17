"""
This implements a finite-state optimal consumption model.
You can find a description of the model and another approach to solution
in John Stachurski's book *Economic Dynamics* (on p.104)
and in `John Stachurski's online notes`_.
We will call this version the Kurtz model,
in honor of Stachurski's supporting story.

:requires: Python 2.5+; NumPy 1.3+
:since: 2009-05-07
:contact: aisaac AT american DOT edu

.. _`John Stachurski's online notes`:
	http://johnstachurski.net/lectures/finite_growth.html
"""
import numpy as np 

class KurtzModel:
	def __init__(self):
		"""Return None.
		"""
		#parameters (initialized to the Stachurski example values)
		self.maxcapacity = 5
		self.maxbites = 10
		self.rho = 0.9 #discount factor
		#create the shock space
		self.shock_space_size = self.maxbites + 1
		self.shock_space = np.arange(self.shock_space_size, dtype=np.int64)
		self.pdf_shocks = self.pdf()
		#create the state space
		self.state_space_size = self.shock_space_size + self.maxcapacity
		self.state_space = np.arange(self.state_space_size, dtype=np.int64)
		#list to store history
		self.value_history = list()

	def pdf(self):
		"""Return array of float,
		the probability density (mass) function for the shock space
		(uniform distribution)."""
		return np.ones(self.shock_space_size) / self.shock_space_size

	def feasible_actions(self, state):
		"""Return array of int,
		representing the feasible actions.
		In the Kurtz model, the state is total fish
		(past frozen plus random new catch) and the
		action is (capacity constrained) amount frozen.
		"""
		constraint = min(state, self.maxcapacity)
		return np.arange(constraint+1, dtype=np.int64)

	def payoffs(self, state, v):
		"""Return array, the payoff for each feasible action.

		:param `state`: int, an index representing the state
		:param `v`: array, value of each future state
		"""
		acts = self.feasible_actions(state)
		current_values =  self.u(state - acts)  #utility for each act
		next_state = np.add.outer(acts, self.shock_space) #len(acts) by len(shock_space)
		future_values = np.dot(v[next_state], self.pdf_shocks)
		return current_values + self.rho * future_values

	def greedy(self, v):
		return list( self.payoffs(state, v).argmax() for state in self.state_space )

	def T(self, v):	  
		"""Return array, the iterated values.
		T is an implementation of the Bellman operator.

		:param `v`: array, function values on `state_space`
		"""
		values = ( self.payoffs(state, v).max() for state in self.state_space )
		Tv = np.fromiter(values, dtype=np.float64)
		return Tv

	def u(self, c):
		"""Return array of float,
		the 'utility' of each ci."""
		return np.sqrt(c)

	def value_iteration(self, v=None, tol=1e-5):
		"""Return None. Run the value iteration.
		"""
		T = self.T
		if v is None:
			#array of utilitys for a=0 (i.e., never store)
			v = self.u(self.state_space)
		history = list()
		history.append(v)
		vold = np.zeros_like(v)
		while (np.abs(v-vold).max()>tol):
			vold, v = v, T(v)
			history.append(v)
		self.value_history = history


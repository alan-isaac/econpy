"""
Provides a base collection of deterministic, *non-optimizing*
agents for macro simulations.

Does not include a usable "Economy" (or "World") class
(to run the simulation),
since these vary greatly by application.

:comment:
	Data structures influenced by a cohort focus.
	For example, an Indiv's age is just its Cohort's age.
:comment:
	Economy class is parameterized.
	An individual gets parameters from its cohort,
	a cohort gets parameters from its population,
	and a population gets parameters from its economy
	(or "world").
:requires: Python 2.5 now, but will move to Python 2.6

Transactor
	Basic mixin for agents conducting cash transactions.
Indiv(Transactor)
	Basic deterministic individual with demographic features.
Cohort
	Tuple of Indiv instances.
Population
	Deque of Cohort instance, with demographic methods.
Firm
	Basic firm (production unit).
Fund
	Basic account issuer.
FundAccount(Transactor)
	Basic account.
State(Transactor)
	Basic state for estate taxation.
Economy
	For illustrative purposes only.
EconomyParams
	Example of a parameters object.


:author: Alan G. Isaac
:license: `MIT license`_

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
"""
from __future__ import division
#from __future__ import absolute_import
__docformat__ = "restructuredtext en"
from collections import deque  #subclassed by Population

#logging
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')
agents_logger = logging.getLogger('agents_logger')
agents_logger.debug("Enter agents001.py.")

from ...pytrix.utilities import calc_gini

#################  module specific exceptions  ########################

class AbsError(Exception):
	"""Base class for exceptions in this module."""
	pass

class InsufficientFundsError(AbsError):
	"""Raised when payout exceeds net worth."""
	pass

class NegativeTransferError(AbsError):
	"""Raised when tranfer amount is negative."""
	pass


#####################  global functions  ###############################

def transfer(payer, payee, amount):  #TODO: cd introduce transactions cost here
	if amount < 0:
		raise NegativeTransferError("Transfers must be nonnegative.")
	payer.payout(amount)
	payee.payin(amount)


####################  BASIC AGENT CLASSES  #############################

class Lockable(object):
	"""Provide a mix-in enabling 'locking' a
	class so that no new attributes can be set.
	"""
	_attrlock = False
	def __setattr__(self, attr, val):
		agents_logger.debug("Enter __setattr__ with %s,%s"%(attr,val))
		"""Lock. (Allow no new attributes.)"""
		try:
			#get the class attribute if it exists
			p = getattr(type(self),attr)
			#if it's a descriptor, use it to set val
			p.__set__(self, val)
		except AttributeError:
			if hasattr(self, attr):
				self.__dict__[attr] = val 
			elif getattr(self, '_attrlock', False):
				raise AttributeError("Unlock to add new attributes.")
			else:
				self.__dict__[attr] = val 
	def lock_attributes(self):
		self._attrlock = True
	def unlock_attributes(self):
		self._attrlock = False


class Transactor(object):
	"""
	Provide a basic transactor mixin,
	with `payin` and `payout` methods,
	which increment or decrement
	the `_cash` instance attribute.
	:todo: ?accommodate multiple accounts?

	Attributes
	----------
	cash : float
		value of cash account
	networth : float
		value of all accounts
		(read only property)
	"""
	_cash = 0
	_accounts = ()
	def payin(self, amt):
		if amt < 0:
			raise NegativeTransferError()
		self._cash += amt
	def payout(self, amt):
		assert(amt >= 0)
		if self.networth < amt:
			raise InsufficientFundsError()
		else:
			self._cash -= amt

	@property
	def networth(self):
		result = self._cash
		for acct in self._accounts:
			result += acct.networth
		return result
	#cash property
	def get_cash(self):
		return self._cash
	def set_cash(self, val):
		self._cash = val
	cash = property(get_cash, set_cash)


class Indiv(Transactor):
	"""Provide a basic non-optimizing individual.

	Attributes
	----------
	age : int
		Age of indiv in cohorts.
		(Read only property.)
	params : object
		Model parameters provided by cohort.
		(Read only property.)
	cohort : Cohort
		Indiv's cohort. (Settable property.)
	spouse : Indiv
		The spouse or None.
	children : list
		Indiv's children, in order of "birth".
		(Read only property.)
	"""
	def __init__(self, sex=None):
		self._cohort = None
		self._params = None
		self._alive = True
		self._spouse = None
		self._children = list()  #list tracks birth order
		if sex:
			self.sex = sex
		self.parents = list() #*living* parents
		self.siblings = list()
		self.employers = set()
		self.contracts = dict(labor=[], capital=[])
	def __str__(self):
		return "%s with wealth %5.2f"%(self.sex,self.networth)
	@property
	def age(self):
		return self._cohort.age
	@property
	def params(self):
		if self._params is None:
			self._params = self.cohort.params
		return self._params
	#cohort property
	def get_cohort(self):
		return self._cohort
	def set_cohort(self, cohort):
		self._cohort = cohort
	cohort = property(get_cohort, set_cohort)
	@property
	def children(self):
		return self._children
	#spouse property
	def get_spouse(self):
		return self._spouse
	def set_spouse(self, other):
		agents_logger.debug("Enter Indiv.set_spouse")
		assert (self._spouse is None) , "no divorce, polygamy or polygony allowed"
		assert (self.sex is 'F' or other.sex is 'F'), "partial check, allowing MF or FF (unisex)"
		self._spouse = other
		if other.spouse:
			assert (other.spouse == self)
		else:
			other.spouse = self
		new_kids = other.children
		if new_kids:
			agents_logger.warn("New spouse already has kids.")
			self.adopt_children(new_kids)
		assert (self._spouse is other and other.spouse is self)
	spouse = property(get_spouse, set_spouse)
	def bear_children(self, sexes=None):
		"""Return list of this indiv's new kids.
		Used by Pop.append_new_cohort
		"""
		assert self.spouse, "for now, must be married (i.e., paired)"
		assert (self.sex == 'F')  #only women bear children
		# TODO: should KidClass use own class or set parametrically?
		KidClass = self.params.INDIVIDUAL
		new_kids = [KidClass(sex=s) for s in sexes]
		for kid in new_kids:
			"""mother's spouse is assumed to be a parent
			- these are *living* parents
			- use list: parent is removed when dead"""
			kid.parents = [self, self.spouse] #mother ("biological"), father
			self.adopt(kid)
			self.spouse.adopt(kid)
		#update siblings
		# each kid knows its siblings directly (not just via parents)
		# otherwise, info gone when parents die (and are removed from `parents`)
		for kid in self._children:
			new_siblings = list(new_kids)  #copy!
			if kid in new_siblings:
				new_siblings.remove(kid)
			kid.siblings.extend(new_siblings)
			assert (len(kid.siblings)==len(self._children)-1)
		return new_kids
	def adopt(self, kid): #used by bear_children
		"""Return: None:
		`adopt` just establishes parent-child relationship."""
		mykids = self._children
		assert (kid not in mykids)
		mykids.append(kid)
	def adopt_children(self, kids):
		"""Return: None.
		:see: `adopt` """
		for kid in kids:
			self.adopt(kid)
	def die(self):
		assert (self._alive is True)
		self._alive = False
		#inform kids
		# comment: w/o this, wd have references forever
		for k in self.children:
			k.parents.remove(self)
	def liquidate(self):
		"""Return: None.
		Pay estate tax; distribute estate; close out accounts.
		"""
		assert (self._alive is False)
		#tax estate if applicable
		try:
			state = self.economy.state
			state.tax_estate(self)
		except AttributeError:
			agents_logger.debug("Skipping estate taxation.")
		#distribute estate (e.g., to kids)
		self.distribute_estate()
		#close accounts
		assert abs(self.networth)<1e-5
		for acct in self._accounts:
			acct.close()  #acct asks its fund to close it
	def distribute_estate(self):
		"""Return None.
		Distribute estate upon death."""
		raise NotImplementedError
	def gift2kids(self,amt):
		"""Return: None.
		Distribute `amt` equally among one's kids."""
		assert (0 <= amt <= self.networth),\
		"Cannot distribute %s with wealth %s"%(amt,self.networth)
		kids = self._children()
		n = len(kids)
		for kid in kids:
			transfer(payer=self, payee=kid, amount=amt/n)
	def open_account(self, fund, amt=0):
		"""Return: None.

		:param fund: Fund object to open account with
		:param amt: initial deposit in new account
		"""
		acct = fund.create_account(self, amt=amt)
		self._accounts.append(acct)

class Fund(Transactor):
	"""Provide a basic financial institution.
	Often just for accounting (e.g., handling transfers)
	Currently only individuals should hold fund accounts.
	"""
	def __init__(self, account_type, economy):
		self.account_type = account_type
		self.economy = economy  #TODO: rethink
		self._accounts = list()
	def calc_accts_value(self):
		return sum( acct.networth for acct in self._accounts )
	def create_account(self, indiv, amt = 0):
		assert len(indiv._accounts)==0,\
		"num accts shd be 0 but is %d"%(len(self._accounts))
		acct = self.account_type(self, indiv, amt)
		self._accounts.append(acct)
		return acct
	def close_account(self,acct):
		self._accounts.remove(acct)
	def accept_contract(self, contract):
		self.contracts[contract.type].append(contract)
	def fulfill_contract(self, contract):
		if contract.type == 'capital':
			assert (contract.seller == self)
			result = self.calc_accts_value()  #this is the amt of capital to be rented
		else:
			raise ValueError("Unknown contract type.")
		return result
	def distribute_gains(self):
		raise NotImplementedError

class FundAccount(Transactor):
	"""Provide a basic security (account)."""
	def __init__(self, fund, indiv, amt=0):
		self.fund = fund
		self.owner = indiv
		self._cash = amt	#needed by Transactor
	def close(self):
		assert ( abs(self.networth) < 1e-9 ),\
			"Zero value required to close acct."
		self.fund.close_account(self)

class Cohort(tuple):
	"""Provide a basic cohort class.

	:note: user must override `marry`
	"""
	def __init__(self, seq):
		"""
		:note: tuple.__init__(self, seq) not needed bc tuples are immutable
		"""
		self._age = 0
		self._population = None
		self._params = None
		for indiv in self:
			indiv.cohort = self
		self.males = tuple(indiv for indiv in self if indiv.sex=='M')
		self.females = tuple(indiv for indiv in self if indiv.sex=='F')
		assert (len(self)==len(self.males)+len(self.females)),\
		"Every indiv must have a sex."
	@property
	def params(self):
		agents_logger.debug('get Cohort params') 
		if self._params is None:
			agents_logger.debug('get Cohort params from pop') 
			self._params = self.population.params
		return self._params
	#population property
	def get_population(self):
		return self._population
	def set_population(self, ppl):
		self._population = ppl
	population = property(get_population, set_population)
	#age property
	def get_age(self):
		"note: indiv age references cohort age"
		return self._age
	def set_age(self, age):
		self._age = age
	age = property(get_age, set_age)

class Population(deque):
	"""Provide a basic population,
	usually as a deque of `Cohort` instances.
	"""
	#economy property
	def get_economy(self):
		return self._economy
	def set_economy(self, val):
		if getattr(self, 'economy', None):
			raise ValueError('The economy should be set *once*.')
		self._economy = val
	economy = property(get_economy, set_economy)
	@property
	def params(self):
		#population gets params from economy
		if getattr(self,'_params',None) is None:
			agents_logger.info('get pop params from ec') 
			self._params = self.economy.params
		return self._params
	@property
	def size(self):
		return sum( len(cohort) for cohort in self )  #assumes cohort only contains living
	@property
	def individuals(self):
		"""Return generator: all individuals."""
		return (indiv for cohort in self for indiv in cohort)
	def get_wealth_distribution(self):
		"""Return float, summary statistic for the wealth distribution.
		This default looks at the distribution across
		*individuals*, not households. Override to change.
		"""
		return calc_gini( indiv.networth for indiv in self.individuals )
	def evolve(self):  #this will be called each "tick" of the economy
		"""Return None.  This is where all the work is done,
		in a way particular to each application.
		Usually relies on a collection of helper methods, such as:
		- get_new_cohort
		- remove_new_dead
		- finalize_dead
		- etc
		""" 
		raise NotImplementedError
	#############   HELPER METHODS FOR `evolve`  ####################
	def get_labor_force(self):
		raise NotImplementedError
	def increment_age(self):
		"""Return None. Increment population age."""
		for cohort in self:
			cohort.age += 1
	def get_new_cohort(self, kidsexgen=None):
		"""Return: COHORT instance.
		Called by evolve.
		"""
		agents_logger.debug(
			"enter Population.get_new_cohort.")
		#currently handle parthenogenic economies as all female and impose marriage  TODO
		#get list of new kids
		# Number and sexes determined by params.KIDSEXGEN
		parents = self.get_parents()
		kids = self.get_new_kids(parents, kidsexgen)
		#turn list into cohort
		kids = self.params.COHORT(kids)
		kids.population = self
		return kids
	def marry(self, prospects):  #TODO: rename
		"""Return None; marry off the prospects."""
		return NotImplemented
	def get_parents(self):
		"""Return sequence the new parents to be.
		(Just a helper method for get_new_cohort.)"""
		return NotImplemented
	def get_new_kids(self):
		"""Return sequence of Indiv instances,
		the new kids.
		Just a helper method for get_new_cohort."""
		return NotImplemented

class State(Transactor):
	"""Provide a basic state for estate taxation."""
	def __init__(self, economy):
		self.economy = economy
		self.params = economy.params
		self._cash = 0
	def tax_estate(self, indiv):
		assert (indiv._alive==False), "Tax estate only of dead."
		estate = indiv.networth
		if estate < -1e-5:
			agents_logger.warn("Individual has negative estate value.")
		tax = self.params.TAX_ESTATE(estate)
		#call module level `transfer` function  #is this best? (or having economy handle transfers?)
		transfer(payer=indiv, payee=self, amount=tax)

class Economy(object):
	"""Provides a controller for the simulation.
	A rough example:  Do not use as is!"""
	def __init__(self, params):
		self.params = params
		self.history = list()  #to record state from each period
		self.funds = list()
		self.state = params.STATE(self)
		self.population = self.get_initial_population()
	def run():
		"""Return None. Run the simulation."""
		raise NotImplementedError
	### helper methods for initialization ###
	def get_initial_population(self):
		"""Return Population instance.
		Create initial population,
		establish any initial familial relations,
		and impose any initial wealth distribution.
		"""
		raise NotImplementedError()
	### helper methods for run ###
	def distribute_gains(self):
		for fund in self.funds:
			fund.distribute_gains()

class EconomyParams(object): #default params, needs work
	"""This is just a rough example of one way to group
	parameters together in a class.  Not usable without
	overriding `__init__`!
	"""
	FUND = Fund
	FUNDACCOUNT = FundAccount
	STATE = State
	INDIVIDUAL = Indiv
	COHORT = Cohort
	POPULATION = Population
	MAX_KIDS = 2
	SEED = None
	DEBUG = False
	def __init__(self):
		if self.SEED:
			self.RNG = random.Random(self.SEED)
		#set class to use in Economy construction
		#self.FIRM = FirmKN
		#list life periods Indivs work (e.g., range(16,66))
		self.WORKING_AGES = list()
		self.LABORMARKET = None
		#default is individual based Gini
		#TODO: household or indiv distributions? (household might be better)
		self.SHUFFLE_NEW_W = False
		self.MSHARE = 0.5
		################################################
		#### ALWAYS provide new values for the following
		################################################
		self.N_YEARS = 0
		self.TAX_ESTATE = None
		self.BEQUEST_TYPE = None        #e.g., child-directed, or random
		self.MATING = None
		#sex generator for new births
		self.KIDSEXGEN = None
		#number of Cohorts
		self.N_COHORTS = 0
		self.COHORT_SIZE = 0
		#number of Firms
		self.N_FIRMS = 0
		#initial Gini for Wealth
		self.GW0 = 0
		self.WEALTH_INIT = 0
		#Life Events  (MUST OVERRIDE)
		# AGE4KIDS is how old you are when you kids APPEAR in the economy (you may be dead)
		self.AGE4KIDS = 0   #NOTE: no cohort has age 0!
		self.AGE4MARRIAGE = 0   #NOTE: no cohort has age 0!
	def compute_ability(self, indiv):
		return 1


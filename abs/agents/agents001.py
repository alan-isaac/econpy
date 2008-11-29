"""
Provides a base collection of deterministic, non-optimizing
agents for macro simulations.  Does not include a "World"
or "Economy" class to run the simulation, since these vary
too greatly by application.

Indiv
	- Data: alive, sex, age, parents, siblings, spouse, _children, _accounts,
	employers, economy, state, contracts, _cash
	- Methdods:
	  payin, payout, get_worth, calc_household_wealth, wed,
	  bear_children, adopt_children, get_children, adopt, open_account,
	  gift2kids, liquidate, distribute_estate, labor_supply, accept_contract,
	  fulfill_contract, 

Cohort
	- Data: _age, males, females
	- Methdods: marry, set_age, increment_age

PestieauCohort(Cohort)
	- NewData: _lock
	- NewMethdods:
	- Override: marry

Population
	- Data:
	- Methdods:

Firm
	- Data:
	- Methdods:

Fund
	- Data:
	- Methdods:

FundAcct
	- Data: fund, owner, _value
	- Methdods: payin, payout, close, transferto

State
	- Data:
	- Methdods:


:copyright: Alan G. Isaac, except where another author is specified.
:license: `MIT license`_

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
"""
from __future__ import division
#from __future__ import absolute_import
__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'
__lastmodified__ = '2008-11-29'

def transfer(payer, payee, amount):  #TODO: cd introduce transactions cost here, cd be a fn
	payer.payout(amount)
	payee.payin(amount)

class AbsError(Exception):
	"""Base class for exceptions in this module."""
	pass

class InsufficientFundsError(AbsError):
	"""Raised when payout exceeds net worth."""
	pass

class TransactorMI(object):
	"""
	Provides `payin` and `payout` methods.
	Requires a `_cash` attribute.
	"""
	_cash = 0
	_accounts = ()
	def payin(self, amt):
		assert(amt >= 0)  #this is just sign checking; TODO: move to transaction
		self._cash += amt
	def payout(self, amt):  #redundant; just for ease of reading and sign check
		assert(amt >= 0)
		if self.get_worth() < amt:
			raise InsufficientFundsError
		else:
			self._cash -= amt   #TODO: accommodate multiple accounts
	def get_worth(self):
		result = self._cash
		for acct in self._accounts:
			result += acct.get_worth()
		return result

class Indiv(TransactorMI):
	def __init__(self, sex=None, economy=None):
		if sex:
			self.sex = sex
		if economy:
			self.economy = economy
			self.state = economy.state
		self.alive = True
		self.age = 0
		self.parents = None
		self.siblings = list()
		self.spouse = None
		self._children = list()  #use list to track birth order
		self._cash = 0
		self._accounts = list()  #accounts[0] is the cash acct
		self.employers = set()
		self.contracts = dict(labor=[], capital=[])
		self._locked = True
	def __setattr__(self, attr, val):
		"""Lock. (Allow no new attributes.)"""
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val 
	def get_children(self):
		return self._children
	def wed(self, other): #may be better to have state perform marriage? TODO
		assert (self.spouse==None) , "no polygamy or polygony allowed"
		assert (self.sex is 'F' or other.sex is 'F'), "partial check, allwoing MF or FF (unisex)"
		self.spouse = other
		if other.spouse:
			assert (other.spouse == self)
		else:
			other.wed(self)
		newkids = other.get_children()
		if newkids:
			script_logger.warn("New spouse already has kids.")
			self.adopt_children(newkids)
	def adopt(self,child): #used by bear_children
		mykids = self._children
		assert (child not in mykids)
		mykids.append(child)
	def adopt_children(self, kids):
		for kid in kids:
			self.adopt(kid)
	def bear_children(self, sexes=None):
		"""Return list of this Indiv's new kids.
		Used by Pop.append_new_cohort
		"""
		assert self.spouse, "must be married"
		assert (self.sex == 'F')  #only women can bear children
		#need `newkids` to be a sequence
		newkids = [self.__class__(sex=s,economy=self.economy) for s in sexes]
		for kid in newkids:
			#mother's spouse is assumed to be biological parent
			kid.parents = (self.spouse, self) #father,mother (biological)
			self.adopt(kid)
			self.spouse.adopt(kid)  #TODO: but maybe a child shd be born to a household???
		#each kid will know its siblings directly (not just via parents) chk
		my_kids = self._children
		for kid in my_kids:
			for sib in my_kids:
				if sib not in kid.siblings:
					kid.siblings.append(sib)
			#kid.siblings.update(my_kids) #TODO: better approaches?
		return newkids
	def open_account(self, fund, amt=0):
		"""Return: None.

		:param fund: Fund object to open account with
		:param amt: initial deposit in new account
		"""
		assert (len(self._accounts) == 0) #TODO: eventually allow multiple accounts
		acct = fund.create_account(self, amt=amt)
		self._accounts.append(acct)

class Fund(TransactorMI):
	"""Basic financial institution.
	Often just for accounting (e.g., handling transfers)
	Currently only individuals should hold fund accounts.
	"""
	def __init__(self, account_type, economy):
		self.account_type = account_type
		self.economy = economy  #TODO: rethink
		self._accounts = list()
		self._locked = True
	def __setattr__(self, attr, val):
		"""Lock. (Allow no new attributes.)"""
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val 
	def calc_accts_value(self):
		return sum( acct.get_worth() for acct in self._accounts )
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

class FundAccount(TransactorMI):
	def __init__(self, fund, indiv, amt=0):
		self.fund = fund
		self.owner = indiv
		self._cash = amt	#needed by TransactorMI
		self._locked = True
	def __setattr__(self, attr, val):
		"""Lock. (Allow no new attributes.)"""
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val 
	def close(self):
		assert (-1e-9 < self.get_worth() < 1e-9),\
		"Zero value required to close acct."
		self.fund.close_account(self)

class Cohort(tuple):
	"""Basic cohort class.

	:note: must override `marry`
	"""
	def __init__(self, seq):
		"""
		:note: tuple.__init__(self, seq) not needed bc tuples are immutable
		"""
		self._age = 0
		self.males = tuple(indiv for indiv in self if indiv.sex=='M')
		self.females = tuple(indiv for indiv in self if indiv.sex=='F')
		assert (len(self)==len(self.males)+len(self.females)),\
		"Every indiv must have a sex."
		self._locked = True
	def __setattr__(self, attr, val):
		"""Lock. (Allow no new attributes.)"""
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val
	def set_age(self,age):
		self._age = age
		for indiv in self:
			indiv.age = age
	def get_age(self):
		return self._age
	def increment_age(self):
		assert (indiv.age == self._age for indiv in self),\
		"indiv age shd not diverge from cohort age"
		self._age += 1
		for indiv in self:
			indiv.age += 1
	def marry(self,mating):  #TODO: rename
		raise NotImplementedError
	def have_kids(self,mating):  #TODO: rename
		raise NotImplementedError

class Population(list):  #provide a list of Cohort tuples
	def evolve(self):  #this will be called each "tick" of the economy
		raise NotImplementedError
	def have_kids(self):
		raise NotImplementedError
	def initialize_kids(self):
		raise NotImplementedError
	def get_labor_force(self):
		raise NotImplementedError
	def get_size(self):
		return sum( len(cohort) for cohort in self )  #assumes cohort only contains living
	def get_new_dead(self):
		"""Return: new_dead (sequence)
		Removes dead from population, sets alive=False, and returns them as sequence.
		"""
		dead = self.pop(0)                     #remove dead cohort from population
		for indiv in dead:  #do this first! (so that estates do not get distributed to dead)
			assert (indiv.alive == True) #just an error check
			indiv.alive = False
		return dead
	def age_ppl(self):
		for cohort in self:
			cohort.increment_age()
	def marry(self):
		"""Return: None.
		"""
		params = self.economy.params
		newlyweds = self[params.AGE4MARRIAGE-1] #Marry within one cohort.  TODO: change this eventually.
		for indiv in newlyweds:
			assert (indiv.spouse is None)
		newlyweds.marry(params.MATING)  #TODO: change to a Pop method??
	def get_new_cohort(self, parents):
		"""Return: COHORT
		Called by evolve.
		Number and sexes determined by params.KIDSEXGEN
		"""
		cohort_type = self[0].__class__
		params = self.economy.params
		#currently handle parthenogenic economies as all female and impose marriage  TODO
		kids = self.have_kids(parents)
		self.initialize_kids( kids )
		return cohort_type( kids )
	def get_indivs(self):
		"""Return list: all individuals."""
		return [indiv for cohort in self for indiv in cohort]
	def gen_indivs(self):
		"""Return generator: all individuals."""
		return (indiv for cohort in self for indiv in cohort)
	def gen_new_mothers(self):
		params = self.economy.params
		# AGE4KIDS -1 (for index: nobody in economy has age 0) -1 (this is conception, not birth)
		new_parents = self[params.AGE4KIDS-2]  #currently restricted to a single cohort TODO
		script_logger.debug( "Number of new parents: %d"%(len(new_parents)) )
		#only married females can have kids
		return ( indiv for indiv in new_parents if (indiv.spouse and indiv.sex=='F') )
	def calc_dist(self):
		params = self.params
		#return calc_gini( indiv.get_worth() for indiv in self.gen_indivs() )
		return  params.calc_dist(self)

class State(TransactorMI):
	def __init__(self, economy):
		self.economy = economy
		self.params = economy.params
		self._cash = 0
		self._locked = True
	def __setattr__(self, attr, val):
		"""Lock. (Allow no new attributes.)"""
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val
	def tax_estate(self, indiv):
		estate = indiv.get_worth()
		tax = self.params.ESTATE_TAX(estate)
		#call module level `transfer` function  #is this best? (or having economy handle transfers?)
		transfer(payer=indiv, payee=self, amount=tax)

class EconomyParams(object): #default params, needs work
	"""This is just a simple example of one way to group
	parameters together in a class.
	"""
	def __init__(self):
		self.DEBUG = False
		#set class to use in Economy construction
		self.FUND = Fund
		self.FUNDACCOUNT = FundAccount
		self.STATE = State
		self.INDIV = Indiv
		self.COHORT = Cohort
		self.Population = Population
		self.LABORMARKET = None
		#self.FIRM = FirmKN
		#list life periods Indivs work (e.g., range(16,66))
		self.WORKING_AGES = list()
		self.SEED = None
		#default is individual based Gini
		#TODO: household or indiv distributions? (household might be better)
		self.SHUFFLE_NEW_W = False
		self.MSHARE = 0.5
		self.FSHARE = 0.5
		#### ALWAYS provide new values for the following
		self.N_YEARS = 0
		self.ESTATE_TAX = None
		self.BEQUEST_TYPE = None
		self.BEQUEST_FN = None
		self.MATING = None
		#sex generator for new births
		self.KIDSEXGEN = None
		#number of Cohorts
		self.N_COHORTS = 0
		#number of Firms
		self.N_FIRMS = 0
		#initial Gini for Wealth
		self.GW0 = 0
		self.WEALTH_INIT = 0
		self.COHORT_SIZE = 0
		#Life Events  (MUST OVERRIDE)
		# AGE4KIDS is how old you are when you kids APPEAR in the economy (you may be dead)
		self.AGE4KIDS = 0   #NOTE: no cohort has age 0!
		self.AGE4MARRIAGE = 0   #NOTE: no cohort has age 0!
	def compute_ability(self, indiv):
		return 1


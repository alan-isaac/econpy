'''
Provides a collection of agents for replication of Pestieau (1984 OEP).

Indiv
	- Data: alive, sex, age, parents_bio, siblings, spouse, children, accounts,
	employers, economy, state, 
	- Methdods: receive_income, outgo, calc_wealth, calc_household_wealth, wed,
	bear_children, adopt, open_account, gift2kids, liquidate,
	distribute_estate, 

Cohort
	- Data: _cohort_age, males, females
	- Methdods: get_married, set_age, age_cohort

PestieauCohort(Cohort)
	- NewData: _lock
	- NewMethdods:
	- Override: get_married

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
	- Methdods: deposit, withdraw, close, transferto

State
	- Data:
	- Methdods:


:copyright: Alan G. Isaac, except where another author is specified.
:license: `MIT license`_

.. _`MIT license`: http://www.opensource.org/licenses/mit-license.php
'''
from __future__ import division
from __future__ import absolute_import

__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'
__lastmodified__ = '20070622'





class Indiv(object):
	def __init__(self, economy=None, sex=None):
		if economy:
			self.economy = economy
			self.state = economy.state
			self.ability = economy.params.compute_ability(self)
		self.alive = True
		self.sex = sex
		self.age = 0
		self.parents_bio = None
		self.siblings = set()
		self.spouse = None
		self.children = set()
		self.accounts = list()  #accounts[0] is the cash acct
		self.employers = set()
		self._locked = True
	def __setattr__(self, attr, val):
		'''Override __setattr__:
		no new attributes allowed after initialization.
		'''
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val 
	def receive_income(self, amt):
		assert(amt >= 0)  #this is just sign checking
		self.accounts[0].deposit(amt)
	def outgo(self, amt):  #redundant; just for ease of reading and sign check
		assert(amt >= 0)
		self.accounts[0].withdraw(amt)
	def calc_wealth(self):
		wealth = 0
		for acct in self.accounts:
			wealth += acct.value
		return wealth
	def calc_household_wealth(self):  #just self and spouse (but cd add def of household as any set!)
		wealth = self.calc_wealth()
		if self.spouse:
			wealth += self.spouse.calc_wealth()
		return wealth
	def wed(self, other): #may be better to have state perform marriage? TODO
		assert (self.spouse==None) , "no remarriage allowed"
		assert set([self.sex,other.sex])==set(['M','F']) #define reproductive union
		self.spouse = other
		if other.spouse:
			assert (other.spouse == self)
		else:
			other.wed(self)
		self.children.update(other.children)
	def bear_children(self, sexes=None):
		'''Return this Indiv's kids
		Used by Pop.produce_new_cohort
		'''
		assert self.spouse  #must be married ...
		assert (self.sex == 'F')  #only women can bear children
		newkids = [self.__class__(economy=self.economy,sex=s) for s in sexes]
		for kid in newkids:
			kid.parents_bio = (self.spouse, self) #father,mother
			self.adopt(kid)
			self.spouse.adopt(kid)  #TODO: but maybe a child is born to a household???
		for kid in self.children:
			kid.siblings.update(self.children)
		assert (len(self.children)==2) #TODO: will need to get rid of constraint
		return newkids
	def adopt(self,child): #used by bear_children
		self.children.add(child)
		assert (len(self.children) <= 2) #TODO: get rid of constraint
	def open_account(self, fund, amt=0):
		assert (len(self.accounts) == 0) #TODO: allow multiple accounts
		acct = fund.create_account(self, amt=amt)
		self.accounts.append(acct)
	def gift2kids(self,amt):
		assert (0 <= amt <= self.calc_wealth()), "amt: %s\t w:%s"%(amt,self.calc_wealth())
		checking = self.accounts[0]
		kids = self.children
		n = len(kids)
		for kid in kids:
			checking.transferto(kid, amt/n)
	def liquidate(self):
		assert (self.alive is False)
		acct = self.accounts[0] #transactions acct
		self.state.tax_estate(self)
		self.distribute_estate()
		#close accounts
		assert abs(self.calc_wealth())<1e-5
		for acct in self.accounts:
			acct.close()  #acct asks its fund to close it
	def distribute_estate(self):
		assert (self.alive is False)
		self.economy.params.BEQUEST_FN(self)

#20 Indiv per Cohort
class Cohort(tuple):
	'''Basic cohort class.

	:note: must override get_married
	'''
	def __init__(self):
		'''
		:note: tuple.__init__(seq) not needed bc tuples are immutable
		'''
		self._cohort_age = 0
		self.males = tuple(indiv for indiv in self if indiv.sex=='M')
		self.females = tuple(indiv for indiv in self if indiv.sex=='F')
		assert (len(self)==len(self.males)+len(self.females)),\
		"Every indiv must have a sex."
	def set_age(self,age):
		self._cohort_age = age
		for indiv in self:
			indiv.age = age
	def age_cohort(self):
		assert (indiv.age == self._cohort_age for indiv in self),\
		"indiv age shd not diverge from cohort age"
		self._cohort_age += 1
		for indiv in self:
			indiv.age += 1
	def get_married(self,mating):  #TODO: rename
		return NotImplemented

class PestieauCohort(Cohort):
	'''Cohort class for Pestieau 1984 replication.
	'''
	def __init__(self,seq):
		Cohort.__init__(self)
		self._locked = True  #see: __setattr__
	def __setattr__(self, attr, val):
		'''Override __setattr__:
		no new attributes allowed after initialization.
		'''
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val
	def get_married(self,mating):	#TODO: move into Pop when marry across Cohorts
		males = list(self.males)
		females = list(self.females)
		maxkids = 2 #TODO: parameterize
		#sort males and females by wealth
		males.sort(key=lambda i: i.calc_wealth(),reverse=True)
		females.sort(key=lambda i: i.calc_wealth(),reverse=True)
		#class mating when cannot marry sibs
		if mating == "class_nosibs":
			#print "class mating, no sibs"
			#first make matches while it is certainly possible that remainder can be matched
			while len(males)>maxkids and len(females)>maxkids:
				groom = males.pop(0)
				for bride in females:
					if bride not in groom.siblings:
						break
				females.remove(bride)
				bride.wed(groom) 
			#second make remaining possible matches
			assert (len(males)==maxkids or len(females)==maxkids)
			mf = zip(males,females)
			#if any matches forbidden, find permissible matches
			if sum( m in f.siblings for (m,f) in mf ):
				mf = match_exclude(males,females, lambda x,y: x in y.siblings)
			for groom,bride in mf:
				bride.wed(groom)
		elif mating == "classonly":
			#print "classonly mating"
			for m,f in itertools.izip(males,females): #some poor possibly left out
				f.wed(m)
			params = m.economy.params
			if params.DEBUG:
				mates = itertools.izip(males,females) #some poor possibly left out
				for m,f in mates:
					print m.calc_wealth(), f.calc_wealth(), m.calc_household_wealth()
		elif mating == "random":
			#print "Random mating"
			if len(males) > len(females): #-> wealth doesn't change likelihood of marriage
				random.shuffle(males)
			else:
				random.shuffle(females)
			mates = itertools.izip(males,females)
			for m,f in mates:
				f.wed(m)
		else:
			assert (mating is None),\
			"%s is an unknown mating type"%(mating)


class Fund(object):
	'''Basic financial institution.
	Often just for accounting (e.g., handling transfers)
	'''
	def __init__(self,economy):
		self.economy = economy  #TODO: rethink
		#self.rBAR = economy.rBAR
		#self.rSD = economy.rSD
		self._accounts = list() #empty list
		#self.max_return = 0  #debugging only
		#self.n_distributions = 0  #debugging only
		#self.n_0distributions = 0  #debugging only
		self._locked = True
	def __setattr__(self, attr, val):
		'''Override __setattr__:
		no new attributes allowed after initialization.
		'''
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val 
	def calc_accts_value(self):
		return sum( acct.value for acct in self._accounts )
	def create_account(self, indiv, amt = 0):
		assert len(indiv.accounts)==0,\
		"num accts shd be 0 but is %d"%(len(self._accounts))
		acct = FundAcct(self, indiv, amt)
		self._accounts.append(acct)
		return acct
	def close_account(self,acct):
		self._accounts.remove(acct)

class FundAcct(object):
	def __init__(self, fund, indiv, amt=0):
		self.fund = fund
		self.owner = indiv
		self._value = amt
		self._locked = True
	def __setattr__(self, attr, val):
		'''Override __setattr__:
		no new attributes allowed after initialization.
		'''
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val 
	def deposit(self, amt):
		assert(amt >= 0)
		self._value += amt
	def withdraw(self, amt): #redundant; just for convenience and error checking
		assert(amt >= 0)
		self._value -= amt
	def close(self):
		assert (-1e-9 < self._value < 1e-9),\
		"Zero value required to close acct."
		self.fund.close_account(self)
	def transferto(self, recipient, amt):  #ugly; have the fund make transfer?
		assert (0 <= amt)
		if (amt > 0):
			assert (amt <= self.owner.calc_wealth()+1e-9)
			toacct = recipient.accounts[0]
			self.withdraw(amt)
			toacct.deposit(amt)
		
class State(object):
	def __init__(self,economy):
		self.economy = economy
		self.params = economy.params
		self.net_worth = 0
		self._locked = True
	def __setattr__(self, attr, val):
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val
	def tax_estate(self,indiv):
		estate = indiv.calc_wealth()
		tax = self.params.ESTATE_TAX(estate)
		self.economy.transfer(indiv, self, tax)  #is this best (having economy handle transfers?)
	def income(self, amt):
		self.net_worth += amt  #TODO: cd parameterize an inefficiency here
	def outgo(self, amt):
		self.net_worth -= amt
	def distribute_estates(self,dead): #move details to Indiv? to State? to Economy? TODO
		if self.economy.BEQUEST_TYPE == 'child_directed':
			for indiv in dead:
				n_children = len(indiv.children)
				bequest_size = indiv.calc_wealth()/n_children #equal bequests
				for kid in indiv.children:
					self.economy.transfer(indiv, kid, bequest_size)
		else:
			raise ValueError("must specify BEQUEST_TYPE")
		#close accounts of the dead
		for indiv in dead:
			assert len(indiv.accounts)==1,\
			"num accts shd be 1 but is %d"%(len(indiv.accounts)) #single acct only for now!?
			for acct in indiv.accounts:
				acct.fund.accounts.remove(acct)
	

class IterativeProcess(object):
	'''General description of iterative process.

	Requires an iterator and a criterion.
	Iterator must have `initialize` and `iterate` methods.
	Criterion must be callable;
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
		iterator.initialize()  #is this redundant to the __init__ method?
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

class Economy(object):
	'''
	Not Implemented.
	'''
	def initialize(self):
		pass
	def iterate(self):
		pass
		


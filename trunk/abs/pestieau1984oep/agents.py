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



Notes:
theoretical model and simulation model not a perfect match
	theory model: parthenogenic
	bequests: theory bop vs simulation eop (p.412)?
Pestieua p.408
	individual t lives 2 periods, t and t+1
		works first period
		leaves bequest at **beginning** of 2nd period
			(effectively, inter vivos transfers)
		picks ct knowing:
			bt and wt at **and**
			rt (but use r@t-1 for simulation!!!) p. 412
			number of kids he'll have!!
			BUT: uncertain of kids abilities.  (Expects same ability; not RE!)
Pestieau p.412
	consider class marriage and random marriage
	allow income class differences in fertility
	allow couple to be childless. (conflict with ability formula?)
	start simulation with 100 indivs and "arbitrary" distribution of wealth (K)
	production fn is CD
	full employment, competitive factor mkts
	**household** decision making (umax)
	use **average** parent ability
Pestieau p.413
	run simulation for 30 periods
	measure inequality with Gini
	simulation parameters in tables p.413 ff
'''

from __future__ import division
from __future__ import absolute_import
import random

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
		self.accounts[0].deposit(amt)  #KC: deposit is a method in the FundAcct class 
	def outgo(self, amt):  #redundant; just for ease of reading and sign check
		assert(amt >= 0)
		self.accounts[0].withdraw(amt)  # KC: withdraw is a method in the FundAcct class
	def calc_wealth(self):
		wealth = 0
		for acct in self.accounts:
			wealth += acct.get_value()
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
		acct = fund.create_account(self, amt=amt)  #KC: create_account is a method in the Fund class
		self.accounts.append(acct)
	def gift2kids(self,amt):
		assert (0 <= amt <= self.calc_wealth()), "amt: %s\t w:%s"%(amt,self.calc_wealth())
		checking = self.accounts[0]  ## KC: "checking" for checking account
		kids = self.children
		n = len(kids)
		for kid in kids:
			checking.transferto(kid, amt/n)
	def liquidate(self):
		assert (self.alive is False)
		acct = self.accounts[0] #transactions acct
		self.state.tax_estate(self)  #KC: tax_estate is a method in the State class
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
	def __init__(self, seq):
		'''
		:note: tuple.__init__(self, seq) not needed bc tuples are immutable
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
	def __init__(self, seq):
		Cohort.__init__(self, seq)
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
	def get_value(self):
		return self._value


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

class Population(list):  #provide a list of Cohort tuples
	def evolve(self):  #this will be called each "tick" of the economy
		'''Return: None.
		'''
		params = self.economy.params  #associated economy have been set by economy...
		parents = self.get_new_parents() #TODO: parents are currently a Cohort; eventually change this
		parents.get_married(params.MATING)  #TODO: change to a Pop method??
		self.produce_new_cohort(parents, kidsexgen=params.KIDSEXGEN) #new cohort has age 0
		self.age_ppl()                         #->new cohort has age 1
		dead = self.get_new_dead()
		assert(dead._cohort_age == self.params.N_COHORTS+1) #TODO only works for non-stochastic deaths
		for indiv in dead:
			indiv.liquidate()  #close out all accounts
	def get_new_dead(self): #removes dead from population and returns as sequence
		dead = self.pop(0)                     #remove dead cohort from population
		for indiv in dead:  #do this first! (so that estates do not get distributed to dead)
			assert (indiv.alive == True) #just an error check
			indiv.alive = False
		return dead
	def age_ppl(self):
		for cohort in self:
			cohort.age_cohort()
	def get_new_parents(self):
		'''Return a cohort.  TODO: change this eventually.
		'''
		params = self.economy.params
		return self[params.KID_AT_YEAR-1]  #params assigned by economy! TODO  recheck timing
	def produce_new_cohort(self, parents, kidsexgen=None):
		'''Return a list (`new_cohort`) of same size as current cohort.
		Called by produce_new_cohort.
		Current model: two children, MF, at fixed age.
		'''
		params = self.economy.params
		kids = list()
		mothers = [indiv for indiv in parents if (indiv.spouse and indiv.sex=='F')]
		getsexes = kidsexgen(mothers)  #returns an iterator
		#each mother has kids of specified sexes (e.g., "MF")
		for indiv in mothers:
			newsexes = getsexes.next()  #TODO: remove restriction to 2 simultaneous kids!!
			kids.extend(indiv.bear_children(sexes=newsexes))
		for kid in kids:
			kid.open_account(self.economy.funds[0])  #provide every kid with an acct
		self.initialize_wealth(kids)
		new_cohort = Cohort(kids)
		self.append( new_cohort )
		return new_cohort  #TODO: do I need this return?
	def calc_dist(self): #TODO: calc distribution over **indivs** or households??
		params = self.economy.params
		#return calc_gini( indiv.calc_wealth() for indiv in self.gf_indivs() )
		return  params.calc_dist(self)
	def get_indivs(self): #return all individuals as single list
		return [indiv for cohort in self for indiv in cohort]
	def gf_indivs(self): #return all individuals as single generator
		return (indiv for cohort in self for indiv in cohort)
	def initialize_wealth(self, kids):
		return NotImplemented

class Economy(object):
	'''
	Not Implemented.
	'''
	def initialize(self):
		pass
	def iterate(self):
		pass
		

###################
class PestieauParams:
	def __init__(self):
		self.DEBUG = False
		self.ESTATE_TAX = None
		self.BEQUEST_TYPE == 'child_directed'
		self.MATING = None
		self.KIDSEXGEN = None
		self.N_COHORTS = None
		self.KID_AT_YEAR =  None
		self.PESTIEAU_BETA = None
		self.PESTIEAU_NBAR = None

def compute_ability(indiv, beta, nbar):
	'''Return: float (child's ability).
	Formula taken from Pestieau 1984, p.407.

	:Parameters:
	  beta : float
	    Pestieau's ability regression parameter
	  nbar : float
	    Pestieau's mean number of kids 
	'''
	#determine ability from biological parents, if possible
	assert (0 < beta < 1) 	#Pestieu p. 407
	try:
		father, mother = indiv.parents_bio
		assert (father.sex == 'M' and mother.sex == 'F') #just an error check
		nsibs = len(mother.children)
		assert (nsibs>0)    #Pestieau p.407
		parents_ability = (father.ability + mother.ability)/2.0  #Pestieau p.412
		z = random.normalvariate(0.0,0.15)  #Pestieau p.413-414
		#Pestieau formula does not allow for zero kids??
		ability = beta*parents_ability + (1-beta)*nbar/nsibs + z #Pestieau p.407 (role of nbar is weird)
	except TypeError:  #if indiv.parents_bio is None
		ability = random.normalvariate(1.0,0.15) #for initial cohort
	return ability


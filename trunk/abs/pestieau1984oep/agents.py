'''
Provides a collection of agents for replication of Pestieau (1984 OEP).

Indiv
	- Data: alive, sex, age, parents_bio, siblings, spouse, _children, accounts,
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
from __future__ import division
from __future__ import absolute_import


'''
from __future__ import division
from __future__ import absolute_import
__docformat__ = "restructuredtext en"
__author__ = 'Alan G. Isaac (and others as specified)'
__lastmodified__ = '20070622'

import random, itertools
from econpy.pytrix import utilities

#logging
import logging
script_logger = logging.getLogger('script_logger')


#################################################################
#########################  functions  ###########################
#################################################################
def distribute(wtotal, units, gini, shuffle=False):
	units = set(units)
	units2 = list(units) 
	g = (1+gini)/(1-gini) # (2A+B)/B
	nb = len(units)  #number of brackets 
	shares = utilities.gini2shares(gini, nb, shuffle=shuffle)
	w = ( wtotal*share for share in shares )
	for wi in w:
		units.pop().receive_income(wi)   #ADD to individual wealth
	assert (not units),  "Length shd now be zero."
	script_logger.debug( "Desired gini: %4.2f,  Achieved Gini: %4.2f"%( gini,utilities.calc_gini( i.calc_wealth() for i in units2 )))
	print "Desired gini: %4.2f,  Achieved Gini: %4.2f"%( gini,utilities.calc_gini( i.calc_wealth() for i in units2 )) 
def sexer_randompairs(n):
	'''Yields n of each of two sexes, in pairs, in random order.
	Assumes from __future__ import division.
	'''
	sexgen = utilities.n_each_rand(n,itemtuple="MF")
	while True:
		yield sexgen.next() + sexgen.next()

#used as BEQUEST_FN by Indiv instances
def bequests_pestieau(indiv, neg_ok=True):
	'''
	Simplest bequest function for equal division among all kids.
	Assumes spouse alive, all kids alive.  (E.g., OG model.)

	:Parameters:
	  indiv : Indiv
	    an individual instance whose wealth to distribute
	  neg_ok : bool
	    True if negative bequests allowed
	'''
	kids = indiv.get_children()  #:note: check that alive?
	assert all(kids.count(kid)==1 for kid in kids)
	each_gets = indiv.calc_wealth()/len(kids)  #equal bequests p.412
	#script_logger.debug("Bequest size: %10.2f"%(each_gets))
	cash_account = indiv.accounts[0]
	if (each_gets >= 0 or neg_ok):
		for kid in kids:
			cash_account.transferto(kid, each_gets)
	else:
		raise ValueError("negative beqests forbidden")

#not currently used by for Pestieau experiments
#can be used as BEQUEST_FN by Indiv instances
def bequests_blinder(indiv):
	'''Bequest function for the Blinder model, generalized.
	Blinder version: 2 kids, M & F, male gets MSHARE.
	'''
	params = indiv.economy.params
	estate_aftertax = indiv.calc_wealth()
	account = indiv.accounts[0]  #the cash acct
	spouse = indiv.spouse
	if spouse.alive:
		sshare = params.SPOUSE_SHARE #spouses share of estate
		if sshare>0: #->need cohort to die simultaneously!!
			assert False
			account.transferto(spouse, sshare*estate_aftertax)
	kids_get = indiv.calc_wealth()
	if kids_get > 0:
		kids = [kid for kid in indiv._children if kid.alive]
		Mkids = [kid for kid in kids if kid.sex=='M']
		Fkids = [kid for kid in kids if kid.sex=='F']
		if Mkids and Fkids:
			alpha = params.MSHARE
			mshare = alpha*len(Mkids)
			fshare = (1-alpha)*len(Fkids)
			scale = mshare + fshare
			mshare = mshare/scale
			fshare = fshare/scale
			boy_gets =  mshare*kids_get
			girl_gets = fshare*kids_get
			#print "bg gets" , boy_gets, girl_gets
		elif Mkids:
			boy_gets = kids_get/len(Mkids)
			#print "b gets" , boy_gets
		elif Fkids:
			girl_gets = kids_get/len(Fkids)
			#print "g gets" ,  girl_gets
		else: #no kids
			raise NotImplementedError
		for kid in Mkids:
			account.transferto(kid, boy_gets)
		for kid in Fkids:
			account.transferto(kid, girl_gets)

#################################################################
##########################  CLASSES  ############################
#################################################################


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
		self._children = list()  #use list to track birth order
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
		newkids = other.get_children()
		if newkids:
			script_logger.warn("New spouse already has kids.")
			self.extend_children(newkids)
	def bear_children(self, sexes=None):
		'''Return this Indiv's kids
		Used by Pop.append_new_cohort
		'''
		assert self.spouse  #must be married ...
		assert (self.sex == 'F')  #only women can bear children
		#need `newkids` to be a sequence
		newkids = [self.__class__(economy=self.economy,sex=s) for s in sexes]
		for kid in newkids:
			kid.parents_bio = (self.spouse, self) #father,mother (biological)
			self.adopt(kid)
			self.spouse.adopt(kid)  #TODO: but maybe a child shd be born to a household???
		my_kids = self._children
		for kid in my_kids:
			kid.siblings.update(my_kids) #TODO: better approaches?
		assert (len(my_kids)==2) #TODO: will need to get rid of this constraint
		return newkids
	def extend_children(self, kids):
		for kid in kids:
			self.adopt(kid)
	def get_children(self):
		return self._children
	def adopt(self,child): #used by bear_children
		mykids = self._children
		assert (len(mykids) <= 2) #TODO: get rid of this constraint
		if child not in mykids:
			mykids.append(child)
		else:
			script_logger.warn("Tried to adopt own child")
	def open_account(self, fund, amt=0):
		'''Return: None.

		:param fund: Fund object to open account with
		:param amt: initial deposit in new account
		'''
		assert (len(self.accounts) == 0) #TODO: eventually allow multiple accounts
		acct = fund.create_account(self, amt=amt)
		self.accounts.append(acct)
	def gift2kids(self,amt):
		assert (0 <= amt <= self.calc_wealth()), "amt: %s\t w:%s"%(amt,self.calc_wealth())
		cash_acct = self.accounts[0]
		kids = self._children
		n = len(kids)
		for kid in kids:
			cash_acct.transferto(kid, amt/n)
	def liquidate(self):
		assert (self.alive is False)
		params = self.economy.params
		acct = self.accounts[0] #transactions acct
		if params.ESTATE_TAX:
			self.state.tax_estate(self)  #KC: tax_estate is a method in the State class
		self.distribute_estate()
		#close accounts
		assert abs(self.calc_wealth())<1e-5
		for acct in self.accounts:
			acct.close()  #acct asks its fund to close it
	def distribute_estate(self):
		assert (self.alive is False)
		params = self.economy.params
		params.BEQUEST_FN(self)

#October: Uncertainty, Decision, and Policy

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
	def get_age(self):
		return self._cohort_age
	def age_cohort(self):
		assert (indiv.age == self._cohort_age for indiv in self),\
		"indiv age shd not diverge from cohort age"
		self._cohort_age += 1
		for indiv in self:
			indiv.age += 1
	def get_married(self,mating):  #TODO: rename
		raise NotImplementedError

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
	def get_married(self, mating):	#TODO: move into Pop when marry across Cohorts
		males = list(self.males)
		females = list(self.females)
		maxkids = 2 #TODO TODO parameterize
		#sort males and females by wealth
		males.sort(key=lambda i: i.calc_wealth(),reverse=True)
		females.sort(key=lambda i: i.calc_wealth(),reverse=True)
		#class mating when cannot marry sibs
		if mating == "class_nosibs":
			script_logger.debug("get_married: class mating, no sibs")
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
			script_logger.debug("get_married: classonly mating")
			for m,f in itertools.izip(males,females): #some poor possibly left out
				f.wed(m)
			params = m.economy.params
			if params.DEBUG:
				mates = itertools.izip(males,females) #some poor possibly left out
				for m,f in mates:
					print m.calc_wealth(), f.calc_wealth(), m.calc_household_wealth()
		elif mating == "random":
			script_logger.debug("get_married: random mating")
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
		return sum( acct.get_value() for acct in self._accounts )
	def create_account(self, indiv, amt = 0):
		assert len(indiv.accounts)==0,\
		"num accts shd be 0 but is %d"%(len(self._accounts))
		acct = FundAcct(self, indiv, amt)
		self._accounts.append(acct)
		return acct
	def close_account(self,acct):
		self._accounts.remove(acct)
	def distribute_gains(self):
		pass #TODO TODO

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
	#Is anything using the distribute_estates function?  I think not ... 
	def distribute_estates(self,dead): #move details to Indiv? to State? to Economy? TODO
		script_logger.warn("Should not be here??")
		if self.economy.BEQUEST_TYPE == 'child_directed':
			for indiv in dead:
				heirs = indiv.get_children()
				n_children = len(heir)
				bequest_size = indiv.calc_wealth()/n_children #equal bequests
				for kid in heirs:
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
		self.append_new_cohort(parents, kidsexgen=params.KIDSEXGEN) #new cohort has age 0
		self.age_ppl()                         #->new cohort has age 1
		dead = self.pop_new_dead()
		assert(dead._cohort_age == self.params.N_COHORTS+1) #TODO only works for non-stochastic deaths
		for indiv in dead:
			indiv.liquidate()  #close out all accounts
	def get_labor_force(self):
		'''Return: list of Indiv instances.
		'''
		labor_force = list()
		working_ages = self.economy.params.WORKING_AGES
		labor_cohorts = ( cohort for cohort in self if cohort.get_age() in working_ages )
		for cohort in labor_cohorts:
			labor_force.extend( cohort )
		return labor_force
	def pop_new_dead(self): #removes dead from population and returns as sequence
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
	def append_new_cohort(self, parents, kidsexgen=None):
		'''Return: None.
		Called by evolve.
		Current model: two children, MF, at fixed age.

		:param kidsexgen: returns an iterator which provides sex tuples (e.g., 'MF' or 'MMF')
		'''
		params = self.economy.params
		new_cohort = list()
		#only married females can have kids
		mothers = [indiv for indiv in parents if (indiv.spouse and indiv.sex=='F')]
		getsexes = kidsexgen(len(mothers))
		#each mother has kids of specified sexes (e.g., "MF"), which specifies number as well!
		for indiv in mothers:
			newsexes = getsexes.next()  #TODO: remove restriction to 2 simultaneous kids!!
			new_cohort.extend(indiv.bear_children(sexes=newsexes))
		for kid in new_cohort:
			kid.open_account(self.economy.funds[0])  #provide every kid with an acct
		self.initialize_wealth(new_cohort)
		new_cohort = params.Cohort(new_cohort)
		self.append( new_cohort )
	def calc_dist_wealth(self): #TODO: calc distribution over **indivs** or households??
		params = self.economy.params
		return  params.CALC_DIST_WEALTH(self)
	def get_indivs(self): #return all individuals as single list
		return [indiv for cohort in self for indiv in cohort]
	def gf_indivs(self): #return all individuals as single generator
		return (indiv for cohort in self for indiv in cohort)
	def initialize_wealth(self, kids):
		return NotImplemented

class Economy(object):
	'''
	Not fully implemented.
	'''
	def __init__(self, params):
		script_logger.debug("begin Economy initialization")
		self.params = params
		self.dist_hist = list()
		self.funds = [ Fund(self) ]  #association needed so Fund can access WEALTH_INIT. Change? TODO
		self.state = None  #TODO TODO
		#initialize economy
		self.ppl = self.create_initial_population()
		self.initialize_population()
		self.firms = self.create_initial_firms()
		script_logger.debug("end Economy initialization")
		script_logger.debug("cohorts: %d; indivs: %d; firms: %d"%(len(self.ppl), len(self.ppl.get_indivs()), len(self.firms)))
	def create_initial_population(self):
		'''Return: a population.
		Override this to use a different sex generator.
		Set Cohort and Indiv classes in params.
		'''
		script_logger.info("create initial population")
		params = self.params
		n_cohorts = params.N_COHORTS
		cohort_size = params.COHORT_SIZE
		cohorts = list()
		for _ in range(n_cohorts):
			indivs = (params.Indiv(economy=self, sex=s) for i in range(cohort_size//2) for s in "MF")
			cohort = params.Cohort(indivs)
			cohorts.append(cohort)
		return params.Population(cohorts)
	def initialize_population(self):
		script_logger.info("initialize population")
		params = self.params
		self.ppl.economy = self  #currently needed for fund access!? TODO
		self.ppl.params = params  #currently needed for parameter access
		age = params.N_COHORTS #initialize, to count down
		for cohort in self.ppl:  #don't actually use ages of initial cohorts, but might in future
			cohort.set_age(age)
			age -= 1
		assert (age == 0) , "no cohort has age 0"
		#open an acct for every Indiv (using the default Fund)
		script_logger.info("assigned indivs initial accounts")
		indivs = self.ppl.get_indivs()
		fund = self.funds[0]
		for indiv in indivs:
			script_logger.debug("open acct for indiv")
			indiv.open_account(fund)
		#initialize parenthood relationship when starting economy
		#if params.BEQUEST_TYPE ==: #unnecessary
		#remember: age = N_COHORTS - index
		script_logger.info("initialize family structure")
		for idx in range(params.N_COHORTS - params.KID_AT_YEAR+1):   ###!! E.g., OG: 2-2+1 (fixed)
			parents = self.ppl[idx]  #retrieve a cohort to be parents
			parents.get_married(mating=params.MATING)  #parents are a Cohort
			kids = self.ppl[idx+params.KID_AT_YEAR-1]  ##!! (fixed)
			assert (len(parents)==len(kids))
			for parent, kid in itertools.izip(parents,kids):
				parent.adopt(kid)
				parent.spouse.adopt(kid)  #TODO: think about adoption
		if params.WEALTH_INIT:
			script_logger.info("distribute initial wealth")  #TODO details scarce in Pestieau 1984
			distribute(params.WEALTH_INIT, (i for i in indivs if i.sex=='M'), params.GW0, params.SHUFFLE_NEW_W) #TODO
			#assert (abs(self.ppl.calc_dist_wealth() - params.GW0) < 0.001)  #TODO!!!!!
	def create_initial_firms(self):
		'''Return: a (possibly empty) list of firms.
		Set Firm class in params.
		(Single sector economy.)
		'''
		script_logger.info("create initial firms")
		params = self.params
		return [Firm() for i in range(params.N_FIRMS)]
	def initialize_firms(self):
		'''
		Note: much of this will look superflous when there is only one firm.
		'''
		script_logger.info("initialize firms")
		params = self.params
		nfirms = len(self.firms)
		labor_force = self.ppl.get_labor_force()
		
		#TODO TODO: allocate capital stock
	def run(self):  #TODO: rely on IterativeProcess?
		script_logger.info("run the economy")
		params = self.params
		assert (len(self.ppl) == params.N_COHORTS)
		assert (len(self.ppl[0]) == params.COHORT_SIZE)
		if params.seed:
			random.seed(params.seed)
		#record initial distribution
		self.dist_hist.append( self.ppl.calc_dist_wealth() )   #TODO TODO does this work well for Pestieau??
		#MAIN LOOP: run economy through N_YEARS "years"
		for t in range(params.N_YEARS):
			#TODO: allow transfers by state??
			#TODO distribute gains *before* aging the ppl (so they are included in bequests)
			self.produce()
			self.factor_payments()
			self.consume()
			self.ppl.evolve()
			self.dist_hist.append( self.ppl.calc_dist_wealth() )
	def produce(self):
		pass
	def consume(self):
		pass
	def factor_payments(self):
		for firm in self.firms:
			firm.pay_wages()
			firm.pay_rents()
		for fund in self.funds:
			fund.distribute_gains()
	def transfer(self, fr, to, amt):  #TODO: cd introduce transactions cost here, cd be a fn
		fr.outgo(amt)
		to.receive_income(amt)
	def final_report(self):
		params = self.params
		#TODO: household or indiv distributions? (household I think wd be better)
		indiv_wealths = [indiv.calc_wealth() for indiv in self.ppl.gf_indivs()]
		report = '''
		Final Gini for individual wealth: %10.2f
		'''%(self.dist_hist[-1])
		#uncomment to check for number of zeros
		#print "zeros: %d\t small:%d"%(sum(i==0 for i in indiv_wealths),sum(i<0.5 for i in indiv_wealths))
		
		

###################
def compute_ability_pestieau(indiv, beta, nbar):
	'''Return: float (child's ability).
	Formula taken from Pestieau 1984, p.407.

	:Parameters:
	  beta : float
	    Pestieau's ability regression parameter
	  nbar : float
	    Pestieau's mean number of kids 
	'''
	#determine ability from biological parents, if possible
	try:
		father, mother = indiv.parents_bio
		assert (father.sex == 'M' and mother.sex == 'F') #just an error check
		assert (0 < beta < 1) 	#Pestieu p. 407
		nsibs = len(mother.get_children())
		assert (nsibs>0)    #Pestieau p.407
		parents_ability = (father.ability + mother.ability)/2.0  #Pestieau p.412
		z = random.normalvariate(0.0,0.15)  #Pestieau p.413-414
		#Pestieau formula does not allow for zero kids??
		ability = beta*parents_ability + (1-beta)*nbar/nsibs + z #Pestieau p.407 (role of nbar is weird)
	except (TypeError, AttributeError):  #if indiv.parents_bio is None
		ability = random.normalvariate(1.0,0.15) #for initial cohort
	return ability

#Pestieau markets very simple (one aggregate "firm")

class LaborMarket(object):
	def __init__(self, economy):
		self.economy = economy
		self.employers = None
	def set_labor_force(self, indivs):
		self.labor_force = indivs
	def set_employers(self, firms):
		employers = self.firms
	def determine_employment(self):
		return NotImplemented

class PestieauLaborMarket(LaborMarket):
	def determine_employment(self):
		economy = self.economy
		Ls = economy.labor_force
		firm = self.employers[0]
		firm.hire(self.labor_force)
	
class CapitalMarket(object):
	def __init__(self, economy):
		self.economy = economy
		self.K = None
		self.renters = None
	def set_labor_force(self, indivs):
		self.labor_force = indivs
	def set_employers(self, firms):
		employers = self.firms
	def determine_employment(self):
		return NotImplemented

class PestieauCapitalMarket(LaborMarket):
	def determine_employment(self):
		firm = self.renters[0]
		firm.rent(self.K)

class Firm:
	def __init__(self, blue_print=None, employees=None, capital=None, economy=None):
		self.blue_print = blue_print
		self.economy = economy
		self.employees = employees
		self.wage_share = None
		self.output_last = None
	def produce(self):
		labor_input = sum(e.labor_power for e in self.employees)
		capital_input = self.capital
		self.output_last = self.blue_print(capital=capital_input, labor=labor_input)
		return self.output_last
	def pay_employees(self):
		wages = self.wage_share * output_last
		labor_input = sum(e.labor_power for e in self.employees)
		wage = wages/labor_input
		for employee in self.employees:
			employee.receive_income(wage * employee.labor_power)
	def pay_wages(self):
		pass
	def pay_rents(self):
		pass

import functools
class EconomyParams(object): #default params, needs work
	def __init__(self):
		self.DEBUG = False
		#set class to use in Economy construction
		self.Indiv = Indiv
		self.Cohort = Cohort
		self.Population = Population
		self.Firm = Firm
		#list life periods Indivs work (e.g., range(16,66))
		self.WORKING_AGES = list()
		self.seed = None
		#default is individual based Gini
		#TODO: household or indiv distributions? (household I think wd be better)
		self.CALC_DIST_WEALTH = lambda ppl: utilities.calc_gini( indiv.calc_wealth() for indiv in ppl.gf_indivs() )
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
		self.KID_AT_YEAR = 0   #NOTE: no cohort has age 0!

class PestieauParams(EconomyParams):
	def __init__(self):
		#first use the super class's initialization
		EconomyParams.__init__(self)
		#NEW INITIALIZATIONS
		self.Cohort = PestieauCohort  #provides `get_married`
		self.N_YEARS = 30
		self.COHORT_SIZE = 100  #p.412
		self.WORKING_AGES = [1]
		#number of Firms
		self.N_FIRMS = 1
		#number of Cohorts
		self.N_COHORTS = 2
		#two period economy, work only period 1 (age 1), bear kids period 2 (age 2)
		self.KID_AT_YEAR =  2   #see Population.evolve (no cohort has age 0!)
		self.MATING = 'classonly' #p.414 says only class mating considered (vs. reported!?)
		#sex generator for new births
		self.KIDSEXGEN = sexer_randompairs         #TODO
		#bequest function
		self.BEQUEST_FN = bequests_pestieau #p.412
		## NEW PARAMETERS  (Pestieau specific)
		self.PESTIEAU_BETA = None
		self.PESTIEAU_NBAR = None
		self.compute_ability = functools.partial(compute_ability_pestieau, beta=self.PESTIEAU_BETA, nbar=self.PESTIEAU_NBAR)  #TODO TODO
		#initial Gini for Wealth
		self.GW0 = 0.8  #"high inequality" case p.413
		#initial wealth(capital stock)
		self.WEALTH_INIT = 100
		#LAST as an error check, lock against dynamic attribute creation (eventually remove TODO)
		self._locked = True
	def __setattr__(self, attr, val):
		'''Override __setattr__:
		no new attributes allowed after initialization.
		'''
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val 


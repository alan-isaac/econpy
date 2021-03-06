'''
Provides a collection of agents for replication of Pestieau (1984 OEP).

PestieauIndiv
	- Data: alive, sex, age, parents, siblings, spouse, _children, accounts,
	employers, economy, state, contracts
	- New Methdods:
	  receive_income, payout, calc_wealth, calc_household_wealth, wed,
	  bear_children, gift2kids, liquidate, distribute_estate, labor_supply, accept_contract,
	  fulfill_contract, 


PestieauCohort(Cohort)
	- Inherit Data: _age, males, females
	- Inherit Methods: marry, set_age, increment_age
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
	- Methdods: receive_income, payout, close, transferto

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

import random, itertools
from collections import defaultdict
from econpy.pytrix import utilities, fmath
from econpy.abm.utilities import impose_gini
from econpy.abm.agents import agents001

#logging
import logging
script_logger = logging.getLogger('script_logger')


#################################################################
#########################  functions  ###########################
#################################################################

def sexer_unisex2(n):
	'''Yield 'FF' n times.
	'''
	for _ in range(n):
		yield 'FF'

def sexer_pestieau_poisson(n):  #TODO TODO chk
	from numpy.random import poisson
	nkidsvec = poisson(2,n)
	for nkids in nkidsvec:
		result = 'F'*nkids
		print result,
		yield result

def sexer_pestieau_123(n):  #TODO TODO chk
	'''Yield: all females, in specified distribution.
	(Pestieau has marriage but is unisex, I believe.)
	'''
	for _ in range(n):
		draw = random.random()
		if draw < 0.2:
			result = 'F'
		elif draw < 0.8:
			result = 'FF'
		else:
			result = 'FFF'
		print result,
		yield result

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
	:todo: state networth shd be distributed to *all* kids in economy TODO TODO
	'''
	kids = indiv.get_children()  #:note: chk that kids alive?
	if not kids: #empty list, no kids
		kids = [indiv.economy.state] #if not kids, state gets estate
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


class PestieauIndiv(agents001.Indiv):
	def __init__(self, sex=None, economy=None):
		agents001.Indiv.__init__(self, sex, economy)
		if economy:
			self.ability = economy.params.compute_ability(self)
	def payout(self, amt):  #redundant; just for ease of reading and sign check
		assert(amt >= 0)
		self.accounts[0].payout(amt)  # KC: payout is a method in the FundAcct class
	def calc_household_wealth(self):  #just self and spouse (but cd add def of household as any set!)
		wealth = self.calc_wealth()
		if self.spouse:
			wealth += self.spouse.calc_wealth()
		return wealth
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
	def labor_supply(self, wage, irate):
		#default is inelastic labor supply
		#(override for different behavior)
		return self.ability
	def accept_contract(self, contract):
		self.contracts[contract.type].append(contract)
	def fulfill_contract(self, contract):
		if contract.type == 'labor':
			assert (contract.seller == self)
			result = self.labor_supply(wage=None, irate=None)
		else:
			raise ValueError("Unknown contract type.")
		return result

#October: Uncertainty, Decision, and Policy

class PestieauCohort(agents001.Cohort):
	'''Cohort class for Pestieau 1984 replication.
	Assuming Pestieau economy is unisex, like Pryor.
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
	def marry(self, mating):
		script_logger.debug( "Enter PestieauCohort.marry" )
		maxkids = 2 #TODO TODO MUST change this
		if mating == "classonly_unisex":
			script_logger.debug("marry: classonly_unisex mating")
			#sort cohort by wealth (requires a copy)
			mates = sorted(self, key=lambda i: i.calc_wealth(),reverse=True)
		elif mating == "random_unisex":
			script_logger.debug("marry: random_unisex mating")
			mates = random.shuffle(list(self))
		else:
			assert (mating is None),\
			"%s is an unknown mating type"%(mating)
		weddings = 0
		for m,f in utilities.groupsof(mates, 2):
			#use next trick to allot children to couples, as needed for Pestieau
			m.sex = 'M'
			f.wed(m)
			weddings += 1
		script_logger.debug( "%d weddings."%(weddings) )



class PestieauFund(agents001.Fund):
	def distribute_gains(self):
		accts_value = self.calc_accts_value()
		assert accts_value==sum( indiv.calc_wealth() for indiv in self.economy.ppl.get_indivs() )
		ror = self.net_worth/accts_value
		for acct in self._accounts:
			value = acct.get_value()
			self.economy.transfer(self, acct, ror*value)
		assert fmath.feq(self.net_worth, 0, 0.01)  #this chk is currently pointless

class FundAcct(agents001.FundAccount):
	def __init__(self, economy):
		agents001.FundAccount.__init__(self, economy)
		self._locked = False
		#only capital services contracts
		self.contracts = dict(capital=[])
		self._locked = True


class State(agents001.State):
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


class Population(agents001.Population):  #provide a list of Cohort tuples
	def evolve(self):  #this will be called each "tick" of the economy
		'''Return: None.
		Evolve population to new state.
		Should be the **last** action in the main loop.
		Establishes the population state for the next iteration.
		'''
		params = self.economy.params  #associated economy have been set by economy...
		new_cohort = self.get_new_cohort()
		self.append(new_cohort)
		self.age_ppl()                         #->new cohort has age 1
		dead = self.get_new_dead()
		assert(dead._age == params.N_COHORTS+1) #TODO only works for non-stochastic deaths
		for indiv in dead:
			indiv.liquidate()  #close out all accounts, leaving bequests
	def get_labor_force(self):
		'''Return: list of Indiv instances.
		'''
		labor_force = list()
		working_ages = self.economy.params.WORKING_AGES
		labor_cohorts = ( cohort for cohort in self if cohort.get_age() in working_ages )
		for cohort in labor_cohorts:
			labor_force.extend( cohort )
		return labor_force
	def have_kids(self):
		n_mothers = sum( 1 for indiv in self.gen_new_mothers() )
		script_logger.debug( "Number of new mothers: %d"%(n_mothers) )
		#sex generator may need to know n_mothers in order to determine distributional properties
		#  kidsexgen is an iterator which provides sex strings (e.g., 'MF' or 'MMF')
		getsexes = params.KIDSEXGEN(n_mothers)
		if self.economy.params.DEBUG:
			getsexes = list(getsexes)
			self.new_cohort_sexes = ";".join(getsexes)
			getsexes = iter(getsexes)
		mothers = self.gen_new_mothers()
		#each mother has kids of specified sexes (e.g., "MF"), which specifies number as well!
		'''
		new_cohort = list()
		for indiv in mothers:
			newsexes = getsexes.next()
			new_cohort.extend(indiv.bear_children(sexes=newsexes))
		'''
		#sum the lists of kids, one list for each mother
		new_cohort = sum( (indiv.bear_children(sexes=getsexes.next()) for indiv in mothers), [])
		for kid in new_cohort:
			kid.open_account(self.economy.funds[0])  #provide every kid with an acct TODO move
		#self.initialize_wealth(new_cohort)  #TODO move
		return params.COHORT(new_cohort)
	def initialize_kids(self):
		pass

class Economy(object):
	'''
	Not fully implemented.
	'''
	def __init__(self, params):
		script_logger.debug("begin Economy initialization, economy type: %s"%(type(self)))
		if params.SEED:
			random.seed(params.SEED)
		self.params = params
		self.history = defaultdict(list)
		self.wage_contracts = list()
		self.rent_contracts = list()
		self.funds = [ params.FUND(account_type=FundAccount, economy=self) ]
		#association needed so Fund can access WEALTH_INIT. Change? TODO
		self.state = params.STATE(economy=self)
		#initialize economy
		self.ppl = self.create_initial_population()
		self.initialize_population()
		self.initialize_wealth()
		self.firms = self.create_initial_firms()
		script_logger.debug("end Economy initialization")
		script_logger.info("cohorts: %d; indivs: %d; firms: %d"%(len(self.ppl), self.ppl.get_size(), len(self.firms)))
	def create_initial_population(self):
		'''Return: a population.
		Override this to use a different sex generator. TODO
		Set Cohort and Indiv classes in params.
		'''
		script_logger.info("create initial population")
		params = self.params
		if 'unisex' in params.MATING:
			sexes = 'FF'
		else:
			sexes = 'MF'
		n_cohorts = params.N_COHORTS
		cohort_size = params.COHORT_SIZE
		cohorts = list()
		for _ in range(n_cohorts):
			indivs = (params.INDIV(sex=s, economy=self) for i in range(cohort_size//2) for s in sexes)
			cohort = params.COHORT(indivs)
			cohorts.append(cohort)
		return params.Population(cohorts)
	def initialize_population(self):
		script_logger.info("initializing population")
		params = self.params
		self.ppl.economy = self  #currently needed for fund access!? TODO
		age = params.N_COHORTS #initialize, to count down
		script_logger.info("- setting initial cohort ages")
		for cohort in self.ppl:  #don't actually use ages of initial cohorts, but might in future
			cohort.set_age(age)
			age -= 1
		assert (age == 0) , "no cohort has age 0"
		#open an acct for every Indiv (using the default Fund)
		script_logger.info("- assigning indivs initial accounts")
		fund = self.funds[0]
		for indiv in self.ppl.gen_indivs(): #get as generator NOT as list!
			indiv.open_account(fund)
		#initialize parenthood relationship when starting economy
		#if params.BEQUEST_TYPE ==: #unnecessary
		#remember: age = N_COHORTS - index
		script_logger.info("- initializing family structure")
		script_logger.info("  - initializing marriages")
		for idx in range(params.N_COHORTS - params.AGE4MARRIAGE):   ###!! E.g., OG: 2-1 chk
			newlyweds = self.ppl[idx]  #retrieve a cohort to be wed
			assert all(i.spouse is None for i in parents)
			newlyweds.marry(mating=params.MATING)  #parents are a Cohort -> use cohort method
		script_logger.info("  - initializing parenthood")
		for idx in range(params.N_COHORTS - params.AGE4KIDS + 1):   ###!! E.g., OG: 2-2+1 chk
			parents = self.ppl[idx]  #retrieve a cohort to be parents
			kids = self.ppl[idx+params.AGE4KIDS-1]  ##!! (fixed)
			assert (len(parents)==len(kids))  #TODO TODO only for fixed 2 kid per couple
			for parent, kid in itertools.izip(parents,kids):
				parent.adopt(kid)
				parent.spouse.adopt(kid)  #TODO: think about adoption
			for parent in parents:
				for kid in parent._children:
					assert parent._age == kid.age + params.AGE4KIDS-1
		script_logger.info("  family structure initialized")
	def initialize_wealth(self, males_only=False):
		script_logger.info("- initializing wealth distribution")
		script_logger.info("- distributing initial wealth")  #TODO details scarce in Pestieau 1984
		params = self.params
		#if params.WEALTH_INIT:
		indivs = self.ppl.gen_indivs()
		if males_only:
			indivs = (i for i in indivs if i.sex=='M')
		impose_gini(params.WEALTH_INIT, indivs, params.GW0, params.SHUFFLE_NEW_W) #TODO
		#assert (abs(self.ppl.calc_dist_wealth() - params.GW0) < 0.001)  #TODO!!!!!
	def create_initial_firms(self):
		'''Return: a (possibly empty) list of firms.
		Set Firm class in params.
		(Single sector economy.)
		'''
		script_logger.info("creating initial firms")
		params = self.params
		script_logger.debug("firm type: %s"%(params.FIRM))
		return [params.FIRM(economy=self) for i in range(params.N_FIRMS)]
		print [params.FIRM(economy=self) for i in range(params.N_FIRMS)]
	def initialize_firms(self): #TODO unnecessary???
		'''
		Note: much of this will look superflous when there is only one firm.
		'''
		script_logger.info("initialize firms")
		params = self.params
		nfirms = len(self.firms)
		labor_force = self.ppl.get_labor_force()
		
		#TODO TODO: allocate capital stock
	def run(self):  #TODO: rely on IterativeProcess?
		'''Return: None.
		Run economy *after* it has been initialized.
		'''
		params = self.params
		assert (len(self.ppl) == params.N_COHORTS)
		assert (len(self.ppl[0]) == params.COHORT_SIZE)
		#record initial distribution
		self.record_history()
		#MAIN LOOP: run economy through N_YEARS "years"
		script_logger.info("BEGIN MAIN LOOP")
		for t in range(params.N_YEARS):
			#TODO: allow transfers by state??
			script_logger.debug("  - allocate factors")
			self.allocate_factors()
			script_logger.debug("  - produce")
			self.produce()
			#distribute gains *before* aging the ppl (so they are included in bequests)
			script_logger.debug("  - factor payments")
			self.factor_payments()
			script_logger.debug("  - marriages")
			self.ppl.marry()
			script_logger.debug("  - consumption")
			self.consume()
			script_logger.debug("  - evolve ppl")
			self.ppl.evolve()  #TODO TODO
			self.record_history()
			script_logger.info("\n" + " Iteration %d complete. ".center(70,'#')%(t+1) + "\n")
	def allocate_factors(self):
		# factor mkts determine K, L, and allocation of K, L
		script_logger.warn("Economy.allocate_factors: not implemented")
	def produce(self):
		# firms produce
		script_logger.warn("Economy.produce: not implemented")
	def factor_payments(self):
		# economy wide factor payments
		script_logger.warn("Economy.factor_payments: not implemented")
	def consume(self):
		script_logger.warn("Economy.consume: not implemented")
	def record_history(self): #TODO: calc distribution over **indivs** or households??
		history = self.history
		#compute current wealth distribution
		dist = utilities.calc_gini( indiv.calc_wealth() for indiv in self.ppl.gen_indivs() )
		history['dist'].append(dist)
		history['ppl_size'].append(self.ppl.get_size())
		history['capital'].append( self.funds[0].calc_accts_value() )
		if hasattr(self.ppl, 'new_cohort_sexes'):
			freq = defaultdict(int)
			for s in self.ppl.new_cohort_sexes.split(';'):
				freq[len(s)] += 1
			history['sexes'].append( freq )
		#compute wealth distribution of young
		#dist0 = utilities.calc_gini( indiv.calc_wealth() for indiv in self.ppl[0] )
		#history['dist0'].append(dist0)
	def transfer(self, fr, to, amt):  #TODO: cd introduce transactions cost here, cd be a fn
		#TODO: improve acctg
		fr.payout(amt)
		to.receive_income(amt)
	def final_report(self):
		report = [" Final Report ".center(80, '*')]
		for key, val in self.history.iteritems():
			report.append( '\n' + key + ': ' + str(val) )
		report.append('''
		Final Gini for individual wealth: %10.2f
		'''%(self.history['dist'][-1]) )
		#uncomment to check for number of zeros
		#print "zeros: %d\t small:%d"%(sum(i==0 for i in indiv_wealths),sum(i<0.5 for i in indiv_wealths))
		return '\n'.join(report)

class PestieauEconomy(Economy):
	def allocate_factors(self):
		assert len(self.funds)==1 and len(self.firms)==1
		fund = self.funds[0]
		repfirm = self.firms[0]
		# factor mkts determine K, N, and allocation of K, N
		# also determine w and irate for these services
		labor_force = self.ppl.get_labor_force()
		#inelastically supplied factors fully employed
		#only the young in the labor force
		elabor = sum(indiv.labor_supply(None, None) for indiv in labor_force) #chk
		#only the young own capital
		capital = fund.calc_accts_value()
		if self.params.DEBUG:
			capital2 = sum(indiv.calc_wealth() for indiv in labor_force)  #chk
			assert fmath.feq(capital2, capital)
		#PestieauEconomy has a single representative firm
		irate, wage = repfirm.mpk_mpn(capital=capital, elabor=elabor)
		script_logger.debug( "Eq. irate %10.2f,           wage %10.2f"%(irate, wage) )
		capital_contract = ServiceContract(contract_type='capital', quantity=capital, price=irate, buyer=repfirm, seller=fund)
		labor_force = self.ppl.get_labor_force()
		script_logger.debug( "Labor force size: %d."%(len(labor_force)) )
		for worker in labor_force:
			labor = worker.labor_supply(irate=None, wage=None) #inelastic labor supply
			wage_contract = ServiceContract(contract_type='labor', quantity=labor, price=wage, buyer=repfirm, seller=worker)  #TODO TODO
		script_logger.debug( "Number of labor contracts: %d."%(len(repfirm.contracts['labor'])) )
		if self.params.DEBUG:
			captital = sum( contract.quantity for contract in repfirm.contracts['capital'] )
			labor = sum( contract.quantity for contract in repfirm.contracts['labor'] )
			script_logger.info("Capital (%10.2f) and eff. labor (%10.2f) allocated."%(capital, elabor))
			script_logger.info("irate (%10.2f) and w (%10.2f) determined."%(irate, wage))
	def factor_payments(self): #chk chk
		'''collect factor payments from representative firm;
		allocate factor payments to providers of factor services.

		:todo: must pay rents before wages, bc rents paid on
		       the individual's wealth, so don't want to change
		       that before paying rents.  This is ugly.
		       Get capital from and pay rents to fund instead. chk
		'''
		assert len(self.firms)==1 and len(self.funds)==1
		repfirm = self.firms[0]
		inventory = repfirm.inventory  #production not yet distributed
		fund = self.funds[0]
		rents_paid = 0
		contracts = repfirm.contracts['capital']  #not a copy!
		while contracts:
			contract = contracts.pop()  #removes contract from list
			assert (contract.seller is fund)  #for simplicity, fund provides all capital services
			rents_paid += contract.payment()   #firm rents capital from fund
		#currently *MUST* distribute gains *BEFORE* other income rcd
		# (this buys convenience of single contract with Fund instead of contracts w each indiv)
		fund.distribute_gains()  #fund distributes gains to fund accounts
		script_logger.debug( "Number of labor contracts: %d."%(len(repfirm.contracts['labor'])) )
		wages_paid = 0
		contracts = repfirm.contracts['labor']  #not a copy!
		while contracts:
			contract = contracts.pop()  #removes contract
			assert isinstance(contract.seller, Indiv) # ugly
			wages_paid += contract.payment()  #payment fulfills contract
		if self.params.DEBUG:
			script_logger.debug("Production: %10.2f"%(inventory))
			script_logger.debug("Factor payments: %10.2f (= %10.2f + %10.2f)"%(rents_paid+wages_paid, rents_paid, wages_paid))
			script_logger.debug("Remaining inventory: %10.2f"%(repfirm.inventory))
		assert fmath.feq(repfirm.inventory, 0, 1e-6*inventory)
		#reset inventory to prevent accumulation of small differences
		repfirm.inventory = 0
		#for fund in self.funds: fund.distribute_gains()  #TODO  #TODO
	def produce(self):
		# firms produce
		script_logger.debug("enter PestieauEconomy.produce")
		firms = self.firms
		assert len(firms)==1
		firms[0].produce()
	def consume(self):
		script_logger.warn("PestieauEconomy.consume: stopgap implementation")
		for indiv in self.ppl.get_indivs():
			w = indiv.calc_wealth()
			#c = w/2 if w<1 else w-1 #target bequest level
			c = 0.9*w #target bequest share
			indiv.payout(c)

class ServiceContract(object):
	'''Single period (tick) service contract.
	Service provided in advance of payment.
	Provides a kind of implicit 3rd party for
	payment flows and service flows.

	:note: Consider labor supply and labor payments.  Payments generally should take
		place after the economy produces, but the economy cannot produce
		without labor.  Using this class, firms can contract for the labor.
		They get the labor via the contract, produce, and then make the payment
		via the contract.  The contract in this sense is just handling the accounting.
	'''
	def __init__(self, contract_type, quantity, price, buyer, seller):
		self._service = False  #service not provided yet
		self._payment = False  #payment not provided yet
		self.type = contract_type
		self.quantity = quantity
		self.price = price
		self.buyer = buyer
		self.seller = seller
		buyer.accept_contract(self)
		seller.accept_contract(self)
	def service(self):
		assert (self._service is False)
		quantity = self.seller.fulfill_contract(self)
		assert (quantity == self.quantity)
		self._service = True
		return quantity
	def payment(self):
		assert (self._service is True)  #no payment before service provided
		amt = self.price * self.quantity
		self.buyer.payout(amt)
		self.seller.receive_income(amt)
		self._payment = True
		return amt



###################
#BEGIN compute_ability_pestieau
def compute_ability_pestieau(indiv, beta, nbar):
	'''Return: float (child's ability).

	:see: Pestieau 1984, p.407, equation 3
	:param beta: float, ability regression parameter
	:param nbar: float, mean number of kids 
	'''
	assert (0 < beta < 1) 	#Pestieu p. 407
	#determine ability from biological parents, if possible
	try:
		father, mother = indiv.parents
		assert (father.sex == 'M' and mother.sex == 'F') #just an error check, but not in Pestieau, so dump TODO
		sibsize = len(mother.get_children())
		assert (sibsize>0)    #error check
		parents_ability = (father.ability + mother.ability)/2.0  #Pestieau p.412
		z = random.normalvariate(0.0,0.15)  #Pestieau p.413-414
		#Pestieau formula (note: role of nbar is peculiar)
		ability = beta*parents_ability + (1-beta)*nbar/sibsize + z
	except (TypeError, AttributeError):  #if indiv.parents is None
		ability = random.normalvariate(1.0,0.15) #for initial cohort
	return ability
#END compute_ability_pestieau




class CobbDouglas2(object):
	def __init__(self, alpha=0.4):
		assert (0 < alpha < 1)
		self.alpha = alpha
		self.capital = 0
		self.elabor = 0
	def __call__(self, capital, elabor):
		self.capital = capital
		self.elabor = elabor
		return self.produce()
	def produce(self, capital=None, elabor=None):
		capital = capital or self.capital 
		elabor = elabor or self.elabor 
		alpha = self.alpha
		return capital**alpha * elabor**(1-alpha)
	def mpk(self, capital=None, elabor=None):  #rename TODO
		capital = capital or self.capital 
		elabor = elabor or self.elabor 
		Y = self.produce(capital, elabor)
		return (self.alpha/capital) * Y
	def mpn(self, capital=None, elabor=None):  #rename TODO
		capital = capital or self.capital 
		elabor = elabor or self.elabor 
		Y = self.produce(capital, elabor)
		return (self.alpha/capital) * Y
	def gradient(self, capital=None, elabor=None):
		capital = capital or self.capital 
		elabor = elabor or self.elabor 
		Y = self.produce(capital, elabor)
		alpha = self.alpha
		mpk = Y * alpha / capital
		mpn = Y * (1-alpha) / elabor
		return mpk, mpn
	def mpk_mpn(self, capital=None, elabor=None):
		return self.gradient(capital, elabor)

class FirmKN(object):
	'''A firm using two factors of production,
	usually called capital and efficiency labor.
	Labor and capital are 'hired' for one period
	of production, and then released.
	'''
	def __init__(self, blue_print=None, economy=None):
		self.set_blue_print(blue_print)
		self.economy = economy
		self.elabor = 0
		self.contracts = dict(labor=[], capital=[])
		self.capital = 0
		self.inventory = 0
	def produce(self):
		script_logger.debug( "Begin production: initial inventory %10.2f"%(self.inventory) )
		elabor = sum( contract.service() for contract in self.contracts['labor'] )
		capital = sum( contract.service() for contract in self.contracts['capital'] )
		script_logger.debug( "Factor services: %10.2f, %10.2f"%(capital, elabor) )
		production = self.blue_print(capital=capital, elabor=elabor)
		script_logger.debug( "Total production: %10.2f"%(production) )
		self.inventory += production
		############
		self.elabor = elabor
		self.capital = capital
	def accept_contract(self, contract):
		self.contracts[contract.type].append(contract)
	def receive_income(self, amt):
		assert(amt >= 0)  #this is just sign checking
		self.inventory += amt
	def payout(self, amt):  #redundant; just for ease of reading and sign check
		assert(amt >= 0)
		self.inventory -= amt
	def mpk_mpn(self, capital=None, elabor=None):
		return self.blue_print.mpk_mpn(capital=capital, elabor=elabor)
	def set_blue_print(self, bp):
		self.blue_print = bp


	######### don't use the following #############
	def old_produce(self):
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

class PestieauFirm(FirmKN):
	def set_blue_print(self, bp):
		assert (bp is None)
		self.blue_print = CobbDouglas2(alpha=0.4)  #plausible capital share


class PestieauParams(agents001.EconomyParams):
	def __init__(self):
		#first use the super class's initialization
		EconomyParams.__init__(self)
		self.DEBUG = True
		#NEW INITIALIZATIONS
		self.STATE = State
		self.FUND = PestieauFund
		self.FIRM = PestieauFirm
		self.LABORMARKET = None
		self.COHORT = PestieauCohort  #provides `marry`
		self.N_YEARS = 30  #p.413
		self.COHORT_SIZE = 100  #p.412
		self.WORKING_AGES = [1]
		#number of Firms
		self.N_FIRMS = 1
		#number of Cohorts
		self.N_COHORTS = 1  #TODO TODO
		#two period economy, work only period 1 (age 1), bear kids period 2 (age 2)
		self.MATING = 'classonly_unisex' #p.414 says only class mating considered (vs. reported!?)
		#sex generator for new births
		#self.KIDSEXGEN = sexer_unisex2
		self.KIDSEXGEN = sexer_pestieau_poisson
		#self.KIDSEXGEN = sexer_pestieau_123         #TODO need other sexers
		#bequest function
		self.BEQUEST_FN = bequests_pestieau #p.412
		#Life Events
		# AGE4KIDS is how old you are when you kids appear in the economy (you may be dead)
		self.AGE4KIDS =  2      #see Population.evolve (no cohort has age 0!)
		self.AGE4MARRIAGE = 1   #NOTE: no cohort has age 0!
		## NEW PARAMETERS  (Pestieau specific)
		self.PESTIEAU_BETA = None
		#mean number of children
		self.PESTIEAU_NBAR = 2
		#MISSING PARAMETERS (not found in Pestieau 1984; see pestieau1984background.tex) recheck TODO
		#initial Gini for Wealth
		self.GW0 = 0.8  #"high inequality" case p.413
		#initial wealth(capital stock)
		self.WEALTH_INIT = 100
		#utility function parameters
		self.PESTIEAU_ALPHA = None	#kc: sh_altruism
		self.PESTIEAU_GAMMA = None	#kc: sh_cons_1t
		#production function parameters
		self.PHI = 0.6	#kc: Capital share parameter for CD production fn.  Details not in Pestieau(1984)
		self.PSI = 0.4	#kc: Labor Share Paremeter for production fn.  Details not in PEstieau(1984)
		#LAST as an error check, lock against dynamic attribute creation (eventually remove TODO)
		self._locked = True
	def __setattr__(self, attr, val):
		'''Override __setattr__:
		no new attributes allowed after initialization.
		'''
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val 
	def compute_ability(self, indiv):
		return compute_ability_pestieau(indiv, beta=self.PESTIEAU_BETA, nbar=self.PESTIEAU_NBAR)  #TODO TODO


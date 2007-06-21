'''
Provides a collection of agents for replication of Pestieau (1984 OEP).

Indiv
	- Data: alive, sex, age, parents_bio, siblings, spouse, children, accounts,
	employers, economy, state, 
	- Methdods: receive_income, outgo, calc_wealth, calc_household_wealth, wed,
	bear_children, adopt, open_account, gift2kids, liquidate,
	distribute_estate, 

Cohort
	- Data:
	- Methdods:

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
	- Data:
	- Methdods:

State
	- Data:
	- Methdods:

'''


class Indiv:
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
		In Blinder model this is really "launch_child" (born 20 years before)?
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


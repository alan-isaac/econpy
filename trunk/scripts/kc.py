'''Module pestieau1984.py
Allows replication of Pestieau (1984).
'''
from __future__ import absolute_import
from __future__ import division
from random import random

from scripts_config import econpy #get access to econpy package
from econpy.abs.pestieau1984oep.agents import (Economy, State, Population, PestieauCohort, Indiv,  Fund, FundAcct, EconomyParams)#, PestieauParams)
from econpy.pytrix.iterate import IterativeProcess

#################################################################
#####################  additional imports #######################
#################################################################
import functools, itertools, random
from econpy.pytrix import utilities

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
	assert (not units)  #len shd be zero now
	print "Desired gini: ", gini, "   Achieved: ", utilities.calc_gini( i.calc_wealth() for i in units2 ), utilities.calc_gini2( i.calc_wealth() for i in units2 )

def sexer_randompairs(n):
	'''Yields n of each of two sexes, in pairs, in random order.
	Assumes from __future__ import division.
	'''
	sexgen = utilities.n_each_rand(n,itemtuple="MF")
	while True:
		yield sexgen.next() + sexgen.next()

#used as BEQUEST_FN by Indiv instances
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
		kids = [kid for kid in indiv.children if kid.alive]
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
		nsibs = len(mother.children)
		assert (nsibs>0)    #Pestieau p.407
		parents_ability = (father.ability + mother.ability)/2.0  #Pestieau p.412
		z = random.normalvariate(0.0,0.15)  #Pestieau p.413-414
		#Pestieau formula does not allow for zero kids??
		ability = beta*parents_ability + (1-beta)*nbar/nsibs + z #Pestieau p.407 (role of nbar is weird)
	except (TypeError, AttributeError):  #if indiv.parents_bio is None
		ability = random.normalvariate(1.0,0.15) #for initial cohort
	return ability

#################################################################
##########################  CLASSES  ############################
#################################################################

class PestieauParams(EconomyParams):
	def __init__(self):
		EconomyParams.__init__(self)
		self.Cohort = PestieauCohort
		self.N_YEARS = 1 
		self.COHORT_SIZE = 100  #p.413
		self.KID_AT_YEAR =  2   #see Population.evolve (no cohort has age 0!)
		self.ESTATE_TAX = None
		self.MATING = random
		#sex generator for new births
		self.KIDSEXGEN = sexer_randompairs         #TODO
		#number of Cohorts
		self.N_COHORTS = 2
		#initial Gini for Wealth
		self.GW0 = 0.5 #TODO TODO
		self.WEALTH_INIT = random.paretovariate(1)	#TODO TODO			#kc: random initial endowment, paper not explicit. p.413  
		self.BEQUEST_FN = bequests_blinder  #TODO TODO
		## NEW PARAMETERS  (Pestieau specific)
		self.PESTIEAU_BETA = 0.6										#kc: set regresion to mean ability parameter
		self.PESTIEAU_NBAR = None
		self.compute_ability = functools.partial(compute_ability_pestieau, beta=self.PESTIEAU_BETA, nbar=self.PESTIEAU_NBAR)
		self._locked = True
	def __setattr__(self, attr, val):
		'''Override __setattr__:
		no new attributes allowed after initialization.
		'''
		if not hasattr(self,attr) and getattr(self,'_locked',False) is True:
			raise ValueError("This object accepts no new attributes.")
		self.__dict__[attr] = val

####################################################################
# Example of a running economy: not a replication of Pestieau (1984)
####################################################################
print
print "#"*80
print " Example: Run Economy ".center(80,'#')
p = PestieauParams()
p.MATING = 'random'
e = Economy(p)
e.run()

############################### Next Steps ###############################
# Random Initial Wealth Endowment for the 1st cohort of 100: 
#	achieved in class PestieauParams() above
# Set up ability differences between parents and children:	
# 	set PESTIEAU_BETA = 0.6 above
# Set up utility max problem --> determines cons_1t, cons_2t, bequest)
# 	Need to develop factor prices as competitive process
# Make a new Bequest Function: Pestieau_bequest
# 
##########################################################################

def Pestieau_Bequest(indiv):
	'''Bequest fn for Pestieau model

	Equal Division (no primogeniture) Based on u-max with CD fn 
	'''
pass


def max_utility_const(indiv, sh_altruism, sh_cons_1t, sh_cons_2t, wage, bequest_rec,n_children, r_t):
	'''Return: float (utility).
	CD Utility function and constraints for consumption and bequest decisions, p.408-409
	
	:Parameters:
		sh_altruism : float
			Pestieau's prpoensity to leave bequests
		sh_cons_1t : float
			Pestieau's consumption share during working generation
		sh_cons_2t : float
			Pestieau's consumption share during non-working generation
		wage : float
			Peasieau's wage derived competitively
		bequest_rec: float
			Pestieau's bequest received by the current generation from the parents
		n_children : float
			Pestieau's number of children per couple
		r_t : float
			Pestieau's ROR on capital
		'''
	params = indiv.economy.params
	
	assert (sh_altruism + sh_cons_1t + sh_cons_2t == 1)  # check: fn homogenous of degree 1
	life_income = wage*ability
	life_weatlth = life_income + bequest_rec  # lifetime wealth is income + bequest received 
	life_cons_beq_2t = cons_1t + ( cons_2t + ( n_children * bequest_2t)/(1 + r_t) )  #lifetime consumption and bequest to children
	
	x = wage * ability + bequest_2t  # x is expected lifetime income of heirs: parents expect children to have = ability and income p.409
	
	u = (x**sh_altruism)*(cons_1t**sh_cons_1t)*(cons_2t**sh_cons_2t)  #define utility
	
	assert (life_weath == life_cons_beq)	# income/expenditure constraint
	
	#optimal values as parameters of the model using CD fn
	bequest_2t = ( (sh_altruism * (1 + r_t) )/n_children )*total_wealth - (1-sh_altruism)*life_income  #optimal bequest

	cons_1t = sh_cons_1t * ( bequest_rec + life_income*( (1 + r_t + n_children)/(1 + r_t) )	#optimal cons_1t

	cons_2t = (1 - sh_altruism - sh_cons_2t)* ( bequest_rec + life_income*( (1 + r_t + n_children)/(1 + r_t) )*(1 + r_t)  #optimal cons_2t


#******************************
#******** END 8-) *************
#******************************

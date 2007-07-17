'''Module kc.py
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
from econpy.abs.pestieau1984oep import agents

#################################################################
#########################  functions  ###########################
#################################################################
from econpy.abs.pestieau1984oep.agents import distribute, sexer_randompairs, bequests_blinder, compute_ability_pestieau



#################################################################
##########################  CLASSES  ############################
#################################################################

class KCPestieauParams(agents.PestieauParams):
	def __init__(self):
		agents.PestieauParams.__init__(self)
		self.WEALTH_INIT = random.paretovariate(1)	#TODO TODO			#kc: random initial endowment, paper not explicit. p.413  
		self.PESTIEAU_BETA = 0.6										#kc: set regresion to mean ability parameter
		self.PESTIEAU_NBAR = None
		self.compute_ability = functools.partial(compute_ability_pestieau, beta=self.PESTIEAU_BETA, nbar=self.PESTIEAU_NBAR)   #have to be careful with this: initialized once!


####################################################################
# Example of a running economy: not a replication of Pestieau (1984)
####################################################################
print
print "#"*80
print " Example: Run Economy ".center(80,'#')
p = agents.PestieauParams()
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

	#optimal cons_1t
	cons_1t = sh_cons_1t * ( bequest_rec + life_income*( (1 + r_t + n_children)/(1 + r_t) ))
	#optimal cons_2t
	cons_2t = (1-sh_altruism-sh_cons_2t) * ( bequest_rec + life_income*( (1 + r_t + n_children)/(1 + r_t) ))*(1 + r_t)


#******************************
#******** END 8-) *************
#******************************

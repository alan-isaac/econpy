'''Module kc.py
Allows replication of Pestieau (1984).
'''
from __future__ import absolute_import
from __future__ import division
from random import random

from scripts_config import econpy #get access to econpy package

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
		#ai: I do not thing this is what you want to do ... ? This is economy wide initial wealth.
		#kc: humm, I thought that this is economy wide initial wealth parameter...I will think about this.
		self.WEALTH_INIT = random.paretovariate(1)	#TODO TODO			#kc: random initial endowment, paper not explicit. p.413  
		self.PESTIEAU_BETA = 0.6										#kc: set regresion to mean ability parameter
		self.PESTIEAU_NBAR = None
		self.compute_ability = functools.partial(compute_ability_pestieau, beta=self.PESTIEAU_BETA, nbar=self.PESTIEAU_NBAR)   
		#have to be careful with this: initialized once!
		self.PESTIEAU_ALPHA = 0.7	#sh_altruism
		self.PESTIEAU_GAMMA = 0.2	#sh_cons_1t
		#together imply (1-alpha-gamma) for u-fn


####################################################################
# Example of a running economy: not a replication of Pestieau (1984)
####################################################################
print
print "#"*80
print " Example: Run Economy ".center(80,'#')
p = agents.PestieauParams()
p.MATING = 'random'
e = agents.Economy(p)
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
def max_utility_const(indiv, sh_altruism, sh_cons_1t, wage, bequest_rec,n_children, r_t):
	'''Return: float (utility).
	CD Utility function and constraints for consumption and bequest decisions, p.408-409
	
	:Parameters:
		sh_altruism : float
			Pestieau's prpoensity to leave bequests
		sh_cons_1t : float
			Pestieau's consumption share during working generation
		sh_cons_2t : float
			Pestieau's consumption share during non-working generation = (1-sh_altruism-sh_cons_1t)
		wage : float
			Peasieau's wage derived competitively
		bequest_rec: float
			Pestieau's bequest received by the current generation from the parents
		n_children : float
			Pestieau's number of children per couple
		r_t : float
			Pestieau's ROR on capital
		'''
	
	'''
	notes: 
	sh_altruism, sh_cons_1t, sh_cons_2t are globally defined parameters
	need access to bequest *received* by each parent for optimization below. could record this in the fund account??
	need wage and ability levels of parents -->pooled/averaged
	need n_children
	need r_t
	'''

	params = indiv.economy.params
	# could add an additional method in indiv class which records ability
	# this passes to firm? (or just done in Iniv) , which determined wage competitively
	
	bequest_rec = indiv.accounts[1]  # must modify account for detailed info. perhpas account[1] = bequest_rec #TODO
	n_children = len(indiv.children)
	
	#get pertinant family unit values:
	#family = [ ]	#TODO
	ability = parents_ability	#average	#TODO
	wage = parents_wage			#average	#TODO
	bequest_rec = parents_combinded_beq_rec	#TODO
	
	K_t = list()  # append family savings for next period capital stock. send to firm


	sh_cons_2t = 1-sh_altruism-sh_cons_1t  # could define this globally, but this gives us one less parameter
	assert (sh_altruism + sh_cons_1t + sh_cons_2t == 1)  # check: fn homogenous of degree 1

	life_income = wage*ability
	life_weatlth = life_income + bequest_rec  # lifetime wealth is income + bequest received 
	life_cons_beq_2t = cons_1t+( cons_2t+(n_children*bequest_2t)/(1 + r_t) )  #lifetime consumption and bequest to children
	assert (life_weath == life_cons_beq_2t)	# income/expenditure constraint
	x = life_income+bequest_2t  # x is expected lifetime income of heirs: parents expect children to have = ability and income p.409
	u = (x**sh_altruism)*(cons_1t**sh_cons_1t)*(cons_2t**sh_cons_2t)  #define utility function
	
	#optimal values as parameters of the model using CD fn: footnote p.409 and confirmed in pestieau1984background.tex
	#optimal bequest_2t (bequest *per*-child if total n_children): 
	bequest_2t = ( (sh_altruism*(1+r_t))/n_children )*life_wealth-(1-sh_altruism)*life_income  #optimal bequest
	#optimal cons_1t
	cons_1t = sh_cons_1t*( bequest_rec+life_income*((1+r_t+n_children)/(1+r_t)) )
	#optimal cons_2t
	cons_2t = (1-sh_altruism-sh_cons_1t)*( bequest_rec+life_income*((1+r_t+n_children)/(1+r_t)) )*(1+r_t)
	#optimal *addition* to capital stock on behalf of *family unit*: p. 409 (residual after consumption and savings) 
	k_t1 = (1-sh_cons_1t)*life_wealth - sh_cons_1t*((n_children*life_income)/(1+r_t)) 
	
	# k_t+1 *from each family* will be sent to the firm for aggregate production
	# K_t1 = SIGMA k_t1 to determine r_{t+1}


	# alternative, more general, from pestieau1984background.tex, where N = number of families in generation t
	# I don't think that we can say this, as optimal bequest and consumption is not proportional across all family units
	# due to ability differences
	N_k_t1 =N*( (1-sh_cons_1t)*life_wealth - sh_cons_1t*( (n_children*life_income)/(1+r_t) )  )

	

class Firm(object):
	def __init__(self):
		pass
	def worker_wage(self,ability):
		pass
	def return_to_capital(self):
		pass

class KCIndiv(agents.Indiv):
	pass

def Pestieau_Bequest(indiv):
	'''Bequest fn for Pestieau model

	Equal Division (no primogeniture) Based on u-max with CD fn 
	'''
	pass	
#******************************
#******** END 8-) *************
#******************************

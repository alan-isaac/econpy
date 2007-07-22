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

#logging
import logging
script_logger = logging.getLogger('script_logger')


#################################################################
#########################  functions  ###########################
#################################################################
from econpy.abs.pestieau1984oep.agents import distribute, sexer_randompairs, bequests_blinder, compute_ability_pestieau



#################################################################
##########################  CLASSES  ############################
#################################################################

class KCPestieauParams(agents.PestieauParams):
	def __init__(self):
		#kc: the following are ADDED parameters:
		self.PESTIEAU_ALPHA = None	#kc: sh_altruism
		self.PESTIEAU_GAMMA = None	#kc: sh_cons_1t
		#kc: together imply (1-alpha-gamma) for u-fn
		self.r_t = None	#kc: to let let Firm know that this is the initial period of the simulation
		self.PHI = 0.6	#kc: Capital share parameter for CD production fn.  Details not in Pestieau(1984)
		self.PSI = 0.4	#kc: Labor Share Paremeter for production fn.  Details not in Pestieau(1984)
		#MISSING PARAMETERS (not found in Pestieau 1984; see pestieau1984background.tex) recheck TODO
	
		agents.PestieauParams.__init__(self)  #ai: locks, so put any new params **before** this line
		self.WEALTH_INIT = 10000	#choice of 10,000 is random --> just different than # of agents in first cohort, for illustration
		self.PESTIEAU_BETA = 0.6	#kc: set regresion to mean ability parameter

####################################################################
# Example of a running economy: not a replication of Pestieau (1984)
####################################################################
#comment it out for now
'''
print
print "#"*80
print " Example: Run Economy ".center(80,'#')
p = agents.PestieauParams()
e = agents.Economy(p)
e.run()
print " END Example: Run Economy ".center(80,'#')
'''


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
	need r_t --> make initial ror in initialization
			 --> thereafter done by the firm
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
	
	K_t = list()  # append family savings for next period capital stock. send to firm? Send to FundAcct?


	sh_cons_2t = 1-sh_altruism-sh_cons_1t  # could define this globally, but this gives us one less parameter
	assert (sh_altruism + sh_cons_1t + sh_cons_2t == 1)  # check: fn homogenous of degree 1
	
	r_t = firm.clac_capital_ror() #does it make sense for a function to call methods in classes?

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
	k_1t = (1-sh_cons_1t)*life_wealth - sh_cons_1t*((n_children*life_income)/(1+r_t)) 
	
	# k_1t *from each family* will be sent to the firm for aggregate production
	# K_1t = SIGMA k_1t to determine r_{t+1}: recall E[r_t}] = r_{t-1} <or> E[r_{t+1}] = r_t
	
	
	# alternative, more general, from pestieau1984background.tex, where N = number of families in generation t
	# I don't think that we can say this, as optimal bequest and consumption is not proportional across all family units
	# due to ability differences
	N_k_t1 =N*( (1-sh_cons_1t)*life_wealth - sh_cons_1t*( (n_children*life_income)/(1+r_t) )  )

	
class KC_ECONOMY(agents.Economy):
		#ai: the next line **overrides** the agents.Economy initialization
	def __init__(self, params):
		self.initial_capital_stock = list()
		#ai: next, start by using the super classes initialization
		agents.Economy.__init__(self,params)
		#ai: now that those initializations are done, you can add some more
		
#		self.fund = Fund(self) 
		#ai: you probably do not want the next line (see line 543 of agents.py; just use self.funds[0])
#		self.fund =  agents.Fund(self) 

		self.initialize_capital_stock_ror()	
		self.initialize_labor_wage()
	def initialize_capital_stock_ror(self):
		script_logger.info("initialize capital stock ROR")
		#self.initial_capital_stock.append( self.fund.calc_accts_value() )	
		#K_0 = self.initial_capital_stock
		#ai: commenting out above ^
		#ai: try this instead
		#ai: BEGIN
		fund = self.funds[0]
		self.initial_capital_stock.append( fund.calc_accts_value() )
		params = self.params
		#ai: END
		# kc: the following is much more direct and substitutes for the above:
		K_0 = params.WEALTH_INIT
		L_0 = params.COHORT_SIZE
		assert (params.PHI + params.PSI == 1), "prod fn not homogenous degree 1"
		r_t = (params.PHI/K_0)*(K_0**params.PHI)*(L_0**params.PSI)
		print r_t
		return r_t
	def initialize_labor_wage(self):
		script_logger.info("initialize wage")
		params = self.params
		K_0 = params.WEALTH_INIT
		L_0 = params.COHORT_SIZE
		w_t = (params.PSI/L_0)*(K_0**params.PHI)*(L_0**params.PSI)
		print w_t
		return w_t

'''
class Firm(object):
	def __init__(self,economy):
		self.economy = economy
		self.params = economy.params
		self.capital_stock = list()
		self.labor = list()
	def calc_capital_ror(self, K_t, L_t):
		# CD pr-fn -> Y_t = (K_t**params.phi)*(L_t**params.psi)
		# NO RE: r_t = dF(K_{t+1},L_{t+1})/dK_{t+1}	!!
		if self.params.r_t == None:	# for initial period ONLY! 
			K_t = fund.calc_accts_value() #sum of initial wealth in model --> From Random initial endowment
			self.capital_stock.append(K_t)
			r_t = (params.phi/K_t)*(K_t**params.phi)*(L_t**params.psi)	 
			self.params.r_t = False  # is this an ok way of handling initialization -> dynamic typing?
			return r_t
		#timing is tricky here...
		else:
			pass 

	def worker_wage(self,ability):
		pass
'''


################
#More Examples #
################

print
print " Example: Run KC_Economy ".center(80,'#')
p1 = KCPestieauParams()
p1.MATING = 'random'
e1 = KC_ECONOMY(p1)
e1.run
print " END Example: Run KC_Economy ".center(80,'#')

#******************************
#******** END 8-) *************
#******************************

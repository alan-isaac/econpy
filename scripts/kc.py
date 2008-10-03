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
		self.WEALTH_INIT = 10000.0	# 10,000 is random --> just different than # of agents in first cohort
		self.PESTIEAU_BETA = 0.6	#kc: set regresion to mean ability parameter
		self.SHUFFLE_NEW_W = True	#kc: this should give us a random initial wealth endowment
									# gini now *always* 0.8 : this is random?
	
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
# Random Initial Wealth Endowment for the 1st cohort of 100 
#
# Set up ability differences between parents and children:	
# 	set PESTIEAU_BETA = 0.6 above
# Set up utility max problem --> determines cons_1t, cons_2t, bequest)
# 	Need to develop factor prices as competitive process
#		wages (initialization seperate)
#		capital_ror (initialization seperate)
# Set up Firm production
# 
##########################################################################
class KCIndiv(agents.PestieauIndiv):
	def __init__(self,economy=None, sex=None):
		#add list storing received bequest used by u-max fun: bequest_rec 
		self.bequest_rec = list()
		print "test"	# kc: not working...assume that other Indiv class is being used
		agents.Indiv.__init__(self,economy=None,sex=None)
	
#def max_utility_const(indiv, sh_altruism, sh_cons_1t, wage, bequest_rec, n_children, r_t):
def max_utility_const(indiv):
	'''Return: float (con_1t, cons_2t, bequest_2t, K_2t).
	CD Utility function and constraints for consumption and bequest decisions, p.408-409
	Governs *optimal* consumption/savings, bequest and consequent next period capital stock. 	

	:Parameters:
		*sh_altruism : float
			Pestieau's prpoensity to leave bequests
		*sh_cons_1t : float
			Pestieau's consumption share during working generation
		*sh_cons_2t : float
			Pestieau's consumption share during non-working generation = (1-sh_altruism-sh_cons_1t)
		**wage : float
			Peasieau's wage derived competitively
		***n_children : float
			Pestieau's number of children per couple
		**r_t : float
			Pestieau's ROR on capital. (not used w/ RE in optimization)

		"*"   Identifies Globally defined parameters
		"**"  Computed by economy class
		"***" Computed by Indiv class
		'''
	'''
	X need r_t --> make initial ror in initialization. Need to pass this to function from Economy initialization
			--> thereafter done by the Economy (or firm?)
			 		More general at the economy level (possible introduction of new firms)
	'''
	
	k_t = list()  # append family savings for next period capital stock. send to firm? Send to FundAcct?
	
	# could add an additional method in indiv class which records list ability	?

	#access to global parameters
	params = indiv.economy.params   
	#define local parameters from global definitions.
	sh_altruism = params.ALPHA
	sh_cons_1t = params.GAMMA
	sh_cons_2t = 1-sh_altruism-sh_cons_1t  # could define this globally, but this gives us one less parameter
	assert (sh_altruism + sh_cons_1t + sh_cons_2t == 1)  # check: fn homogenous of degree 1

	# ROR
	r_t = economy.calc_ror()
	#Wage
	wage = economy.calc_wage()

	#### couple/family data
	children =  indiv.get_children() 
	n_children = len(children)
	#similar procedure as in compute_ability function
	father, mother = indiv.parents_bio
	parents_ability = ( father.abiliy + mother.ability )/2.0
	ability = parents_ability
	parents_life_income = ability*wage
	life_income = parents_life_income
	parents_life_wealth = father.calc_wealth + mother.calc_wealth
	life_wealth = parents_life_wealth	# for family consumption and bequest problem

	life_cons_beq_2t = cons_1t+( cons_2t+(n_children*bequest_2t)/(1+r_t) )  # discounted lifetime family consumption and bequest to children
	assert (life_weath == life_cons_beq_2t)	# income/expenditure constraint
	#x = life_income+bequest_2t  # x is expected lifetime income of heirs: parents expect children to have = ability and income p.409
	#u = (x**sh_altruism)*(cons_1t**sh_cons_1t)*(cons_2t**sh_cons_2t)  #define utility function

	#optimal values as parameters of the model using CD fn: footnote p.409 and confirmed in pestieau1984background.tex
	#optimal bequest_2t (bequest *per*-child if total n_children): 
	bequest_2t = ( (sh_altruism*(1+r_t))/n_children )*life_wealth-(1-sh_altruism)*life_income  #optimal bequest
	return bequest_2t
	#optimal cons_1t
	cons_1t = sh_cons_1t*( life_wealth+(life_income*n_children)/(1+r_t) ) 
	return cons_1t
	#optimal cons_2t
	cons_2t = (1-sh_altruism-sh_cons_1t)*( life_wealth+(life_income*n_children)/(1+r_t) )
	return cons_2t
	
	#optimal *addition* to capital stock on behalf of *family unit*: p. 409 (residual after consumption and savings) 
	k_1t = (1-sh_cons_1t)*life_wealth - sh_cons_1t*( (n_children*life_income)/(1+r_t) ) 
	k_t.append(k_1t)
	return k_1t
	# k_1t *from each family* will be sent to the firm for aggregate production (next period capital stock)
	# K_1t = SIGMA k_1t to determine r_{t+1}: recall E[r_t}] = r_{t-1} <or> E[r_{t+1}] = r_t
	
	
	# alternative, more general, from pestieau1984background.tex, where N = number of families in generation t
	# I don't think that we can say this, as optimal bequest and consumption is not proportional across all family units
	# due to ability differences
	N_k_t1 =N*( (1-sh_cons_1t)*life_wealth - sh_cons_1t*( (n_children*life_income)/(1+r_t) )  )

	
class KC_ECONOMY(agents.PestieauEconomy):
		#ai: the next line **overrides** the agents.Economy initialization
	def __init__(self, params):
		self.initial_capital_stock = list()
		self.capital_ror = list()
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
		assert (params.PHI + params.PSI == 1), "production fn NOT homogenous degree 1"
		r_0 = (params.PHI/K_0)*(K_0**params.PHI)*(L_0**params.PSI)
		self.capital_ror.append(r_0)
		print r_0
		return r_0
	def initialize_labor_wage(self):
		script_logger.info("initialize labor wage")
		params = self.params
		K_0 = params.WEALTH_INIT
		L_0 = params.COHORT_SIZE
		w_0 = (params.PSI/L_0)*(K_0**params.PHI)*(L_0**params.PSI)
		print w_0
		return w_0
		
	def calc_ror(self):
		# used by u_max function 
		# note: ROR_t computed using L_{t+1} and K_{t+1}. p.408
		script_logger.info("ROR")
		fund = self.funds[0]
		self.params = params
		#self.capital_stock.append( fund.calc_accts_value() )  #assumes all saved *capital* from last period has been added to fund
		K_t = fund.calc_accts_value() #kc: *ASSUMES* all saved *capital* from last period has been added to fund
		L_t = len( ppl.get_labor_force() ) 
		r_t = (params.PHI/K_t)*(K_t**params.PHI)*(L_t**params.PSI)
		self.capital_ror.append(r_t)
		assert(len(self.capital_ror) >=1), "no ROR recorded"
		if len(self.capital_ror) == 1: # for second period: return initial period (initialized) ROR 
			return self.capital_ror[0] 
		else:
			return self.capital_ror[-2] #return last period ROR for consumption/bequest decisions 
	
	def calc_wage(self):
		#used by u_max function 
		script_logger.info("Wage")
		fund = self.funds[0]
		self.params = params
		K_t = fund.calc_accts_value()  # assumes previous period capital stock has been sent to Firm
		L_t = len( ppl.get_labor_force() ) 
		w_t = (params.PSI/L_t)*(K_t**params.PHI)*(L_t**params.PSI) 
		self.labor_wage.append(w_t)
		return w_t	#note that contemporanious wages are used in consumpiton/bequest decisions
'''			
class Firm(object):
	def __init__(self,economy):
		self.economy = economy
		self.params = economy.params
		self.capital_stock = list()
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
p1.MATING = 'classonly_unisex'
e1 = KC_ECONOMY(p1)
e1.run()
print e1.final_report()
print " END Example: Run KC_Economy ".center(80,'#')

#******************************
#******** END 8-) *************
#******************************

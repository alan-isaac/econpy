'''Module pestieau1984.py
Allows replication of Pestieau (1984).
'''

from __future__ import absolute_import
from __future__ import division
from random import random

from scripts_config import econpy #get access to econpy package
from econpy.abs.pestieau1984oep.agents import Indiv, PestieauCohort, Population, Fund, FundAcct
from econpy.pytrix.iterate import IterativeProcess

#for now, this is just illustrative; it's not "doing" anything

COHORT_SIZE = 10	# indiv in cohort
N_COHORTS = 5
print
print '1.###############################' 
print
individuals = [ Indiv(economy=None,sex=s) for i in range(COHORT_SIZE//2) for s in "MF" ]
print 'sex of indiv in cohort  :',''.join(ind.sex for ind in individuals)
print
print '2.###############################'
print
cohort = PestieauCohort(individuals)
print "Cohort element (an Indiv):"
print cohort[0]
print
print '3.###############################' 
print

ppl = Population(PestieauCohort(Indiv(economy=None,sex=s) for i in range(COHORT_SIZE//2) for s in "MF") for j in range(N_COHORTS))
print "Pop element (a cohort, i.e., tuple of Indivs):"
print ppl[0]
print
print '4.###############################' 
print


#KC: just practice getting the classes do so something (not much yet, just testing my understanding):
#first age the cohort 5 periods 
#then receive income (7 units) for deposit and calculate wealth each period
fnd = Fund(individuals)
fndacct = FundAcct(fnd, individuals)
amt = 7

for t in range(5):
	for cohort in ppl:
#		cohort.set_age(age)
		cohort.age_cohort()
		print 'cohort i age is:', cohort._cohort_age  #make i a parameter 
		for ind in cohort:
			ind.open_account
#			ind.receive_income(amt)	# not sure why I get a out of range error here
#			ind.calc_wealth()
			print '	acct for ind j in cohort i:', ind.accounts	#make j a parameter 
print
print '###############################' 
print




#******************************
#******** END ;-) *************
#******************************


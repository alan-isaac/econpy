'''Module pestieau1984.py
Allows replication of Pestieau (1984).
'''
from __future__ import absolute_import
from __future__ import division
from random import random

from scripts_config import econpy #get access to econpy package
from econpy.abs.pestieau1984oep.agents import (Economy, State, Population, PestieauCohort, Indiv,  Fund, FundAcct, PestieauParams)
from econpy.pytrix.iterate import IterativeProcess

#for now, this is just illustrative; it's not "doing" anything
'''
COHORT_SIZE = 10	# indiv in cohort
N_COHORTS = 5

print
print "#"*80
print " Example: Create Cohort of Indivs ".center(80,'#')
cohort = PestieauCohort( Indiv(economy=None,sex=s) for i in range(COHORT_SIZE//2) for s in "MF" )
print 'sex of indiv in cohort  :',''.join(ind.sex for ind in cohort)

print "#"*80
print " Example: Create Population ".center(80,'#')
ppl = Population( PestieauCohort( Indiv(economy=None,sex=s) for i in range(COHORT_SIZE//2) for s in "MF") for j in range(N_COHORTS) )
print "Type of pop element (shd be a cohort): ", type(ppl[0])


print
print "#"*80
print " Example: Create Fund to hold Accounts ".center(80,'#')
p = PestieauParams()
p.MATING = 'random'
e = Economy(p)
fnd = Fund(e)

print
print "#"*80
print " Initialize Cohort Ages ".center(80,'#')
age = N_COHORTS
for cohort in ppl:
	cohort.set_age(age)
	for indiv in cohort:
		indiv.open_account(fnd, 100/age)
	age -= 1

print
print "#"*80
print " Example of Aging ".center(80,'#')
for t in range(5):
	print 'period %d:' %(t)
	for i, cohort in enumerate(ppl):
		cohort.age_cohort()
		for ind in cohort:
			#ind.open_account  #already initialized
			ind.receive_income(100)
		print "Indiv 0 of cohort %d has age %d and wealth of %5.2f."%( i, cohort[0].age, ind.calc_wealth() )
	print
'''

print
print "#"*80
print " Example: Run Economy ".center(80,'#')
p = PestieauParams()
p.MATING = 'random'
e = Economy(p)
e.run()

#******************************
#******** END ;-) *************
#******************************

'''Module pestieau1984.py
Allows replication of Pestieau (1984).
'''
from __future__ import absolute_import
from __future__ import division
from random import random

from scripts_config import econpy #get access to econpy package
from econpy.abs.pestieau1984oep.agents import (PestieauEconomy, State, Population, PestieauCohort, Indiv,  Fund, FundAcct, PestieauParams)
from econpy.pytrix.iterate import IterativeProcess

#for now, this is just illustrative; it's not "doing" anything

COHORT_SIZE = 10	# indiv in cohort
N_COHORTS = 5

print
print "#"*80
print " Create Indivs ".center(80,'#')
individuals = [ Indiv(economy=None,sex=s) for i in range(COHORT_SIZE//2) for s in "MF" ]
print 'sex of indiv in cohort  :',''.join(ind.sex for ind in individuals)

print
print "#"*80
print " Create Cohort ".center(80,'#')
cohort = PestieauCohort(individuals)
print "Cohort element (an Indiv): ", cohort[0]

print "#"*80
print " Create Population ".center(80,'#')
ppl = Population( PestieauCohort( Indiv(economy=None,sex=s) for i in range(COHORT_SIZE//2) for s in "MF") for j in range(N_COHORTS) )
print "Type of pop element (shd be a cohort): ", type(ppl[0])


#KC: just practice getting the classes do so something (not much yet, just testing my understanding):
#first age the cohort 5 periods 
#then receive income (7 units) for deposit and calculate wealth each period

print
print "#"*80
print " Create Fund with Accounts ".center(80,'#')
p = PestieauParams()
p.MATING = 'random'
e = PestieauEconomy(p)
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

#******************************
#******** END ;-) *************
#******************************

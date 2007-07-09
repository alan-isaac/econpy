'''Module pestieau1984.py
Allows replication of Pestieau (1984).
'''
from __future__ import absolute_import
from __future__ import division
from random import random

from scripts_config import econpy #get access to econpy package
from econpy.abs.pestieau1984oep.agents import Indiv, PestieauCohort, Population, Fund, FundAcct, Economy
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
ppl = Population(PestieauCohort(Indiv(economy=None,sex=s) for i in range(COHORT_SIZE//2) for s in "MF") for j in range(N_COHORTS))
print "Type of pop element (shd be a cohort): ", type(ppl[0])


#KC: just practice getting the classes do so something (not much yet, just testing my understanding):
#first age the cohort 5 periods 
#then receive income (7 units) for deposit and calculate wealth each period

print "#"*80
print " Create Fund with Accounts ".center(80,'#')
e = Economy()
fnd = Fund(e)

print "#"*80
print " Initialize Cohort Ages ".center(80,'#')
age = 0
for cohort in ppl:
	age += 1
	cohort.set_age(age)
	for indiv in cohort:
		indiv.open_account(fnd, 100/age)


for t in range(5):
	print
	for cohort in ppl:
		cohort.age_cohort()
		for i, ind in enumerate(cohort):
			#ind.open_account  #already initialized
			ind.receive_income(100)	# not sure why I get a out of range error here
			print "Indiv %d has wealth of %5.2f."%(i,ind.calc_wealth()) ,
	print




#******************************
#******** END ;-) *************
#******************************


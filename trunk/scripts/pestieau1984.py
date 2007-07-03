from __future__ import absolute_import
from __future__ import division
from random import random

from scripts_config import econpy #get access to econpy package
from econpy.abs.pestieau1984oep.agents import Indiv, PestieauCohort, Population
from econpy.pytrix.iterate import IterativeProcess

#for now, this is just illustrative; it's not "doing" anything
COHORT_SIZE = 50
N_COHORTS = 10
individuals = [ Indiv(economy=None,sex=s) for i in range(COHORT_SIZE//2) for s in "MF" ]
print ''.join(ind.sex for ind in individuals)
cohort = PestieauCohort(individuals)
print "Cohort element (an Indiv):"
print cohort[0]
ppl = Population(PestieauCohort(Indiv(economy=None,sex=s) for i in range(COHORT_SIZE//2) for s in "MF") for j in range(N_COHORTS))
print "Pop element (a cohort, i.e., tuple of Indivs):"
print ppl[0]


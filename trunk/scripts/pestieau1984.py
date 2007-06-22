from __future__ import division
from __future__ import absolute_import
from random import random

#get access to econpy package
import sys
sys.path.insert(0,'/econpy')
from abs.pestieau1984oep.agents import Indiv

#from agents import calc_gini
COHORT_SIZE = 50
individuals = [ Indiv(economy=None,sex=s) for i in range(COHORT_SIZE//2) for s in "MF" ]
print ''.join(ind.sex for ind in individuals)


'''
Unit tests for Pestieau replication.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
from __future__ import absolute_import
import unittest
import random

from tests_config import econpy  #tests_config.py modifies sys.path to find econpy
from econpy.abs.pestieau1984oep import agents
from econpy.pytrix import utilities, iterate, fmath



class testPestieau(unittest.TestCase):
	def setUp(self):
		self.N = 5
		self.wealths = [random.random() for _ in range(2*self.N)]
		self.indivs = [agents.PestieauIndiv(sex=x) for x in "MF"*self.N]
	'''
	def test_match_exclude(self):
		males = self.indivs[:2]
		females = self.indivs[-2:]
		for i in range(2):
			males[i].siblings.add(females[i])
			females[i].siblings.add(males[i])
		mf = blindermodel.match_exclude(males,females, lambda x,y: x in y.siblings)
		self.assertEqual(mf , [(males[0],females[1]),(males[1],females[0])] )
	def test_match_exclude2(self):
		g1 = range(5)
		g2 = range(5)
		random.shuffle(g2)
		mf = blindermodel.match_exclude(g1,g2, lambda x,y: x != y)
		self.assertEqual(mf , [(0,0),(1,1),(2,2),(3,3),(4,4)] )
	def test_random2sexer(self):
		s = blindermodel.random2sexer(10)
		for si in s:
			self.assert_(si in ['MM','MF','FM','FF'])
	'''
	def test_ability(self):
		indiv = self.indivs[0]
		ability = agents.compute_ability_pestieau(indiv, 0.5, 2)
		#TODO
	def test_PestieauCohort(self):
		indivs = self.indivs
		cohort = agents.PestieauCohort(indivs)
		self.assertEqual(len(cohort),len(indivs))
		for i in indivs:
			self.assert_(i.sex in "MF")
	def test_Fund(self):
		fund = agents.Fund(None)  #usu want association w economy
		fund._accounts = [agents.FundAcct(fund, self.indivs[i], self.wealths[i]) for i in range(self.N)]
		for i in range(self.N):
			self.assertEqual(fund._accounts[i]._value, self.wealths[i])

if __name__=="__main__":
	unittest.main()


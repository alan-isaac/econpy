'''Module pestieau1984.py
Will eventually replicate Pestieau (1984).
'''
from __future__ import absolute_import
from __future__ import division
__docformat__ = "restructuredtext en"
__version__ = "0.01"

from random import random

from scripts_config import econpy, script_logger #get access to econpy package
from econpy.abs.pestieau1984oep import agents
from econpy.pytrix.iterate import IterativeProcess

#for now, this is just illustrative; it's not "doing" anything

COHORT_SIZE = 10	# indiv in cohort
N_COHORTS = 5

'''
print
print "#"*80
print " Example: Create Cohort of Indivs ".center(80,'#')
cohort = agents.PestieauCohort( agents.Indiv(sex=s, economy=None) for i in range(COHORT_SIZE//2) for s in "MF" )
print 'sex of indiv in cohort  :',''.join(ind.sex for ind in cohort)

print "#"*80
print " Example: Create Population ".center(80,'#')
ppl = agents.Population( agents.PestieauCohort( agents.Indiv(sex=s, economy=None) for i in range(COHORT_SIZE//2) for s in "MF") for j in range(N_COHORTS) )
print "Type of pop element (shd be a cohort): ", type(ppl[0])


print
print "#"*80
print " Example: Create Fund to hold Accounts ".center(80,'#')
p = agents.PestieauParams()
p.MATING = 'random'
e = agents.Economy(p)
fnd = agents.Fund(e)

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


def main():

	import sys, logging
	#set default output for logging
	output = sys.stdout
	
	from optparse import OptionParser
	
	usage = """
	usage: %prog [options]
	standard usage: %prog --very_verbose --logfile=temp.log
	"""

	parser = OptionParser(usage=usage, version ="%prog " + __version__)

	parser.add_option("-l", "--logfile", action="store", type="string", dest="logfile",
					  help="Parse FILE for citation references.", metavar="FILE")
	parser.add_option("-n", "--nuke", action="store_true", dest="overwrite", default=True,
					  help="silently overwrite logfile, default=%default")
	parser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False,
					  help="Print only ERROR messages to stdout, default=%default")
	parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
					  help="Print INFO messages to stdout, default=%default")
	parser.add_option("-V", "--very_verbose", action="store_true", dest="very_verbose", default=False,
					  help="Print DEBUG messages to stdout, default=%default")

	(options, args) = parser.parse_args()
	print options, args
	if options.quiet:
		script_logger.setLevel(logging.ERROR)
	elif options.verbose:
		script_logger.setLevel(logging.INFO)
	elif options.very_verbose:
		script_logger.setLevel(logging.DEBUG)
	else:
		script_logger.setLevel(logging.WARN)

	# open output file for writing (default: stdout)
	if options.logfile:
		if os.path.exists(options.logfile) and not options.overwrite:
			print "File %s exists:  use -n option to nuke (overwrite) this file."%(options.outfile)
			sys.exit(1)
		output = open(options.logfile,'w')

	print
	print "#"*80
	print " Example: Run Economy ".center(80,'#')
	p = agents.PestieauParams()
	p.PESTIEAU_BETA = 0.7
	e = agents.PestieauEconomy(p)
	e.run()


if __name__ == '__main__':
	main()

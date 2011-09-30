""" Template Model 8: Log Model State Information to File """

from gridworld import describe
from template07 import *
params.update(logfile='c:/temp/sizes.csv', logformat='\n{min}, {mean}, {max}')

class World08(World05):
	def setup(self):
		World05.setup(self)
		self.header2logfile() # write header to logfile
	def header2logfile(self):
		with open(params['logfile'], 'w') as fout:
			fout.write('minimum, mean, maximum')
	def log2logfile(self):
		agents = self.get_agents(self.AgentType)
		sizes = list(agent.size for agent in agents)
		stats = describe(sizes)
		with open(params['logfile'], 'a') as fout:
			fout.write(params['logformat'].format(**stats))
	def schedule(self):
		self.log2logfile()
		World05.schedule(self)
		if max(agent.size for agent in self.agents) >= 100:  #from model 7
			self.log2logfile()    #log final agent state
			self.stop(exit=True)

if __name__ == '__main__':
	myworld = World08(topology=TorusGrid(shape=params['world_shape']))
	myobserver = GUI06(myworld)
	myobserver.mainloop()

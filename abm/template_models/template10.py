""" Template Model 10: Hierarchy """

from template09 import *

class World10(World08):
	def sortkey10(self, agent):
		return agent.size
	def schedule(self):
		self.log2logfile()                                #from model 8
		ask(self.patches, 'produce')                      #from model 3
		agents = self.get_agents(self.AgentType)
		agents.sort(key=self.sortkey10, reverse=True)     #model 10
		ask(agents, 'move')                               #from model 1
		ask(agents, 'change_size')                        #from model 3
		if max(agent.size for agent in agents) >= 100:    #from model 7
			self.log2logfile()                            #from model 8
			self.stop(exit=True)

if __name__ == '__main__':
	myworld = World10(topology=TorusGrid(shape=params['world_shape']))
	myobserver = GUI06(myworld)
	myobserver.mainloop() 

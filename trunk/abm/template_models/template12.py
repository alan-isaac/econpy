""" Template Model 12: Entry and Exit """

from template11 import *
params.update(agent_exit_probability=0.05)

class Agent12(Agent11):
	def split_if_ready(self):
		if self.size > 10:
			self.propagate()
			self.die()
	def propagate(self):
		MyType = self.__class__                       #splits share agent class
		hood4split = self.neighborhood('moore', radius=3)
		cells4split = list()
		for i in range(5):                            #5 propagation attempts
			for cell in random.sample(hood4split, 5):   #5 tries per attempt
				if cell not in cells4split and not cell.get_agents(MyType):
					cells4split.append(cell)
					break
		splitlocs = list(cell.position for cell in cells4split)
		splits = self.world.create_agents(MyType, locations=splitlocs)
		return splits
	def venture(self):
		if random.uniform(0,1) < params['agent_exit_probability']:
			self.die()

class World12(World11):
	AgentType = Agent12
	def schedule(self):
		World11.schedule(self)
		agents = self.get_agents(self.AgentType)
		askrandomly(agents, 'split_if_ready')     #creates new entrants
		agents = self.get_agents(self.AgentType)  #include new entrants
		ask(agents, 'venture')
		if (self.iteration==1000) or (len(agents)==0):    #model 12
			self.log2logfile()                              #from model 8
			self.stop()

if __name__ == '__main__':
	myworld = World12(topology=TorusGrid(shape=params['world_shape']))
	myobserver = GUI06(myworld)
	myobserver.mainloop() 

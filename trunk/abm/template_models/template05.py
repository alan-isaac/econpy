""" Template Model 5: Parameter Interface """

from template04 import *

class Agent05(Agent03):
	def initialize(self):
		Agent03.initialize(self)
		self.max_extract = self.world.agent_max_extract

class World05(World03):
	AgentType = Agent05
	PatchType = Cell03
	n_agents = params['n_agents']
	agent_max_extract = params['agent_max_extract']
	def setup(self):
		self.setup_patches()
		self.setup_agents()
	def setup_patches(self):
		self.create_patches(self.PatchType)
	def setup_agents(self):
		self.create_agents(self.AgentType, number=self.n_agents)

class GUI05(GUI04):
	def gui(self):
		GUI04.gui(self)
		self.add_slider('Initial Number of Bugs', 'n_agents', 10, 500, 10)
		self.add_slider('Agent Max Extract', 'agent_max_extract', 0.0, 2.0, 0.1)
		self.add_button('Set Up', 'setup')
		self.add_button('Run', 'run')
		self.add_button('Stop', 'stop')

if __name__ == '__main__':
	myworld = World05(topology=TorusGrid(shape=params['world_shape']))
	myobserver = GUI05(myworld)
	myobserver.mainloop()

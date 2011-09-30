""" Template Model 2: Dynamic Agent State """

from time import sleep
from gridworld import ask
from template01 import *
params.update(agent_initial_size=0.0, extraction_rate=0.1)

class Agent02(Agent01):
	def initialize(self):
		self.size = params['agent_initial_size']
		self.display(shape='circle', shapesize=(0.25,0.25))
		self.change_color()
	def change_size(self):
		self.size += self.extract()
		self.change_color()
	def extract(self):
		return params['extraction_rate']
	def change_color(self):
		g = b = max(0.0, 1.0 - self.size/10)
		self.display(fillcolor=(1.0, g, b))

class World02(GridWorld):
	def schedule(self):
		sleep(0.2)
		ask(self.agents, 'move')
		ask(self.agents, 'change_size')

if __name__ == '__main__':
	myworld = World02(topology=TorusGrid(shape=params['world_shape']))
	myagents = myworld.create_agents(Agent02, number=params['n_agents'])
	myobserver = GridWorldGUI(myworld)
	myworld.run(maxiter=params['maxiter'])
	myobserver.mainloop()       # keep GUI open after `run` completes

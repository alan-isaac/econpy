""" Template Model 1: Random Movement on a Toroidal Grid """ 

import random
from gridworld import Agent, TorusGrid, GridWorld
from gridworld import moore_neighborhood, GridWorldGUI
params = dict(world_shape=(100,100), n_agents=100, maxiter=100)

class Agent01(Agent):
	def move(self):
		choice = self.choose_location()
		self.position = choice
	def choose_location(self):
		old_position = self.position
		hood = moore_neighborhood(radius=4, center=old_position)
		random.shuffle(hood)
		for location in hood:
			if  self.world.is_empty(location):
				return location
		return old_position

class World01(GridWorld):
	def schedule(self):
		for agent in self.agents:
			agent.move()

if __name__ == '__main__':                   #setup and run the simulation
	mygrid = TorusGrid(shape=params['world_shape'])
	myworld = World01(topology=mygrid)
	myagents = myworld.create_agents(AgentType=Agent01, number=params['n_agents'])
	for agent in myagents:
		agent.display(shape='circle', fillcolor='red', shapesize=(0.25,0.25))
	observer = GridWorldGUI(myworld)
	myworld.run(maxiter=params['maxiter'])   #run the schedule repeatedly

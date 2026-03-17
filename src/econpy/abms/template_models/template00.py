""" Template Model 1 (procedural): Random Movement on a Toroidal Grid """

import random
from gridworld import Agent, TorusGrid, GridWorld
from gridworld import moore_neighborhood, GridWorldGUI

params = dict(world_shape=(100,100), n_agents=100, maxiter=100)

def move(agent):
	choice = choose_location(agent)
	agent.position = choice

def choose_location(agent):
	old_position = agent.position
	hood = moore_neighborhood(radius=4, center=old_position)
	random.shuffle(hood)
	for location in hood:
		if agent.world.is_empty(location):
			return location
	return old_position

def schedule():
	for agent in myagents:
		move(agent)

def run(maxiter):
	for ct in range(maxiter):
		myobserver.off()
		schedule()
		myobserver.on()

#create a grid and a world based on this grid
mygrid = TorusGrid(shape=params['world_shape'])
myworld = GridWorld(topology=mygrid)
#create agents, located in `myworld`, and then set display suggestions
myagents = myworld.create_agents(AgentType=Agent, number=params['n_agents'])
for agent in myagents:
	agent.display(shape='circle', fillcolor='red', shapesize=(0.25,0.25))
#add an observer
myobserver = GridWorldGUI(myworld)
#run the simulation by repeatedly executing the schedule
run(maxiter=params['maxiter'])

""" Template Model 13: Time-Series Plot """

from template12 import *

class GUI13(GUI06):
	def gui(self):
		GUI06.gui(self)
		def number_living():
			world = self.subject
			return len(world.get_agents(world.AgentType))
		self.add_plot('Number of Agents', number_living)

if __name__ == '__main__':
	myworld = World12(topology=TorusGrid(shape=params['world_shape']))
	myobserver = GUI13(myworld)
	myobserver.mainloop() 

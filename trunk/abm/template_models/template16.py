""" Template Model 16: Interacting Agents of Different Types """

from template15 import *

class Hunter(Agent):
	def initialize(self):
		self.display(fillcolor='yellow', shapesize=(0.75,0.75))
	def hunt(self):
		hunthood = self.neighborhood('moore', radius=1, keepcenter=True)
		random.shuffle(hunthood)
		change_position = True
		for patch in hunthood:
			hunters = patch.get_agents(AgentType=Hunter)
			gatherers = patch.get_agents(Agent12)
			if hunters and not self in hunters:
				change_position = False
				break
			elif gatherers:
				gatherers.pop().die()
				self.position = patch.position
				change_position = False
				break
		if change_position: #encountered no gatherers nor hunters
			newcell = random.choice(hunthood)
			self.position = newcell.position

class World16(World15):
	def schedule(self):
		World15.schedule(self)
		hunters = self.get_agents(Hunter)
		askrandomly(hunters, 'hunt')
	def setup(self):
		World15.setup(self)
		hunter_locations = self.random_locations(200)
		hunters = self.create_agents(Hunter, locations=hunter_locations)

if __name__ == '__main__':
	myworld = World16(topology=TorusGrid(shape=params['world_shape']))
	myobserver = GUI14(myworld)
	myobserver.mainloop() 

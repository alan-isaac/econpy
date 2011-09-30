""" Template Model 7: Stopping Condition """

from template06 import *

class World07(World05):
	def schedule(self):
		World05.schedule(self)
		if max(agent.size for agent in self.agents) >= 100:
			self.stop(exit=True)

if __name__ == '__main__':
	myworld = World07(topology=TorusGrid(shape=params['world_shape']))
	myobserver = GUI06(myworld)
	myobserver.mainloop()

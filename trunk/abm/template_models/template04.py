""" Template Model 4: Probe Object State """

from template03 import *

class GUI04(GridWorldGUI):
	def gui(self):
		self.add_clickmonitor('Agent', Agent03, 'size')
		self.add_clickmonitor('Cell', Cell03, 'supply')

if __name__ == '__main__':
	myworld = World03(topology=TorusGrid(shape=params['world_shape']))
	mypatches = myworld.create_patches(Cell03)  #setup patches
	myagents = myworld.create_agents(Agent03, number=params['n_agents'])
	myobserver = GUI04(myworld)
	myworld.run(maxiter=params['maxiter'])
	myobserver.mainloop()

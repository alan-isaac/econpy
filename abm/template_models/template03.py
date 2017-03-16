""" Template Model 3: Spatially Distributed Resources """

from gridworld import Patch
from template02 import *
params.update(cell_initial_supply=0.0, cell_max_produce=0.01)
params.update(agent_max_extract=1.0)

class Cell03(Patch):
    max_produce = params['cell_max_produce']
    supply = params['cell_initial_supply']
    def produce(self):
        self.supply += random.uniform(0, self.max_produce)
    def provide(self, amount):
        amount = min(self.supply, amount)
        self.supply -= amount
        return amount

class Agent03(Agent02):
    max_extract = params['agent_max_extract']
    def extract(self):
        mytake = self.patch.provide(self.max_extract)
        return mytake
 
class World03(GridWorld):
    def schedule(self):
        ask(self.patches, 'produce')
        ask(self.agents, 'move')
        ask(self.agents, 'change_size')

if __name__ == '__main__':
    myworld = World03(topology=TorusGrid(shape=params['world_shape']))
    mypatches = myworld.create_patches(Cell03)  #setup patches
    myagents = myworld.create_agents(Agent03, number=params['n_agents'])
    myobserver = GridWorldGUI(myworld)
    myworld.run(maxiter=params['maxiter'])
    myobserver.mainloop()

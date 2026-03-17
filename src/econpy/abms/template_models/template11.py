""" Template Model 11: Optimization """

from gridworld import maximizers
from template10 import *

class Agent11(Agent05):
    def sortkey11(self, cell):
        return cell.supply
    def choose_location(self):
        MyType = self.__class__
        hood = self.neighborhood('moore', 4)  #get the neighboring cells
        available = [cell for cell in hood if not cell.get_agents(MyType)]
        available.append(self.patch)           #agent can always stay put
        best_cells = maximizers(self.sortkey11, available)
        if self.patch in best_cells:
            return self.position
        else:
            return random.choice(best_cells).position

class World11(World10):
    AgentType = Agent11

if __name__ == '__main__':
    myworld = World11(topology=TorusGrid(shape=params['world_shape']))
    myobserver = GUI06(myworld)
    myobserver.mainloop() 

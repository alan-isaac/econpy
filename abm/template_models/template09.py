""" Template Model 9: Randomized Agent Actions """

from gridworld import askrandomly
from template08 import *

class World09(World08):
    def schedule(self):
        self.log2logfile()  #version 8 adds logging
        ask(self.patches, 'produce')
        #version 9: agents move in random order
        askrandomly(self.agents, 'move')
        ask(self.agents, 'change_size')
        #consistency chk: no two agents should share a position
        assert len(set(a.position for a in self.agents))==len(self.topology)
        #version 7 adds stopping condition
        if max(agent.size for agent in self.agents) >= 100:
            self.stop(exit=True)

if __name__ == '__main__':
    myworld = World09(topology=TorusGrid(shape=params['world_shape']))
    myobserver = GUI06(myworld)
    myobserver.mainloop() 

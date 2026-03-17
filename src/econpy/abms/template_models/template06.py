""" Template Model 6: Animated Histogram """

from template05 import *

class GUI06(GUI05):
    def gui(self):
        GUI05.gui(self)
        def get_agent_sizes():
            agents = self.subject.get_agents(self.subject.AgentType)
            return list(agent.size for agent in agents)
        self.add_histogram('Agent Sizes', get_agent_sizes, bins=range(11))

if __name__ == '__main__':
    myworld = World05(topology=TorusGrid(shape=params['world_shape']))
    myobserver = GUI06(myworld)
    myobserver.mainloop()

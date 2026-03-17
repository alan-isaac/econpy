""" Template Model 14: Randomized Model Initialization """

from template13 import *
params.update(agent_size_mean=0.1, agent_size_sd=0.03)

class World14(World12):
    agent_size_mean = params['agent_size_mean']
    agent_size_sd = params['agent_size_sd']
    def setup_agents(self):                #random size for initial agents
        myagents = self.create_agents(self.AgentType, number=self.n_agents)
        mean = self.agent_size_mean
        sd = self.agent_size_sd
        for agent in myagents:
            size_drawn = random.normalvariate(mean, sd)
            agent.size = max(0.0, size_drawn)

class GUI14(GUI13):
    def gui(self):
        GUI13.gui(self)
        self.add_slider('Init. Size Mean', 'agent_size_mean', 0.0, 1.0, 0.1)
        self.add_slider('Init. Size SD', 'agent_size_sd', 0.0, 0.1, 0.01)

if __name__ == '__main__':
    myworld = World14(topology=TorusGrid(shape=params['world_shape']))
    myobserver = GUI14(myworld)
    myobserver.mainloop()

# -*- coding: utf8 -*-
import math

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import NetworkModule
from mesa.visualization.modules import TextElement
from .model import VirusModel, State, number_infected


def network_portrayal(G):
    # The model ensures there is always 1 agent per node

    def node_color(agent):
        # return {
        #     State.INFECTED: '#FF0000',
        #     State.SUSCEPTIBLE: '#008000'
        # }.get(agent.state, '#808080')
        return '#800000'

    def edge_color(agent1, agent2):
        # if State.RESISTANT in (agent1.state, agent2.state):
        #     return '#000000'
        return '#e8e8e8'

    def edge_width(agent1, agent2):
        # if State.RESISTANT in (agent1.state, agent2.state):
        #     return 3
        return 2

    def get_agents(source, target):
        return G.node[source]['agent'][0], G.node[target]['agent'][0]

    portrayal = dict()
    portrayal['nodes'] = [{'size': len(agents) * 2,
                           'color': node_color(agents[0]),
                           'tooltip': "id: {}<br>state: {}".format(agents[0].unique_id, agents[0].name),
                           }
                          for (node_id, agents) in G.nodes.data('agent')]

    portrayal['edges'] = [{'source': source,
                           'target': target,
                           'color': edge_color(*get_agents(source, target)),
                           'width': edge_width(*get_agents(source, target)),
                           }
                          for (source, target) in G.edges]

    return portrayal


network = NetworkModule(network_portrayal, 500, 500, library='d3')
chart = ChartModule([{'Label': 'Czytelnia', 'Color': '#FF0000'},
                     {'Label': 'Kawiarnia', 'Color': '#008000'},
                     {'Label': 'Chillout', 'Color': '#808000'},
                     {'Label': 'Biuro', 'Color': '#008080'},
                     {'Label': 'Toaleta', 'Color': '#808080'}])


class MyTextElement(TextElement):
    def render(self, model):
        return "ASD"


model_params = {}

# model_params = {
#     'num_nodes': UserSettableParameter('slider', 'Number of agents', 10, 10, 100, 1,
#                                        description='Choose how many agents to include in the model'),
#     'avg_node_degree': UserSettableParameter('slider', 'Avg Node Degree', 3, 3, 8, 1,
#                                              description='Avg Node Degree'),
#     'initial_outbreak_size': UserSettableParameter('slider', 'Initial Outbreak Size', 1, 1, 10, 1,
#                                                    description='Initial Outbreak Size'),
#     'virus_spread_chance': UserSettableParameter('slider', 'Virus Spread Chance', 0.4, 0.0, 1.0, 0.1,
#                                                  description='Probability that susceptible neighbor will be infected'),
#     'virus_check_frequency': UserSettableParameter('slider', 'Virus Check Frequency', 0.4, 0.0, 1.0, 0.1,
#                                                    description='Frequency the nodes check whether they are infected by '
#                                                                'a virus'),
#     'recovery_chance': UserSettableParameter('slider', 'Recovery Chance', 0.3, 0.0, 1.0, 0.1,
#                                              description='Probability that the virus will be removed'),
#     'gain_resistance_chance': UserSettableParameter('slider', 'Gain Resistance Chance', 0.5, 0.0, 1.0, 0.1,
#                                                     description='Probability that a recovered agent will become '
#                                                                 'resistant to this virus in the future'),
# }

server = ModularServer(VirusModel, [network, MyTextElement(), chart], 'Budynek publiczny w społeczeństwie cyfrowym', model_params)
server.port = 8521

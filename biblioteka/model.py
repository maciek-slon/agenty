import random
import math
from enum import Enum
import networkx as nx

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid

import numpy as np

class State(Enum):
    DOING = 0
    GOING = 1
    BEING = 2

def number_state(model, state):
    #return sum([1 for a in model.grid.get_all_cell_contents() if a.state is state])
    return 1


def number_infected(model):
    #return number_state(model, State.INFECTED)
    return 1


def number_susceptible(model):
    #return number_state(model, State.SUSCEPTIBLE)
    return 1


def number_resistant(model):
    #return number_state(model, State.RESISTANT)
    return 1


class VirusModel(Model):
    """A virus model with some number of agents"""

    def __init__(self):
        # self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
        # self.G = nx.erdos_renyi_graph(n=3, p=0.5)
        self.G = nx.Graph()
        self.G.add_node(0)
        self.G.add_node(1)
        self.G.add_node(2)
        self.G.add_node(3)
        self.G.add_node(4)
        self.G.add_node(4)
        self.G.add_edge(0, 1)
        self.G.add_edge(0, 2) 
        self.G.add_edge(0, 3) 
        self.G.add_edge(0, 4) 
        self.G.add_edge(0, 5) 
        self.G.add_edge(1, 4) 
        self.G.add_edge(4, 5) 
        self.grid = NetworkGrid(self.G)

        self.rooms = {}
        self.rooms[0] = {"name": "Wejście",   "rates": {}}
        self.rooms[1] = {"name": "Czytelnia", "rates": {"Nauka" : 2}}
        self.rooms[2] = {"name": "Chillout",  "rates": {"Relaks": 10}}
        self.rooms[3] = {"name": "Biuro",     "rates": {"Praca": 1.5}}
        self.rooms[4] = {"name": "Toaleta",   "rates": {"Toaleta": 30}}
        self.rooms[5] = {"name": "Kawiarnia", "rates": {"Jedzenie": 12, "Kultura": 0.5}}

        collector_dict = {}
        for i, room in enumerate(self.rooms):
            collector_dict[self.rooms[i]["name"]] = lambda model, i=i: len(model.grid.get_cell_list_contents([i]))-1
        self.datacollector = DataCollector(collector_dict)

        self.schedule = RandomActivation(self)


        # Create agents 
        for i, node in enumerate(self.G.nodes()):
            r = RoomAgent(i, self, self.rooms[i]["name"], self.rooms[i]["rates"])
            self.schedule.add(r)

            # Add the agent to the node
            self.grid.place_agent(r, node)

        
        self.prob_needs = {"Jedzenie": [4, 0.6], "Toaleta": [2, 0.6], "Relaks": [5, 1]}
        self.prob_studs = {"Nauka": [2, 1.5], "Praca": [0, 0.5], "Kultura": [0, 1.0]}
        self.prob_works = {"Nauka": [0, 0.3], "Praca": [6, 1.0], "Kultura": [0, 0.2]}
        self.prob_tours = {"Nauka": [0, 0.3], "Praca": [0, 0.5], "Kultura": [1, 1.0]}
        self.prob_local = {"Nauka": [1, 0.7], "Praca": [2, 0.9], "Kultura": [1, 1.0]}

        # godziny        0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
        self.rate_studs=[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        self.rate_works=[0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0]
        self.rate_tours=[0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 3, 3, 3, 3, 4, 4, 4, 6, 6, 4, 3, 2, 0, 0]
        self.rate_local=[0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 4, 4, 2, 2, 4, 5, 6, 6, 6, 3, 0, 0, 0]

        self.running = True
        self.datacollector.collect(self)

        self.tm = 6*60
        self.count = 0

    def get_sample(self, probs):
        ret = {}
        for k, [m, s] in probs.items():
            tm = int(np.clip(np.random.normal(m, s)*60, 15, 600))
            ret[k] = tm
        return ret


    def step(self):
        # prepare list for the satisfied agents
        self.satisfied = []

        # add new agents 
        hour = int(self.tm / 60)
        if (hour > 23):
            hour = 0

        for i in range(self.rate_studs[hour]):
            a = HumanAgent(100+self.count, self, self.get_sample(self.prob_needs), self.get_sample(self.prob_studs))
            self.schedule.add(a)
            self.grid.place_agent(a, 0)
            self.count += 1

        for i in range(self.rate_works[hour]):
            a = HumanAgent(100+self.count, self, self.get_sample(self.prob_needs), self.get_sample(self.prob_works))
            self.schedule.add(a)
            self.grid.place_agent(a, 0)
            self.count += 1

        # update system
        self.schedule.step()

        # collect data
        self.datacollector.collect(self)
        
        # make time step
        self.tm = self.tm + 1
        if (self.tm > 24*60):
            self.tm = 0

        # remove satisfied agents from the system
        for a in self.satisfied:
            print(a.unique_id, a.goals, "is satisfied")
            self.grid.move_agent(a, 0)
            self.grid._remove_agent(a, 0)
            self.schedule.remove(a)

    def run_model(self, n):
        for i in range(n):
            self.step()

    def find_best_room(self, goal):
        #print("Looking for room for", goal)
        for i, room in enumerate(self.rooms):
            #print("Room", room, self.rooms[room]["rates"])
            if goal in self.rooms[room]["rates"]:
                return room
        return -1



class RoomAgent(Agent):    
    def __init__(self, unique_id, model, name, rates):
        super().__init__(unique_id, model)
        self.name = name
        self.rates = rates

    def step(self):
        pass

class HumanAgent(Agent):
    def __init__(self, unique_id, model, stamina, goals):
        super().__init__(unique_id, model)
        self.stamina = stamina
        self.needs = stamina.copy()
        self.goals = goals
        self.state = State.DOING
        self.current_aim = ""
        self.need_list = []

    def satisfy_goals(self, room):
        need_move = True
        for rate in room.rates:
            if rate in self.goals and self.goals[rate] > 0:
                self.goals[rate] = self.goals[rate] - room.rates[rate]
                need_move = False
                break

        if need_move:
            new_goal = random.choice(list(self.goals.keys()))
            new_room = self.model.find_best_room(new_goal)
            if new_room >= 0:
                self.model.grid.move_agent(self, new_room)
            else:
                print("Agent cant't find room to satisfy goal: ", new_goal)
    
    def satisfy_needs(self, room):
        need_move = True
        need = self.need_list[0]
        if need in room.rates:
            self.needs[need] = self.needs[need] + room.rates[need]
            if self.needs[need] > self.stamina[need]:
                self.need_list.pop(0)
        else:
            new_room = self.model.find_best_room(self.need_list[0])
            if new_room >= 0:
                self.model.grid.move_agent(self, new_room)
            else:
                print("Agent cant't find room to satisfy need: ", self.need_list[0])

    def update_needs(self, room):
        for need, value in self.needs.items():
            self.needs[need] = value - 1
            if (value <= 0):
                if not need in self.need_list:
                    self.need_list.append(need)

    def step(self):
        current_room = [agent for agent in self.model.grid.get_cell_list_contents([self.pos]) if type(agent) is RoomAgent][0]

        self.update_needs(current_room)

        if len(self.need_list) > 0:
            self.satisfy_needs(current_room)
        else:
            self.satisfy_goals(current_room)

        satisfied = True
        for goal, value in self.goals.items():
            if value > 0:
                satisfied = False
                break

        if satisfied:
            self.model.satisfied.append(self)
        
        #print(current_room.name)
        #print(self.goals)
        #print(self.needs)
            





class VirusAgent(Agent):
    def __init__(self, unique_id, model, initial_state, virus_spread_chance, virus_check_frequency,
                 recovery_chance, gain_resistance_chance):
        super().__init__(unique_id, model)

        self.state = initial_state

        self.virus_spread_chance = virus_spread_chance
        self.virus_check_frequency = virus_check_frequency
        self.recovery_chance = recovery_chance
        self.gain_resistance_chance = gain_resistance_chance

    def try_to_infect_neighbors(self):
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        susceptible_neighbors = [agent for agent in self.model.grid.get_cell_list_contents(neighbors_nodes) if
                                 agent.state is State.SUSCEPTIBLE]
        for a in susceptible_neighbors:
            if random.random() < self.virus_spread_chance:
                a.state = State.INFECTED

    def try_gain_resistance(self):
        if random.random() < self.gain_resistance_chance:
            self.state = State.RESISTANT

    def try_remove_infection(self):
        # Try to remove
        if random.random() < self.recovery_chance:
            # Success
            self.state = State.SUSCEPTIBLE
            self.try_gain_resistance()
        else:
            # Failed
            self.state = State.INFECTED

    def try_check_situation(self):
        if random.random() < self.virus_check_frequency:
            # Checking...
            if self.state is State.INFECTED:
                self.try_remove_infection()

    def step(self):
        if self.state is State.INFECTED:
            self.try_to_infect_neighbors()
        self.try_check_situation()

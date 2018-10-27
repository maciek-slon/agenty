#! /usr/bin/env python

import matplotlib.pyplot as plt
import networkx as nx

#G = nx.petersen_graph()
G = nx.Graph()
G.add_node(2)
G.add_node(1)
G.add_node(3)
G.add_edge(1, 2)
G.add_edge(1, 3) 

nx.draw(G, with_labels=True, font_weight='bold')
plt.show()
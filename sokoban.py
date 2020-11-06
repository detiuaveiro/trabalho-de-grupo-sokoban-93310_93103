#
# Module: cidades
# 
# Implements a SearchDomain for find paths between cities
# using the tree_search module
#
# (c) Luis Seabra Lopes
# Introducao a Inteligencia Artificial, 2012-2020
# Inteligência Artificial, 2014-2020
#

import math
from tree_search import *

class Sokoban(SearchDomain):
    def __init__(self):
        pass
    
    def actions(self,node):
        actlist = []
        for (C1,C2,D) in self.connections:
            if (C1==city):
                actlist += [(C1,C2)]
            elif (C2==city):
               actlist += [(C2,C1)]
        return actlist 
    def result(self,city,action):
        (C1,C2) = action
        if C1==city:
            return C2
    def cost(self, city, action):
        if action[0]!=city:
            action = (action[1],action[0])
        assert city==action[0]
        for c1,c2,c in self.connections:
            if (c1,c2)==action or (c2,c1)==action: 
                return c

    def heuristic(self, city, goal_city):
        return math.sqrt((self.coordinates[city][0]-self.coordinates[goal_city][0])**2 +(self.coordinates[city][1]-self.coordinates[goal_city][1])**2)
    
    def satisfies(self, city, goal_city):
        return goal_city==city




p = SearchProblem(sokoban,'Braga','Faro')
t = SearchTree(p,'depth')

print(t.search())


# Atalho para obter caminho de c1 para c2 usando strategy:
def search_path(c1,c2,strategy):
    my_prob = SearchProblem(cidades_portugal,c1,c2)
    my_tree = SearchTree(my_prob)
    my_tree.strategy = strategy
    return my_tree.search()




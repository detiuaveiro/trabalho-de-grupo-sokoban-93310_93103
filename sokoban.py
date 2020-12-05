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
from mapa import Map
from algorithms import *
from consts import Tiles
class Sokoban(SearchDomain):
	def __init__(self):
		pass
	
	#pushes possiveis das caixas
	def actions(self,node): #(x, y, dx, dy, d) action = (1, 3, 1, 2, 'w')
		#node tem mapa e tens de ver os pushes das caixas
		mapa=node.state
		actions=[]
		for box in mapa.boxes:
			x,y=box
			for dx,dy,l in [(-1,0,"a"),(1,0,"d"),(0,1,"s"),(0,-1,"w")]:
				px=x+dx
				py=y+dy
				if not (mapa.get_tile((px,py)) & 0b1100) and breadth_first_search(mapa.keeper,(x-dx,y-dy),mapa) is not None:
					actions.append((x,y,px,py,l))
		return actions    

	def result(self,mapa,action):
		x, y, dx, dy, _ = action
		cpos_box = x, y 
		npos_box = dx, dy 
		mapa.clear_tile(mapa.keeper)
		mapa.clear_tile(cpos_box)
		mapa.set_tile(cpos_box, Tiles.MAN)
		mapa.set_tile(npos_box, Tiles.BOX)
		return mapa

	
	# numero de passos entre nodes
	def cost(self, mapa, action):
		return 0
	# distancias  
	def heuristic(self, mapa):
		total=0
		finished_boxes=set()
		for storage in mapa.empty_goals:
			mini=1000
			end_box=None
			for box in mapa.boxes:
				dist=manhattan_distance(box,storage)
				if dist < mini and box not in finished_boxes:
					mini=dist
					end_box=box	
			finished_boxes.add(end_box)
			total+=mini
		return total

	def satisfies(self, mapa):
		return mapa.completed

if __name__ == "__main__":
	sokoban = Sokoban()
	mapa = Map("./levels/1.xsb")
	node = SearchNode(mapa,None,None,None,None)
	print(sokoban.actions(node))
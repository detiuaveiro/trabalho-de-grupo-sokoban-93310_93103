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
	def actions(self,node,deadlocks): #(x, y, dx, dy, d) action = (1, 3, 1, 2, 'w')
		#node tem mapa e tens de ver os pushes das caixas
		mapa=node.state
		actions=[]
		for box in node.boxes:
			x,y=box
			for dx,dy,l in [(-1,0,"a"),(1,0,"d"),(0,1,"s"),(0,-1,"w")]:
				px=x+dx
				py=y+dy
				if (px,py) not in deadlocks:
					if not (mapa.get_tile((px,py)) & 0b1100) and breadth_first_search(mapa.keeper,(x-dx,y-dy),mapa) is not None:
						actions.append((x,y,px,py,l))
		return actions

	def result(self,mapa,action, backtrack, deadlocks):
		x, y, dx, dy, _ = action
		cpos_box = x, y 
		npos_box = dx, dy 
		mapa.clear_tile(mapa.keeper)
		mapa.clear_tile(cpos_box)
		mapa.set_tile(cpos_box, Tiles.MAN)
		mapa.set_tile(npos_box, Tiles.BOX)
		if(hash(frozenset(mapa.boxes)),mapa.keeper) not in backtrack:
			print(mapa)
			if self.freeze(mapa,deadlocks,[],(action[2],action[3])):
				print("Not frozen")
				return mapa
		return None


	def freeze(self,newstate,deadlocks,boxeschecked,box):
		x,y=box
		owntile=newstate.get_tile((x,y))
		toptile=newstate.get_tile((x,y-1))
		bottomtile=newstate.get_tile((x,y+1))
		lefttile=newstate.get_tile((x-1,y))
		righttile=newstate.get_tile((x+1,y))
		vert = True
		hor  = True

		boxeschecked.append((x,y))
		#check if box  moved is on goal
		if owntile==Tiles.BOX_ON_GOAL:
    		#check if box moved to goal can be moved
			if (toptile in [Tiles.BOX,Tiles.BOX_ON_GOAL,Tiles.WALL] or bottomtile in [Tiles.BOX,Tiles.BOX_ON_GOAL,Tiles.WALL]) and (lefttile in [Tiles.BOX,Tiles.BOX_ON_GOAL,Tiles.WALL] or righttile in [Tiles.BOX,Tiles.BOX_ON_GOAL,Tiles.WALL]):
				print("ongoal")
				on_goal=True
				if toptile==Tiles.BOX and toptile not in boxeschecked:
					on_goal=self.freeze(newstate,deadlocks,list(boxeschecked),(x,y-1))
				if on_goal and bottomtile==Tiles.BOX and bottomtile not in boxeschecked:
					on_goal=self.freeze(newstate,deadlocks,list(boxeschecked),(x,y+1))
				if on_goal and lefttile==Tiles.BOX and lefttile not in boxeschecked:
					on_goal=self.freeze(newstate,deadlocks,list(boxeschecked),(x-1,y))
				if on_goal and righttile==Tiles.BOX and righttile not in boxeschecked:
					on_goal=self.freeze(newstate,deadlocks,list(boxeschecked),(x+1,y))
				print(on_goal)
				return on_goal

		# Check vertical walls
		if (toptile == Tiles.WALL or bottomtile==Tiles.WALL):
			vert = False

		# Check vertical deadlocks
		elif toptile in deadlocks and bottomtile in deadlocks:
			vert = False

		# Check horizontal walls
		if  (lefttile == Tiles.WALL or righttile==Tiles.WALL):
			hor = False

		# Check horizontal deadlocks
		elif  righttile in deadlocks and lefttile in deadlocks:
			hor = False
		
		if not hor and not vert:
			return False
		
		if toptile in [Tiles.BOX,Tiles.BOX_ON_GOAL] and vert:
			if (x,y-1) not in boxeschecked:
				vert = self.freeze(newstate,deadlocks,list(boxeschecked),(x,y-1))
			else:
				vert = False

		if bottomtile in [Tiles.BOX,Tiles.BOX_ON_GOAL] and vert:
			if (x,y+1) not in boxeschecked:
				vert = self.freeze(newstate,deadlocks,list(boxeschecked),(x,y+1))
			else:
				vert=False

		if (lefttile in [Tiles.BOX ,Tiles.BOX_ON_GOAL]) and hor:
			if(x-1,y) not in boxeschecked:
				hor = self.freeze(newstate,deadlocks,list(boxeschecked),(x-1,y))
			else:
				hor = False

		if (righttile in [Tiles.BOX,Tiles.BOX_ON_GOAL]) and hor:
			if(x+1,y) not in boxeschecked:
				hor = self.freeze(newstate,deadlocks,list(boxeschecked),(x+1,y))
			else:
				hor = False

		if hor or vert:
			print(x,y,"pode mexer",hor,":",vert)
			return True

		return False

	
	# numero de passos entre nodes
	def cost(self, mapa, action):
		return 1
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
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
	def actions(self,node,deadlocks,freez): #(x, y, dx, dy, d) action = (1, 3, 1, 2, 'w')
		mapa=node.state
		actions=[]
		for box in node.boxes:
			x,y=box
			for dx,dy,l in [(-1,0,"a"),(1,0,"d"),(0,1,"s"),(0,-1,"w")]:
				px=x+dx
				py=y+dy
				if not (mapa.get_tile((px,py)) & 0b1100) and breadth_first_search(node.keeper,(x-dx,y-dy),mapa) is not None:
					if (px,py) not in deadlocks and not self.checkfreezes((px,py),freez,mapa,(x,y)): 
						#print("append ",px,py)
						actions.append((x,y,px,py,l))
		return actions

	
	def checkfreezes(self,box_moved,freezes,mapa,prev_pos):
		
		#print(freezes)
		for freeze in freezes:
			if prev_pos not in freeze:
				#print("freeze")
				if len(freeze)!=0 and freeze[0]==box_moved:
					flag=False
					#print(mapa.get_tile(freeze[0]))
					#print(box_moved,"and",freeze)
					for tile in freeze:
						tipo=mapa.get_tile(tile)
						if not flag:
							#print("\na\n\n",mapa,box_moved)
							flag=True
						else:
							if tipo not in [Tiles.BOX,Tiles.BOX_ON_GOAL]:
								flag=False
								#print(tile,"")
								break
					if flag:
						#print("freeze repetido: ",freeze)
						#print("\nb\n\n",mapa)
						return True
			
		return False
	
	def result(self,mapa,action, backtrack, deadlocks,node,freezes):
		x, y, dx, dy, _ = action
		cpos_box = x, y 
		npos_box = dx, dy 
		mapa.clear_tile(node.keeper)
		mapa.clear_tile(cpos_box)
		mapa.set_tile(cpos_box, Tiles.MAN)
		mapa.set_tile(npos_box, Tiles.BOX)


		if(hash(frozenset(mapa.boxes)),mapa.keeper) not in backtrack:
			flag, newfreezes = self.freeze(mapa,deadlocks,[],(dx,dy))
			if flag:
				return mapa
			flag=True
			for box in newfreezes:
				if mapa.get_tile(box) != Tiles.BOX_ON_GOAL:
					#print("not on goal ",newfreezes)
					flag=False
			if flag:
				return mapa
			if len(newfreezes)>1:
				freezes.add(newfreezes)
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

		# Check vertical walls
		if (toptile == Tiles.WALL or bottomtile==Tiles.WALL):
			vert = False

		# Check vertical deadlocks
		elif (x,y+1) in deadlocks and (x,y-1) in deadlocks:
			vert = False

		# Check horizontal walls
		if  (lefttile == Tiles.WALL or righttile==Tiles.WALL):
			hor = False

		# Check horizontal deadlocks
		elif (x+1,y) in deadlocks and (x-1,y) in deadlocks:
			hor = False

		if not hor and not vert:
			#print(newstate)
			return (False, tuple(boxeschecked))

		if toptile in [Tiles.BOX,Tiles.BOX_ON_GOAL] and vert:
			if (x,y-1) not in boxeschecked:
				vert, boxeschecked = self.freeze(newstate,deadlocks,list(boxeschecked),(x,y-1))
			else:
				vert = False

		if bottomtile in [Tiles.BOX,Tiles.BOX_ON_GOAL] and vert:
			if (x,y+1) not in boxeschecked:
				vert, boxeschecked = self.freeze(newstate,deadlocks,list(boxeschecked),(x,y+1))
			else:
				vert=False

		if (lefttile in [Tiles.BOX ,Tiles.BOX_ON_GOAL]) and hor:
			if(x-1,y) not in boxeschecked:
				hor, boxeschecked = self.freeze(newstate,deadlocks,list(boxeschecked),(x-1,y))
			else:
				hor = False

		if (righttile in [Tiles.BOX,Tiles.BOX_ON_GOAL]) and hor:
			if(x+1,y) not in boxeschecked:
				hor, boxeschecked = self.freeze(newstate,deadlocks,list(boxeschecked),(x+1,y))
			else:
				hor = False

		#print(newstate)
		if hor or vert:
			return (True, tuple(boxeschecked))
		return (False, tuple(boxeschecked))
	
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
	#print(sokoban.actions(node))
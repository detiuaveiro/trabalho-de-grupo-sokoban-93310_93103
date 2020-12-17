#Authors:
# Pedro Tavares 93103
# Gonçalo Pereira 93310
#
# partilhamos ideias com:
# Bruno Bastos 93302
# Leandro Silva 93446
#
# Fontes consultadas:
# http://sokobano.de/wiki/index.php?title=Solver
# http://sokobano.de/wiki/index.php?title=How_to_detect_deadlocks
import math
from tree_search import *
from mapa import Map
from algorithms import *
from consts import Tiles
class Sokoban(SearchDomain):
	def __init__(self):
		pass

	# retorna todos os pushes possiveis das caixas
	def actions(self,node,deadlocks,freez): #(x, y, dx, dy, d) action = (1, 3, 1, 2, 'w')
		mapa=node.state
		actions=[]
		for box in node.boxes:
			x,y=box
			# percorre todos os movimentos possíveis
			for dx,dy,l in [(-1,0,"a"),(1,0,"d"),(0,1,"s"),(0,-1,"w")]:
				px=x+dx
				py=y+dy
				# verifica se a caixa é movida para uma posição não bloqueada
				# verifica se o keeper consegue alcançar a tile necessária para empurrar a caixa para a posição pretendida
				if not (mapa.get_tile((px,py)) & 0b1100) and breadth_first_search(node.keeper,(x-dx,y-dy),mapa) is not None:
					# verifica se a caixa não é movida para um simple deadlock
					# verifica se mover a caixa para a posição (px,py) forma um freeze deadlock
					if (px,py) not in deadlocks and not self.checkfreezes((px,py),freez,mapa,(x,y)):
						actions.append((x,y,px,py,l))
		return actions

	# procura se ao mover a caixa encontra um freeze conhecido
	def checkfreezes(self,box_moved,freezes,mapa,prev_pos):
		for freeze in freezes:
			# a posição anterior da caixa ainda é uma box no mapa, logo confirmamos que não se encontra no freeze para evitar falsos positivos
			if prev_pos not in freeze:
				# mover a caixa pode originar um freeze conhecido
				if len(freeze)!=0 and freeze[0]==box_moved:
					flag=False
					for tile in freeze:
						tipo=mapa.get_tile(tile)
						if not flag:
							# primeira caixa está sempre no freeze, é a caixa movida
							flag=True
						else:
							if tipo not in [Tiles.BOX,Tiles.BOX_ON_GOAL]:
								# não é freeze pois uma das tiles do freeze está livre
								flag=False
								break
					if flag:
						# encontrou um freeze conhecido
						return True

		# não encontrou nenhum freeze conhecido
		return False

	# retorna o mapa resultante de uma action 
	def result(self,mapa,action, backtrack, deadlocks,node,freezes):
		x, y, dx, dy, _ = action
		cpos_box = x, y 
		npos_box = dx, dy 
		mapa.clear_tile(node.keeper)
		mapa.clear_tile(cpos_box)
		mapa.set_tile(cpos_box, Tiles.MAN)
		mapa.set_tile(npos_box, Tiles.BOX)


		if(hash(frozenset(mapa.boxes)),mapa.keeper) not in backtrack:
			# procura a existência de freeze deadlocks no mapa
			flag, newfreezes = self.freeze(mapa,deadlocks,[],(dx,dy))
			if flag:
				# não encontrou freezes
				return mapa
			# encontrou um freeze
			flag=True
			for box in newfreezes:
				if mapa.get_tile(box) != Tiles.BOX_ON_GOAL:
					flag=False
			if flag:
				# todas as caixas do freeze encontrado encontram-se em goals, logo não é freeze
				return mapa
			# Guarda a combinação de caixas que formam o freeze deadlock
			if len(newfreezes)>1:
				freezes.add(newfreezes)
		
		return None

	# Procura a existência de freezes no mapa
	def freeze(self,newstate,deadlocks,boxeschecked,box):
		x,y=box
		owntile=newstate.get_tile((x,y))
		toptile=newstate.get_tile((x,y-1))
		bottomtile=newstate.get_tile((x,y+1))
		lefttile=newstate.get_tile((x-1,y))
		righttile=newstate.get_tile((x+1,y))
		# vert: pode mover-se verticalmente
		vert = True
		# hor: pode mover-se horizontalmente
		hor  = True
		# guarda as caixas já visitadas, para não as verificar novamente
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

		# A caixa não se consegue mover -> está bloqueada
		if not hor and not vert:
			return (False, tuple(boxeschecked))

		if toptile in [Tiles.BOX,Tiles.BOX_ON_GOAL] and vert:
			if (x,y-1) not in boxeschecked:
				# A caixa está bloqueada por uma caixa que ainda não foi pesquisada
				vert, boxeschecked = self.freeze(newstate,deadlocks,list(boxeschecked),(x,y-1))
			else:
				# A caixa está bloqueada por uma caixa que sabemos estar bloquada -> está bloqueada
				vert = False

		if bottomtile in [Tiles.BOX,Tiles.BOX_ON_GOAL] and vert:
			if (x,y+1) not in boxeschecked:
				# A caixa está bloqueada por uma caixa que ainda não foi pesquisada
				vert, boxeschecked = self.freeze(newstate,deadlocks,list(boxeschecked),(x,y+1))
			else:
				# A caixa está bloqueada por uma caixa que sabemos estar bloquada -> está bloqueada
				vert=False

		if (lefttile in [Tiles.BOX ,Tiles.BOX_ON_GOAL]) and hor:
			if(x-1,y) not in boxeschecked:
				# A caixa está bloqueada por uma caixa que ainda não foi pesquisada
				hor, boxeschecked = self.freeze(newstate,deadlocks,list(boxeschecked),(x-1,y))
			else:
				# A caixa está bloqueada por uma caixa que sabemos estar bloquada -> está bloqueada
				hor = False

		if (righttile in [Tiles.BOX,Tiles.BOX_ON_GOAL]) and hor:
			if(x+1,y) not in boxeschecked:
				# A caixa está bloqueada por uma caixa que ainda não foi pesquisada
				hor, boxeschecked = self.freeze(newstate,deadlocks,list(boxeschecked),(x+1,y))
			else:
				# A caixa está bloqueada por uma caixa que sabemos estar bloquada -> está bloqueada
				hor = False

		
		if hor or vert:
			# A caixa não está bloquada
			return (True, tuple(boxeschecked))
		# A caixa está bloqueada
		return (False, tuple(boxeschecked))
	
	# numero de passos entre nodes
	def cost(self, mapa, action):
		return 1
	
	# Retorna a soma das distâncias de Manhattan de cada goal à caixa mais próxima do mesmo
	def heuristic(self, mapa):
		total=0
		finished_boxes=set()
		for empty_goal in mapa.empty_goals:
			mini=1000
			end_box=None
			for box in mapa.boxes:
				dist=manhattan_distance(box,empty_goal)
				if dist < mini and box not in finished_boxes:
					mini=dist
					end_box=box
			finished_boxes.add(end_box)
			total+=mini
		return total

	# Retorna um boolean que diz se o mapa foi completo ou não
	def satisfies(self, mapa):
		return mapa.completed

if __name__ == "__main__":
	sokoban = Sokoban()
	mapa = Map("./levels/1.xsb")
	node = SearchNode(mapa,None,None,None,None)
	#print(sokoban.actions(node))
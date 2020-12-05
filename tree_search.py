
# Module: tree_search
# 
# This module provides a set o classes for automated
# problem solving through tree search:
#    SearchDomain  - problem domains
#    SearchProblem - concrete problems to be solved
#    SearchNode    - search tree nodes
#    SearchTree    - search tree with the necessary methods for searhing
#
#  (c) Luis Seabra Lopes
#  Introducao a Inteligencia Artificial, 2012-2019,
#  Inteligência Artificial, 2014-2019
from copy import deepcopy
from abc import ABC, abstractmethod
from algorithms import *
from mapa import Tiles, Map
import asyncio
# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomain(ABC):

	# construtor
	@abstractmethod
	def __init__(self):
		pass

	# lista de accoes possiveis num estado
	@abstractmethod
	def actions(self, state):
		pass

	# resultado de uma accao num estado, ou seja, o estado seguinte
	@abstractmethod
	def result(self, state, action):
		pass

	# custo de uma accao num estado
	@abstractmethod
	def cost(self, state, action):
		pass

	# custo estimado de chegar de um estado a outro
	@abstractmethod
	def heuristic(self, state, goal):
		pass

	# test if the given "goal" is satisfied in "state"
	@abstractmethod
	def satisfies(self, state, goal):
		pass


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
	def __init__(self, domain, initial):
		self.domain = domain # sokoban
		self.initial = initial #mapa inicial
	def goal_test(self, state):
		return self.domain.satisfies(state)


# Nos de uma arvore de pesquisa
class SearchNode:
	def __init__(self,state,parent,depth,cost,heuristic,laction): 
		self.state = state      #mapa deepcopy(mapa)
		self.parent = parent    #node
		self.depth = depth
		self.cost = cost
		self.heuristic = heuristic
		self.laction = laction

		#node(asdiadjas,parent.depth+1,parent.cost+problem.domain.cost(mapa),p.doman.heuris(mapa))
	
	#pode ser melhorado a guardar todas as posicoes anteriores
	def in_parent(self,newstate):
		if self.parent == None:
			return False
		if self.parent.state ==newstate:
			return True
		return self.parent.in_parent(newstate)

	def __str__(self):
		return str(self.state)
	def __repr__(self):
		return str(self)

# Arvores de pesquisa
class SearchTree:

	# construtor
	def __init__(self,problem, strategy='breadth'): 
		self.problem = problem          #search problem
		root = SearchNode(problem.initial, None,0,0,problem.domain.heuristic(problem.initial),None)
		self.open_nodes = [root]
		self.strategy = strategy
		self.terminals = 1
		self.non_terminals = 0
		self.solution=None
		#set do backtrack  (hash(boxes),hash(keeper))

	# obter o caminho (sequencia de estados) da raiz ate um no
	def get_path(self,node):
		if node.parent == None:
			return ""
		x,y,xf,yf,l=node.laction
		px=xf-x
		py=yf-y
		path=breadth_first_search(node.parent.state.keeper,(x-px,y-py),node.parent.state)
		path+=l
		return self.get_path(node.parent)+path



	@property
	def length(self):
		return self.solution.depth
	
	@property
	def cost(self):
		return self.solution.cost

	def checkdeadlocks(self,map_init):
		deadlocks = set()
		n_hor, n_vert = map_init.size
		queue = []
		goals=map_init.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL])
		deadlocks=[(x,y) for x in range(1,n_hor) for y in range(1,n_vert) if map_init.get_tile((x,y))!=Tiles.WALL]
		for (x,y) in goals:
			vis = [[0] * n_vert for _ in range(n_hor)]
			queue.append((x, y, x, y))
			while queue:
				x, y, xp, yp = queue.pop(0)
				if vis[x][y] or map_init.get_tile((xp,yp)) == Tiles.WALL or map_init.get_tile((x,y)) == Tiles.WALL:
					# unreachable
					continue
				vis[x][y] = 1
				if (x,y) in deadlocks:
					deadlocks.remove((x,y))
				if 0 <= y + 2 < n_vert:
					queue.append((x, y + 1, x,y+2))
				if 0 <= x + 2 < n_hor:
					queue.append((x + 1, y, x+2,y))
				if 0 <= y - 2 < n_vert:
					queue.append((x, y - 1, x,y-2))
				if 0 <= x - 2 < n_hor:
					queue.append((x - 1, y, x-2,y))
		return deadlocks


	def freeze(self,newstate,deadlocks,boxeschecked,box):
		x,y=box
		owntile=newstate.get_tile((x,y))
		toptile=newstate.get_tile((x,y-1))
		bottomtile=newstate.get_tile((x,y+1))
		lefttile=newstate.get_tile((x-1,y))
		righttile=newstate.get_tile((x+1,y))
		vert = True
		hor  = True
		
		# Check vertical walls

		if owntile==Tiles.BOX_ON_GOAL and not boxeschecked:
			return True
		boxeschecked.append((x,y))

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
			return True
		
		return False
	

	# procurar a solucao 
	async def search(self,limit=None):
		backtrack=set()
		deadlocks = self.checkdeadlocks(self.problem.initial)
		self.problem.initial._map
		while self.open_nodes != []:
			await asyncio.sleep(0)
			node = self.open_nodes.pop(0)
			if self.problem.goal_test(node.state):
				self.solution = node
				self.terminals = len(self.open_nodes)+1
				return self.get_path(node)
			self.non_terminals += 1
			lnewnodes = []
			#print(self.problem.domain.actions(node))
			for a in self.problem.domain.actions(node):
				newstate = self.problem.domain.result(deepcopy(node.state),a)
				newnode = SearchNode(newstate,node,node.depth+1,node.cost+self.problem.domain.cost(node.state,a),self.problem.domain.heuristic(newstate),a)
				if (hash(frozenset(newnode.state.boxes)),newstate.keeper) not in backtrack and deadlocks!=None and (a[2],a[3]) not in deadlocks:
					if self.freeze(newstate,deadlocks,[],(a[2],a[3])):
						lnewnodes.append(newnode)
						self.add_to_open(lnewnodes)
				backtrack.add((hash(frozenset(newnode.state.boxes)),newstate.keeper))
		return None
		
	@property
	def avg_branching(self):
		return round((self.terminals - 1 + self.non_terminals) / self.non_terminals,2)  

	# juntar novos nos a lista de nos abertos de acordo com a estrategia
	def add_to_open(self,lnewnodes):
		if self.strategy == 'breadth':
			#adiciona ao fim
			self.open_nodes.extend(lnewnodes)
		elif self.strategy == 'depth':
			#mete no inicio
			self.open_nodes[:0] = lnewnodes
		elif self.strategy == 'uniform':
			self.open_nodes.extend(lnewnodes)
			self.open_nodes.sort(key=lambda node:node.cost)
		elif self.strategy == "greedy":
			self.open_nodes.extend(lnewnodes)
			self.open_nodes.sort(key=lambda node:node.heuristic)
		elif self.strategy == "a*":
			self.open_nodes.extend(lnewnodes)
			self.open_nodes.sort(key=lambda node:node.heuristic+node.cost)

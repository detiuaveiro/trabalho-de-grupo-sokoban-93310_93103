
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
from mapa import Tiles
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
		print("NODE: ",node)
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

	def checkdeadlocks(self,newstate,a):
		#xi,yi,xf,yf,key
		if(newstate.get_tile((a[2],a[3]))!=Tiles.BOX_ON_GOAL and ((newstate.get_tile((a[2],a[3]-1))==Tiles.WALL or newstate.get_tile((a[2],a[3]+1))==Tiles.WALL) and (newstate.get_tile((a[2]+1,a[3]))==Tiles.WALL or newstate.get_tile((a[2]-1,a[3]))==Tiles.WALL))):
			print("DEADLOCK!!!\nx:",a[2],"y:",a[3])
			print(newstate)
			return False
		return True
			
	# procurar a solucao
	async def search(self,limit=None):
		backtrack=set()
		while self.open_nodes != []:
			await asyncio.sleep(0)
			node = self.open_nodes.pop(0)
			if self.problem.goal_test(node.state):
				self.solution = node
				self.terminals = len(self.open_nodes)+1
				print("\n\n\n\n\n\n\n\nCHEGOU AQUI\n\n\n\n\n\n\n\n",self.get_path(node))
				return self.get_path(node)
			self.non_terminals += 1
			lnewnodes = []
			print(self.problem.domain.actions(node))
			for a in self.problem.domain.actions(node):
				newstate = self.problem.domain.result(deepcopy(node.state),a)
				newnode = SearchNode(newstate,node,node.depth+1,node.cost+self.problem.domain.cost(node.state,a),self.problem.domain.heuristic(newstate),a)
				if self.checkdeadlocks(newstate,a):
					if (hash(frozenset(newnode.state.boxes)),newstate.keeper) not in backtrack:
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
		

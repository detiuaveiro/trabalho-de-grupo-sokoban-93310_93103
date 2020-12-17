
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

# Authors:
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
	def __init__(self,state,parent,depth,cost,heuristic,laction,boxes,keeper): 
		self.state = state      #mapa deepcopy(mapa)
		self.parent = parent    #node
		self.depth = depth
		self.cost = cost
		self.heuristic = heuristic
		self.laction = laction
		self.boxes=boxes		#caixas para nao ter de fazer for loops desnecessarios
		self.keeper=keeper		#keeper para nao ter de procurar sempre que o keeper for necessario
	
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
		root = SearchNode(problem.initial, None,0,0,problem.domain.heuristic(problem.initial),None,problem.initial.boxes,problem.initial.keeper)#node inicial
		self.open_nodes = [root]	#nodes a verificar
		self.strategy = strategy    #estrategia de pesquisa
		self.terminals = 1			
		self.non_terminals = 0
		self.solution=None
		self.deadlocks=self.checkdeadlocks(problem.initial)		#posicoes de deadlock
		self.freezes=set()										#set de todos os freezes encontrados até ao momento

	# obter o caminho (sequencia de estados) da raiz ate um no
	def get_path(self,node):
		if node.parent == None:
			return ""
		x,y,xf,yf,l=node.laction
		px=xf-x
		py=yf-y
		path=breadth_first_search(node.parent.keeper,(x-px,y-py),node.parent.state)#procura caminho da posicao apos a ação anterior até a açao seguinte
		path+=l #ao caminho ate a açao adiciona a açao em si (mover a caixa)
		return self.get_path(node.parent)+path #chama se a si proprio, mas para o node pai ate chegar a root

	@property
	def length(self):
		return self.solution.depth	#numero de antecedentes ate a root
	
	@property
	def cost(self):
		return self.solution.cost

	#verifica quais as posiçoes que criam simple deadlocks
	def checkdeadlocks(self,map_init):
		deadlocks = set()
		n_hor, n_vert = map_init.size
		queue = []
		goals=map_init.filter_tiles([Tiles.GOAL, Tiles.MAN_ON_GOAL, Tiles.BOX_ON_GOAL]) #todos os tipos de goal
		deadlocks=[(x,y) for x in range(1,n_hor) for y in range(1,n_vert) if map_init.get_tile((x,y))!=Tiles.WALL]#inicializar deadlocks como todas as tiles que nao sejam paredes
		#verificar ate que tiles se poderiam levar caixas caso elas fossem puxadas a partir dos goals
		for (x,y) in goals:
			vis = [[0] * n_vert for _ in range(n_hor)]
			queue.append((x, y, x, y))
			while queue:
				x, y, xp, yp = queue.pop(0)
				if vis[x][y] or map_init.get_tile((xp,yp)) == Tiles.WALL or map_init.get_tile((x,y)) == Tiles.WALL:
					# tile inalcançavel pela caixa
					continue
				vis[x][y] = 1
				if (x,y) in deadlocks:			#verificar se ainda esta na lista de possiveis deadlocks
					deadlocks.remove((x,y))		#remover da lista
				#proximas tiles a verificar
				if 0 <= y + 2 < n_vert:
					queue.append((x, y + 1, x,y+2))
				if 0 <= x + 2 < n_hor:
					queue.append((x + 1, y, x+2,y))
				if 0 <= y - 2 < n_vert:
					queue.append((x, y - 1, x,y-2))
				if 0 <= x - 2 < n_hor:
					queue.append((x - 1, y, x-2,y))
		return deadlocks						#retorna lista de simple deadlocks
	

	# procurar a solucao 
	async def search(self,limit=None):
		# set que contém os nodes já visitados, para evitar visitar várias vezes o mesmo nó
		backtrack=set()
		self.problem.initial._map
		# enquanto existem nodes para pesquisar, o programa procura uma solução para o problema
		while self.open_nodes != []:
			await asyncio.sleep(0)
			node = self.open_nodes.pop(0)
			self.non_terminals += 1
			lnewnodes = []
			# percorre todas as ações geradas pelo node
			for a in self.problem.domain.actions(node,self.deadlocks,self.freezes):
    			# newstate é o mapa resultante da ação
				newstate = self.problem.domain.result(deepcopy(node.state),a,backtrack,self.deadlocks,node,self.freezes)
				# se o mapa é válido, cria um novo node
				if newstate != None:
					print(newstate)
					# newnode: novo node criado
					newnode = SearchNode(newstate,node,node.depth+1,node.cost+self.problem.domain.cost(node.state,a),self.problem.domain.heuristic(newstate),a,newstate.boxes,newstate.keeper)
					# se o novo node corresponde à solução não é preciso criar novo nós
					if self.problem.goal_test(newstate):
						self.solution = node
						print("num of iter:",self.non_terminals)
						print("depth:",node.depth)
						self.terminals = len(self.open_nodes)+1
						print("terminals:",self.terminals)
						# o programa vai agora procurar o caminho correspondente à solução encontrada
						return self.get_path(newnode)
					# se a solução não é a final, guardamos o novo node e continuamos a pesquisar
					lnewnodes.append(newnode)
					# adicionamos o node à backtrack para não criarmos um igual noutra ocasião
					backtrack.add((hash(frozenset(newnode.boxes)),newnode.keeper))
			# adicionamos os nodes originados pelas ações à fila de nodes abertos consuante a estratégia definida em add_to_open
			self.add_to_open(lnewnodes)
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
			self.open_nodes.sort(key=lambda node:node.heuristic+node.depth)

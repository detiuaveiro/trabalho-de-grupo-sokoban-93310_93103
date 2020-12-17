def breadth_first_search(start, end, map):
	n_hor, n_vert = map.size	
	vis = [[0] * n_hor for _ in range(n_vert)]	#criar lista bidimensional com o tamanho do mapa e com todos os elementos a 0
	queue = []	#posicoes a percorrer
	queue.append((start[0], start[1], ""))#posicao inicial da pesquisa
	
	while queue:	#enquanto a queue ao for vazia
		x, y, path = queue.pop(0)	#obter primeiro elemento da queue
		if vis[y][x] or map.get_tile((x,y)) & 0b1100: #verificar se a posicao ja foi verificada e se a posicao é ocupada por uma parede, box ou box on goal
			# already visited or blocked
			continue 
		vis[y][x] = 1	#alterar de forma a mostrar que ja foi visitado

		if (x, y) == end:	#se tiver chegado a posicao final retorna o caminho
			return path
		
		#verificar se esta dentro dos limites do mapa
		#caso esteja adiciona-se a lista das posicoes a verificar
		if 0 <= y + 1 < n_vert:	
			queue.append((x, y + 1, path + "s"))
		if 0 <= x + 1 < n_hor:
			queue.append((x + 1, y, path + "d"))
		if 0 <= y - 1 < n_vert:
			queue.append((x, y - 1, path + "w"))
		if 0 <= x - 1 < n_hor:
			queue.append((x - 1, y, path + "a"))
	return None #se nao obtiver solucao

def manhattan_distance(p1,p2):
	return abs(p1[0]-p2[0])+abs(p1[1]-p2[1]) #distancia entre cada eixo de dois pontos, sem ter em conta obstaculos
import math

def breadth_first_search(start, map, end):
	n_hor, n_vert = map.size
	vis = [[0] * n_hor for _ in range(n_vert)]
	queue = []
	queue.append((start[0], start[1], ""))
	
	while queue:
		x, y, path = queue.pop(0)
		if vis[y][x] or map.get_tile((x,y)) & 0b1100:
			# already visited or blocked
			continue 
		vis[y][x] = 1

		if (x, y) == end:
			return path

		if 0 <= y + 1 < n_vert:
			queue.append((x, y + 1, path + "s"))
		if 0 <= x + 1 < n_hor:
			queue.append((x + 1, y, path + "d"))
		if 0 <= y - 1 < n_vert:
			queue.append((x, y - 1, path + "w"))
		if 0 <= x - 1 < n_hor:
			queue.append((x - 1, y, path + "a"))
	return None


def depth_first_search(start, end, map):
	def recursive(cur, path):
		x, y = cur
		print("x:",x," y:",y)
		if vis[y][x] or map.get_tile(cur) & 0b1100:
			print("none1")
			return None 
		vis[y][x] = 1

		if cur == end:
			return path   

		if 0 <= y - 1 < ver_tiles:
			goal_path = recursive((x, y - 1), path + "w")
			if goal_path is not None:
				return goal_path
		if 0 <= x - 1 < hor_tiles:
			goal_path = recursive((x - 1, y), path + "a")
			if goal_path is not None:
				return goal_path
		if 0 <= y + 1 < ver_tiles:
			goal_path = recursive((x, y + 1), path + "s")
			if goal_path is not None:
				return goal_path
		if 0 <= x + 1 < hor_tiles:
			goal_path = recursive((x + 1, y), path + "d")
			if goal_path is not None:
				return goal_path
		print("none2")	
		return None

	hor_tiles, ver_tiles = map.size
	vis = [[0] * hor_tiles for _ in range(ver_tiles)]

	return recursive(start, "")

def manhattan_distance(p1,p2):
	return abs(p1[0]-p2[0])+abs(p1[1]-p2[1])
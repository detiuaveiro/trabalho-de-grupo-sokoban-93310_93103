

def breadth_first_search(start,end,mapa):

    queue = [start]
    hor,ver = mapa.size
    backtrack = []
    while len(queue)!=0:
        x,y = queue.pop(0)
        backtrack.append((x,y))
        if (x,y)==end:
            return True

        if 0<=x-1<hor and not mapa.get_tile((x-1,y)) == 8:
            if (x-1,y) not in backtrack:
                queue.append((x-1,y))
        if 0<=x+1<hor and not mapa.get_tile((x+1,y)) == 8: 
            if (x+1,y) not in backtrack:            
                queue.append((x+1,y))
        if 0<=y-1<ver and not mapa.get_tile((x,y-1)) == 8: 
            if (x,y-1) not in backtrack:
                queue.append((x,y-1))
        if 0<=y+1<ver and not mapa.get_tile((x,y+1)) == 8: 
            if (x,y+1) not in backtrack:
                queue.append((x,y+1))
    return False

def depth_first_search(start, end, map):
	def recursive(cur, path):
		x, y = cur
		if vis[y][x] or map.get_tile(cur) & 0b1100:
			return None 
		vis[y][x] = 1

		if cur == end:
			print("puta q pareu \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
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
		return None

	hor_tiles, ver_tiles = map.size
	vis = [[0] * hor_tiles for _ in range(ver_tiles)]

	return recursive(start, "")
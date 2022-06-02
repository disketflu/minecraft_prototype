
def createworld(chunk_amount, chunk_size):
	cubes_positions = {}
	for x in range(-(chunk_size * chunk_amount), chunk_size * chunk_amount):
		cubes_positions[x] = {}
		for y in range(-(chunk_size * chunk_amount), chunk_size * chunk_amount):
			cubes_positions[x][y] = {}
			for z in range(-(chunk_size * chunk_amount), chunk_size * chunk_amount):
				cubes_positions[x][y][z] = [True, 0]


				
	return cubes_positions

world = createworld(10, 10)
print(world.__sizeof__())
print(world)

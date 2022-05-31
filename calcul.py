import math
import noise
import numpy as np
import matplotlib.pyplot as plt

shape = (1024,1024)
scale = 100.0
octaves = 6
persistence = 0.5
lacunarity = 2.0

world = np.zeros(shape)
for x in range(shape[0]):
    for y in range(shape[1]):
            world[x][y] = noise.pnoise2(x/scale, 
                                    y/scale,
                                    octaves=octaves, 
                                    persistence=persistence, 
                                    lacunarity=lacunarity, 
                                    repeatx=1024, 
                                    repeaty=1024,  
                                    base=0)

color_world = np.zeros(world.shape+(3,))
for x in range(shape[0]):
    for y in range(shape[1]):
            if world[x][y] < -0.05:
                color_world[x][y] = [50, 50, 200]
            elif world[x][y] < 0:
                color_world[x][y] = [250, 250, 50]
            else:
                color_world[x][y] = [50, 200, 50]

print(np.max(world))
print(np.min(world))

# plt.imshow(world, cmap='gray') # .astype('uint8')
plt.imshow(color_world.astype('uint8'))
plt.show()
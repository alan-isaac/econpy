"""
An ultra-simple version of Conway's game of life.
Implements the Gosper glider gun for illustration.
Uses a finite world, so there is a small anomaly
at the edge.

:see: http://www.argentum.freeserve.co.uk/lex_g.htm#gosperglidergun
"""
from time import sleep
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

#turn on interactive use
plt.ion()
plt.hold(False)

#initialize figure
fig1 = plt.figure(1)
ax1 = fig1.gca()

#initialize array
grid = np.zeros( (100,100), dtype=np.int)

"""
#blinker
grid[2,1:4] = 1
print grid

#glider
grid[2:5,2:5] = [(0,1,0),(0,0,1),(1,1,1)]

#rabbits
grid[40:43,40:47]= np.array([
1,0,0,0,1,1,1,
1,1,1,0,0,1,0,
0,1,0,0,0,0,0,
]).reshape((3,-1))

"""
#Gosper glider gun
grid[2:11,2:38] = np.array([
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,
1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
]).reshape(9,-1)




#Game of Life footprint and rules
fp = [(1,1,1),(1,1,1),(1,1,1)]
def fnc(buffer):
	alive = buffer[4]
	s = sum(buffer)
	test = ((s==3) or (s-alive==3))
	return test


for _ in range(1000):
	plt.matshow(grid, fignum=False)
	grid = ndimage.generic_filter(grid, fnc, footprint=fp, mode='constant')
	sleep(0.05)



""" Template Model 15: Data-Based Model Initialization """

from gridworld import RectangularGrid
from template14 import *
params.update(cell_data_file='Cell.Data')

def read_celldata(filename):
	location2value = dict()
	maxx, maxy = 0, 0
	fh = open(filename, 'r')
	for _ in range(3): #discard 3 lines
		trash = next(fh)
	for line in fh:
		x, y, prodrate = line.split()
		x, y, prodrate = int(x), int(y), float(prodrate)
		location2value[(x,y)] = prodrate
		maxx, maxy = max(x,maxx), max(y,maxy)
	location2value['shape'] = (maxx+1, maxy+1)
	return location2value

class Cell15(Cell03):
	def initialize(self):
		self.change_color()
	def produce(self):
		self.supply += self.max_produce #no longer random
		self.change_color()
	def change_color(self):
		r = b = 0
		g = min(2*self.supply, 1.0)
		self.display(fillcolor=(r, g, b))

class World15(World14):
	PatchType = Cell15
	def setup_patches(self):
		celldata = read_celldata(params['cell_data_file'])
		shape = celldata.pop('shape')
		self.set_topology(RectangularGrid(shape=shape))
		patches = self.create_patches(self.PatchType)
		for (x,y), prodrate in celldata.items():
			patches[x][y].max_produce = prodrate

if __name__ == '__main__':
	myworld = World15(topology=None)
	myobserver = GUI14(myworld)
	myobserver.mainloop() 

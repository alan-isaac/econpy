import pyx

def pyx_scatter_plot_matrix(group,figwidth=18,hsep=1,vsep=1):
	"""
	Return: pyx canvas,
	a scatter plot matrix for the group.
	(group[i] must be the i-th series.)
	Sample use::

		import numpy as np
		data = np.random.random((3,10))
		test1 = pyx_scatter_plot_matrix(data)
		test1.writeEPSfile("c:/temp/temp.eps")
	"""
	g_len = len(group)
	subplot_size = (figwidth - (g_len-1)*hsep)/g_len
	c = pyx.canvas.canvas()
	g_id = range(g_len)
	xlinks = []
	for yi in g_id[::-1]:
		for xi in g_id:
			xseries = group[xi]
			yseries = group[yi]
			if xi == 0:
				ylinkaxis = None
			else:
				ylinkaxis = pyx.graph.axis.linkedaxis(ylink.axes["y"])
			if yi == g_len-1:
				xlinkaxis = None
			else:
				xlinkaxis = pyx.graph.axis.linkedaxis(xlinks[xi].axes["x"])
			newgraph = c.insert(pyx.graph.graphxy(width=subplot_size, height=subplot_size,
				xpos=(subplot_size+hsep)*xi,
				ypos=(subplot_size+vsep)*(g_len-1-yi),
				x = (xlinkaxis or pyx.graph.axis.linear()),
				y = (ylinkaxis or pyx.graph.axis.linear()),
				)
				)
			newgraph.plot(pyx.graph.data.points(zip(xseries,yseries), x=1, y=2))
			if xi == 0:
				ylink = newgraph
			if yi == g_len -1:
				xlinks.append( newgraph )
	return c


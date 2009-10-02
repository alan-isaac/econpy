"""A collection of simple tools for implementing
agent-based simulations on a grid.

:author: Alan G Isaac <alan dot isaac @ gmail dot com>
:note: we draw the following distinction:
	a world has locations, an object has a position
:requires: Numpy_ and Matplotlib_ (for graphics)
:thanks: Kentaro Murayama suggested treating screen
	clicks as patch clicks, which allows patch clicks
	without any rectangle creation.

.. _NumPy: http://numpy.scipy.org/
.. _Matplotlib: http://matplotlib.sourceforge.net/
"""
import Tkinter as tk
from operator import add, methodcaller
import logging, math, operator, random, turtle
from itertools import imap, izip, starmap
from itertools import product as cartesian_product
from collections import defaultdict, deque

try:
	import numpy as np
	import matplotlib as mpl
except ImportError:
	msg = """
	gridworld depends on NumPy and Matplotlib.
	Please install these first.
	http://numpy.scipy.org/
	http://matplotlib.sourceforge.net/
	"""
	raise ImportError(msg)
mpl.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure 


## CONVENIENCE FUNCTIONS
def ask(agents, methodname, *args, **kwargs):
	"""Return None. Calls method `methodname`
	on each agent, where `agents` is any iterable
	of objects supporting this method call.
	Comment: only living agents are asked to do things.

	:see: http://docs.python.org/library/operator.html#operator.methodcaller
	"""
	f = methodcaller(methodname, *args, **kwargs)
	for agent in agents:
			f(agent)

def askrandomly(agents, methodname, *args, **kwargs):
	"""Return list. Calls method `methodname`
	on each agent, where `agents` is any iterable
	of objects supporting this method call.
	A copy of `agents` is shuffled before the method calls.
	"""
	agents = list(agents)
	random.shuffle(agents)
	ask(agents, methodname, *args, **kwargs)
	return agents

def moore_neighborhood(radius, center=(0,0), keepcenter=False, aslist=True):
	"""Return list or generator, the Moore neighborhood of the origin
	(or equivalently. the Moore neighborhood of any point
	as characterized by offsets from its location).
	By default (center=(0,0)), uses (0,0) as 2d origin.
	(Change the center dimension to change the dimension.)
	By default (keepcenter=False), does not include origin.
	"""
	offsets = range(-radius, radius+1)
	dim = len(center)
	hood = cartesian_product(offsets, repeat=dim)
	if center != (0,)*dim:
		hood = ( tuple(imap(add, center, nbr)) for nbr in hood )
	if not keepcenter:
		hood = (loc for loc in hood if loc != center)
	if aslist:
		hood = list(hood)
	return hood

def register_person(screen):
	"""Return None. Register a simple person shape."""
	body = [(3, -2), (1, -12), (4, -21), (3, -23), (0, -23),
	(-2, -15), (-3, -23), (-6, -23), (-8, -21), (-5, -12), (-6, -2)]
	arm1 = [(-6, -2), (-11, -8), (-9, -11), (-3, -3)]
	arm2 = [(3, -2), (7, -8), (6, -11), (0, -3)]
	head = [(4, 0), (3.804, 1.236), (3.236, 2.352), (2.352, 3.236), (1.236, 3.804),
			(0, 4), (-1.236, 3.804), (-2.352, 3.236), (-3.236, 2.352), (-3.804, 1.236),
			(-4., 0), (-3.804, -1.236), (-3.236, -2.352), (-2.352, -3.236), (-1.236, -3.804),
			(0, -4), (1.236, -3.804), (2.352, -3.236), (3.236, -2.352), (3.804, -1.236)]
	person = turtle.Shape('compound')
	for component in (body, arm1, arm2, head):
		person.addcomponent(component, 'red', 'black')
	screen.register_shape('person',person)

def describe(seq):
	"""Return dict, simple stats for `seq`,
	which should be a sequence of numbers.
	Note the `std` is the *population* standard deviation.
	"""
	count = len(seq)
	total = float( sum(seq) )
	stats = dict(count=count, total=total)
	if count > 0:
		mean = total / count
		stats['mean'] = mean
		stats['max'] = max(seq)
		stats['min'] = min(seq)
		deviations = (xi-mean for xi in seq)
		variance = sum(d*d for d in deviations) / count
		stats['variance'] = variance
		stats['std'] = math.sqrt(variance)
	else:
		stats['mean'] = None
		stats['max'] = None
		stats['min'] = None
		stats['variance'] = None
		stats['std'] = None
	return stats


#BEGIN GRID CLASSES
class FiniteGrid(dict):
	"""Maps agents to coordinates, where coordinates
	are NOT constrained to the grid."""
	def __init__(self, shape):
		dict.__init__(self)
		self._shape = shape
	def location(self, location):
		"""Return tuple, the constrained location.
		"""
		raise NotImplementedError
	def set_position(self, agent, coordinates):
		"""Return tuple, the constrained coordinates."""
		gridloc = self.location(coordinates)
		if gridloc is None:
			logging.warn('Moving agent off grid.')
			self[agent] = coordinates
		else:
			self[agent] = gridloc
		return gridloc or coordinates
	def is_empty(self, coordinates):
		"""Return bool,
		True if location not occupied else False."""
		grid_position = self.location(coordinates)
		return grid_position not in self.values()
	def round2int(self, coordinates):
		#no border constraint!
		coordinates = map(round, coordinates)
		#chk not needed in Python 3
		coordinates = map(int, coordinates)
		return tuple(coordinates)
	def place(self, objects, coordinates):
		"""Return None. Place objects on grid.
		Does not check for occupancy."""
		logging.debug('Enter FiniteGrid.populate.')
		for obj, loc in zip(objects, coordinates):
			if not hasattr(obj,'position'):
				logging.warn('Creating position attr for {0}.'.format(obj))
			obj.position = loc
			self[obj] = loc
		logging.debug('Exit FiniteGrid.populate.')
	def get_random_locations(self, number, exclude=False):
		"""Return set of `number` random locations from the grid.
		If `exclude` is True, only empty cells are returned.
		If `exclude` is a tuple of agent types,
		only empty cells not containing these types are returned.
		If `exclude` is False, any cells may be returned.
		"""
		if number != abs(int(number)):
			errmsg = '{0} is not a positive integer.'.format(number)
			raise ValueError(errmsg)
		shape = self._shape
		n_possible = reduce(operator.mul, shape)
		if exclude is True:
			occupied = set(self.values())
			n_possible -= len(occupied)
		elif exclude:
			occupied = set(val for key,val in self.items() if isinstance(key,exclude))
		else:
			occupied = set()
		if (number > n_possible):
			errmsg = '{0} is too many objects for this grid.'.format(number)
			raise ValueError(errmsg)
		locations = set()
		while len(locations) < number:
			loc = tuple( random.randrange(si) for si in shape )
			if loc not in locations and loc not in occupied:
				locations.add(loc)
		assert len(locations) == number
		return locations
	#properties
	# read-only
	@property
	def shape(self):
		return self._shape

class Torus(FiniteGrid):
	"""Maps agents to coordinates, where coordinates
	are constrained to the torus by wrapping."""
	def location(self, location):
		"""Return tuple, the constrained location.
		"""
		shape = self.shape
		assert len(location)==len(shape)
		location = self.round2int(location)
		result = tuple( xi%si for (xi,si) in izip(location,shape) )
		return result
	def locations(self, locations):
		"""Return generator, the constrained locations.
		"""
		func = self.location
		return ( func(loc) for loc in locations )

class RectangularGrid(FiniteGrid):
	"""Maps agents to coordinates, where coordinates
	are constrained to the torus by wrapping."""
	def location(self, location):
		"""Return tuple or None,
		the corresponding location on the grid,
		or None if there is none.
		"""
		shape = self.shape
		assert len(location)==len(shape)
		location = self.round2int(location)
		result = tuple( xi%si for (xi,si) in izip(location,shape) )
		if result != location:
			result = None
		return result
	def locations(self, locations, discard=False):
		"""Return generator, the constrained locations.
		Some may be None.
		"""
		return ( self.location(loc) for loc in locations )


#END GRID CLASSES



#BEGIN WORLD CLASSES

class WorldBase(object):
	"""Provides an abstract base class for worlds.
	"""
	_agents = set()
	_agentcounts = 0
	_iteration = 0
	_update_frequency = 1
	maxiter = None
	def initialize(self):
		raise NotImplementedError
	def constrain_loc(self, loc):
		pass
	def constrain_locs(self, loc):
		pass
	def reset(self):
		self.stop()
		self._agents = set()
		self._agentcounts = 0
		self._iteration = 0
	def create_agents(self, AgentType, number=0, locations=None):
		"""Return list, the newly created agents.
		Locations are assigned by `place_randomly` if not specified.
		"""
		if number==0:
			try:
				number = len(locations)
			except TypeError: #must be generator
				locations = tuple(locations)
				number = len(locations)
		else:
			number = int(number)
		#need to know world to complete initialization!
		new_agents = tuple( AgentType(world=self) for _ in range(number) )
		for agent in new_agents:
			self.register(agent)
		assert self._agentcounts == len(self._agents)
		if locations is None:
			self.place_randomly(new_agents)
		else:
			self.place(new_agents, locations)
		return new_agents
	def register(self, agent):
		"""Return None.  Register agent with world. """
		self._agents.add(agent)
		self._agentcounts += 1
	def unregister(self, agent):
		"""Return None.  Unregister agent with world. """
		self._agents.remove(agent)
		self._agentcounts -= 1
		agent.world = None
	def place_randomly(self, agents):
		raise NotImplementedError
	def place(self, agents, locations):
		logging.debug('Enter WorldBase.place.')
		#recall that agent.setposition calls self.setposition
		for agent, loc  in zip(agents, locations):
			agent.set_position(loc)
		logging.debug('Exit WorldBase.place.')
	def set_position(self, agent, location):
		raise NotImplementedError
	def run(self, maxiter=None):
		maxiter = maxiter or self.maxiter
		self._stop = False
		while self.keep_running() \
				and (self._iteration < (maxiter or self._iteration+1)):
			self._iteration += 1
			self.schedule()
			if not (self._iteration % self._update_frequency):
				self._update()
		self.clean_up()
	def keep_running(self):
		return not self._stop
	def stop(self):
		"""Return None. Sets `_stop` to True,
		terminating the loop in `run`.
		"""
		self._stop = True
	def schedule(self):
		raise NotImplementedError
	def _update(self):
		return NotImplemented
	def clean_up(self):
		"""Return None.
		Final WorldBase actions after stop running."""
		return NotImplemented
	def get_agents(self, AgentType=None):
		"""Return set or list,
		the set of all agents (if `AgentType` is None)
		or a list of all instances of `AgentType`.
		"""
		if AgentType is None:
			return list(self._agents)
		else:
			return list(a for a in self.agents if isinstance(a,AgentType))
	#PROPERTIES
	# read-only
	@property
	def agents(self):
		"""Return list, the world's agents.  (Agents subsequently added
		to the world will *not* be included.)
		"""
		return list(self._agents)
	@property
	def iteration(self):
		return self._iteration
	# read-write
	@property
	def update_frequency(self):
		return self._update_frequency
	@update_frequency.setter
	def update_frequency(self, value):
		self._update_frequency = int(value)

class GridWorldBase(WorldBase):
	"""Mixin class for grid-world simulations."""
	#convenience declarations
	_grid = None
	_patches2d = None
	def setup_display(self):
		pass
	def initialize(self):
		"""Return None.
		Commands to be executed at instance creation.
		"""
	def reset(self):
		WorldBase.reset(self)
		self._grid.clear()
		self._patches2d = None
	def schedule(self):
		"""Return None. Schedule actions to be executed each iteration.
		User should override this method."""
		raise NotImplementedError('You must override ``schedule``.')
	def is_empty(self, coordinates):
		"""Return bool,
		True if location not occupied else False."""
		return self._grid.is_empty(coordinates)
	def place_randomly(self, agents, exclude=True):
		logging.debug('Enter GridWorldBase.place_randomly.')
		locations = self.get_random_locations(len(agents), exclude=exclude)
		self.place(agents, locations)
		logging.debug('Exit GridWorldBase.place_randomly.')
	def set_position(self, agent, coordinates):
		oldpos = agent.position
		occupants = self.agents_at(coordinates, agent.__class__)
		if occupants and not agent in occupants:
			info = '{0} is occupied; moving there anyway.'.format(coordinates)
			logging.warn(info)
		grid = self._grid
		#does *not* enforce single occupancy
		gridlocation = grid.set_position(agent, coordinates)
		if self._patches2d:
			oldpatch = self.patch_at(oldpos)
			oldpatch.unregister(agent)
			newpatch = self.patch_at(coordinates)
			newpatch.register(agent)
		return gridlocation
	def get_random_locations(self, number, exclude=False):
		return self._grid.get_random_locations(number, exclude=exclude)
	def constrain_loc(self, location):
		"""Return tuple or None, the constrained location (as a tuple)
		or None (if there is no corresponding constrained location).
		"""
		return self._grid.location(location)
	def constrain_locs(self, locations):
		"""Return set, the constrained valid locations."""
		locations = set( self._grid.locations(locations) )
		locations.discard(None)
		return locations
	def hood_locs(self, shape, radius, center=(0,0), keepcenter=False):
		"""Return set, the central coordinates of the neighborhood patches."""
		if shape.lower() == 'moore':
			locations = moore_neighborhood(radius=radius, center=center,
											keepcenter=keepcenter,
											aslist=False)
			locations = self.constrain_locs(locations)
		else:
			raise ValueError('Unsupported neighborhood type.')
		return locations
	def agents_at(self, location, AgentType=None):
		if self._patches2d:
			all_agents = self.patch_at(location).agents
		else:
			all_agents = set(agent for (agent,loc) in self._grid.items() if loc==location)
		if AgentType:
			all_agents = set(agent for agent in all_agents if isinstance(agent,AgentType))
		return all_agents
	#patch related methods
	def create_patches(self, PatchType):
		"""Return list of lists.  Creates the patches for this world.
		Patch creation should take place **before** agent creation.
		:todo: chk generalize to Nd
		"""
		logging.debug('Enter create_patches.')
		width, height = self.grid.shape
		if self._patches2d is not None:
			logging.warn('This world already seems to have patches.')
		#chk should a patch know its world?
		#:note: rows correspond to first (x) coordinate!
		patches = [[PatchType(world=self, position=(r,k))
						for k in range(height)] for r in range(width)]
		self._patches2d = patches
		logging.debug('Leave create_patches.')
		return patches
	def patches_at(self, locations, preconstrained=True):
		"""Return generator, the patches at the locations.
		"""
		patches = self._patches2d
		if not preconstrained: #get set of constrained locations
			locations = self.constrain_locs(locations)
		return ( self.patch_at(loc, True) for loc in locations )
	def patch_at(self, location, preconstrained=False):
		"""Return Patch, the patch at location.
		If `preconstrained` is True, then `location` is not tested for constraint.
		"""
		patches = self._patches2d
		if not preconstrained:
			location = self.constrain_loc(location)
		#NOTE: assumes _patches2d is a list!
		#thanks to Steven D'Aprano
		# for suggesting operator.getitem to replace list.__getitem__
		if location is not None:
			result = reduce(operator.getitem, location, patches)
			return result
	def kill(self, agent):
		assert agent.is_alive
		patch = agent.patch_here()
		if patch:
			patch.unregister(agent)
		del self._grid[agent]
		self.unregister(agent)
		del agent
	#properties
	# read-only
	@property
	def grid(self):
		return self._grid
	@property
	def patches(self):
		"""Return generator, all the patches in `_patches2d`."""
		patches = self._patches2d
		return (patch for row in patches for patch in row)

class GridWorldCLI(GridWorldBase):
	def	__init__(self, grid):
		self._grid = grid
		self.initialize()

class GridWorldGUI(GridWorldBase, tk.Frame):
	"""Provides a GridWorldBase with a screen."""
	def __init__(self, grid=None, master=None):
		logging.debug('Enter GridWorldGUI.__init__.')
		tk.Frame.__init__(self, master)
		try: self.master.title('GridWorld')
		except AttributeError: pass
		#careful: a Frame has a grid attribute, as does GridWorldBase!
		tk.Frame.grid(self)
		turtle._root = self
		#convenience declarations
		self._turtle_screen = None
		self._button_frame = None
		self._slider_frame = None
		self._monitor_frame = None
		self._graph_frame = None
		self._buttons = dict()  #labels to buttons
		self._setup_button = None
		self._monitors = list()
		self._clickmonitors = defaultdict(list)
		self._graphs = list()
		#GUI request lists
		self.__button_requests = list()
		self.__slider_requests = list()
		self.__clickmonitor_requests = list()
		self.__monitor_requests = list()
		self.__graph_requests = list()
		self.__update_gui = True
		#initializations must come **before** display setup
		# button, slider, and monitor requests should be
		# made in the initialize method
		# (also initial agent creation)
		self.initialize()
		#setup_display will implement the
		# button, slider, and monitor requests
		# (must come **after** `initialize`!!)
		self.setup_display()
		#need to set_grid *after* setup_display (_turtle_screen)
		if grid is not None:
			#this also sets the worldcoordinates
			self.set_grid(grid)
		logging.debug('Leave GridWorldGUI.__init__.')
	def initialize(self):
		"""User can override this with desired initializations.
		This is the right place to add buttons, sliders, etc."""
	def reset(self):
		GridWorldBase.reset(self)
		self._turtle_screen.clear()
		self._setup_button['state'] = 'normal'
	def setup_display(self):
		#setup screen
		self.setup_turtlescreen()
		self._setup_button_frame()
		self._setup_slider_frame()
		self._setup_monitor_frame()
		self._setup_graph_frame()
	def setup_turtlescreen(self):
		my_turtle_frame = tk.Frame(master=self, relief='raised', borderwidth=2)
		turtle._Screen._root = my_turtle_frame
		my_turtle_frame.grid(row=0, column=1, rowspan=3)
		turtle._Screen._canvas = turtle.ScrolledCanvas(my_turtle_frame, 500, 500, 500, 500)
		self._turtle_screen = screen = turtle.Screen()
		screen.onclick(self.clicked_at, add=True)
		screen_canvas = screen._canvas
		screen_canvas.grid(row=0, column=1)
		turtle.RawTurtle.screens = [screen]
	def create_agents(self, AgentType, number=0, locations=None):
		"""Return list, the newly created agents.
		Positions are assigned by `place_randomly` if not specified.
		"""
		screen = self._turtle_screen
		screen.tracer(False)
		agents = GridWorldBase.create_agents(self,
			AgentType=AgentType, number=number, locations=locations)
		return agents
	def set_grid(self, grid):
		self._grid = grid
		x, y = grid.shape
		#set screen coordinates
		screen = self._turtle_screen
		#leave a little space at edges
		screen_coordinates = -1, -1, x, y
		screen.setworldcoordinates(*screen_coordinates)
	def clicked_at(self, *pos):
		"""
		The following may seem a bit roundabout.
		Our patches do not receive clicks (yet), so we report
		clicks received by the screen to the relevant patch.
		This is probably a good idea even if patches can receive
		clicks, since it avoids concerns about accuracy of rectangle
		placement, overlap, etc.
		"""
		#todo: change this if patches become turtles
		#self.patch_at(pos).clicked_at(*pos)
		self.notify(self.patch_at(pos), 'click')
	def add_button(self, label, callback):
		"""Return None. Appends a button request,
		which will be acted upon during setup_display."""
		self.__button_requests.append((label,callback))
	### methods to assist user setup
	def __setup_callback(self, label, callback):
		"""Return function.
		Adds button disabling to the callback.
		(The SetUp button is special because it is disabled after being pressed.)
		"""
		def f():
			self._setup_button['state'] = 'disabled'
			callback()
			self._setup()
		return f
	def setup(self):
		"""Return None.
		User should override this method to do model set up.
		Usually called by the SetUp button."""
	#### set up the frames (buttons, sliders, monitors, and graphs)
	def _setup_button_frame(self):
		#BUTTON FRAME
		btn_frame = tk.Frame(master=self, relief='flat', borderwidth=0)
		self._button_frame = btn_frame
		btn_frame.grid(row=0, column=0)
		requests = self.__button_requests
		for ct, request in enumerate(requests):
			label, callback = request
			button = tk.Button(master=btn_frame,
					text=label,
					command=callback,
					width=15)
			#special handling of SetUp, which should only be called once
			if label.replace(' ','').lower() == 'setup':
				callback = self.__setup_callback(label, callback)
				button['command'] = callback
				self._setup_button = button
			button.grid(row=ct//4, column=ct%4)
			self._buttons[label] = button
	## SLIDERS
	def add_slider(self, label, attr, from_, to, resolution=None):
		if resolution is None:
			resolution = (to-from_)/10.
		self.__slider_requests.append( (label, attr, from_, to, resolution) )
	def _setup_slider_frame(self):
		"""Return None.  Sets up the slider frame."""
		def mkcmd(attr):
			"""Return function, an attribute setter that first
			converts to float (since sliders pass strings)."""
			def cmd(x):
				setattr(self, attr, float(x))
			return cmd
		#SLIDER FRAME
		slider_frame = tk.Frame(master=self, relief='flat', borderwidth=0)
		self._slider_frame = slider_frame
		slider_frame.grid(row=1,column=0)
		sliders = self.__slider_requests
		for ct, slider in enumerate(sliders):
			label, attr, from_, to, res = slider
			init_val = getattr(self, attr)
			cmd = mkcmd(attr)
			newslider = tk.Scale(
				master=slider_frame,
				label=label,
				from_=from_,
				to=to,
				resolution=res,
				command = cmd,
				#variable=var01,
				relief='raised',
				orient=tk.HORIZONTAL,
				length=150
				)
			newslider.set(init_val)
			newslider.grid(row=ct//3, column=ct%3)
	##MONITORS
	def add_monitor(self, label, func, period=1, **kwargs):
		"""Return None.  Adds a monitor request to the queue.
		This must be done during initialization.
		(User should call this function in `initialize`.)
		A monitor reports the value of `func` once each iteration
		by default, but update frequency can be reduced by setting
		`period` to any positive integer.
		"""
		logging.debug('Enter GridWorldGUI.add_monitor')
		self.__monitor_requests.append( (label, func, period, kwargs) ) 
		logging.debug('Enter GridWorldGUI.add_monitor')
		pass
	def add_clickmonitor(self, label, AgentType, *attributues, **kwargs):
		"""Return None.  Adds a click monitor request to the queue.
		This must be done during initialization.
		(User should call this function in `initialize`.)
		A click monitor reports the `attributes` of an `AgentType`
		when it is clicked.
		:comment: You may set multiple click monitors for the same AgentType
			or monitor multiple attributes with a single click monitor
		:comment: value displayed is value at the time of the last click;
			it is not updated
		:comment: kwargs can contain any keyword arguments appropriate to
			a Tkinter label widget.
		"""
		logging.debug('Enter GridWorldGUI.add_clickmonitor')
		self.__clickmonitor_requests.append( (label, AgentType, attributues, kwargs) ) 
		logging.debug('Enter GridWorldGUI.add_clickmonitor')
	def _setup_monitor_frame(self):
		"""Return None. Set up the frame of click monitors and monitors."""
		logging.debug('Enter GridWorldGUI._setup_monitor_frame')
		monitor_frame = tk.Frame(master=self, relief='flat', borderwidth=0)
		self._monitor_frame = monitor_frame
		monitor_frame.grid(row=2,column=0)
		monitors = list()
		#set up click monitors
		requests = self.__clickmonitor_requests
		for label, AgentType, attributes, kwargs in requests:
			tksvar = tk.StringVar(value=label+'\n'*len(attributes) )
			config = dict(relief='raised', bg='white', width=25, justify='left', anchor='nw')
			config.update(kwargs)
			tklabel = tk.Label(master=monitor_frame, textvar=tksvar, **config)
			monitors.append(tklabel)
			#:note: _clickmonitors is a defaultdict(list)
			self._clickmonitors[AgentType].append( (tksvar, label, attributes) )
		#set up the other monitors
		requests = self.__monitor_requests
		for lbl, func, period, kwargs in requests:
			tksvar = tk.StringVar(value=label+'\n')
			config = dict(relief='raised', bg='white', width=25, justify='left', anchor='nw')
			config.update(kwargs)
			tklabel = tk.Label(master=monitor_frame, textvar=tksvar, **config)
			monitors.append(tklabel)
			self._monitors.append( (tksvar, lbl, func, period) )
		for ct, mon in enumerate(monitors):
			mon.grid(row=ct//3, column=ct%3, sticky='nw')
		logging.debug('Exit GridWorldGUI._setup_monitor_frame')
	### GRAPHS
	def add_histogram(self, title, datafunc, **kwargs):
		"""Return None.
		Creates a histogram graph request, which will produce a histogram
		in the GUI.  The `datafunc` should return a sequence of numbers,
		which will be used as data by the histogram.
		Depends on Matplotlib.  See Matplotlib documentation for kwargs.
		If you specify the bins, note that we clip the data so that all
		numbers are in the bins.
		:see: http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.hist
		"""
		logging.debug('Enter GridWorldGUI.add_histogram')
		self.__graph_requests.append(('histogram', title, datafunc, kwargs))
		logging.debug('Exit GridWorldGUI.add_histogram')
	def add_plot(self, title, datafunc, **kwargs):
		"""Return None.
		Creates a time-series plot request, which will produce a histogram
		in the GUI.  The `datafunc` should return one number for plotting each
		time it is called.
		Depends on Matplotlib.  See Matplotlib documentation for kwargs.
		:see: http://matplotlib.sourceforge.net/api/pyplot_api.html#matplotlib.pyplot.hist
		"""
		logging.debug('Enter GridWorldGUI.add_plot')
		self.__graph_requests.append(('plot', title, datafunc, kwargs))
		logging.debug('Exit GridWorldGUI.add_plot')
	# GRAPH FRAME
	def _setup_graph_frame(self):
		"""Return None. Creates a GUI frame that will contain any graphs.
		(See `add_plot` and `add_histogram`.)
		"""
		graph_frame = tk.Frame(master=self, relief='flat', borderwidth=0)
		self._graph_frame = graph_frame
		graph_frame.grid(row=3,column=0, columnspan=2)
		#graph_frame.title('Model Parameters!')
		graphs = self.__graph_requests
		for ct, graph in enumerate(graphs):
			kind, title, datafunc, kwargs = graph
			if kind == 'histogram':
				graph = Histogram(datafunc=datafunc, master=graph_frame, title=title, world=self, **kwargs)
			elif kind == 'plot':
				graph = TSPlot(datafunc, master=graph_frame, title=title, world=self, **kwargs)
			else:
				logging.warn('Unknown graph type: {0}'.format(kind))
			graph.get_tk_widget().grid(row=ct//2, column=ct%2, sticky='nw') 
			#toolbar = NavigationToolbar2TkAgg( cvs, master=graph_frame )
			#toolbar.update()
			#cvs._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
			self._graphs.append(graph)
	###UPDATES
	def _setup(self):
		"""Return None.  Basic GUI setup.
		Called by `__setup_callback`.
		"""
		self._turtle_screen.tracer(True)
		self._turtle_screen.tracer(False)
		self._update_monitors()
		self._setup_graphs()
	def _update(self):
		"""Return None.  Schedules the GUI updating.
		Note that we update the agent display via `turtle` module
		screen's tracer method.  This assumes we do not want a
		continuous update of the agent display.  
		"""
		self._turtle_screen.tracer(True)
		self._turtle_screen.tracer(False)
		self._update_monitors()
		self._update_graphs()
	def _setup_graphs(self):
		for graph in self._graphs:
			graph.setup()
	def _update_graphs(self):
		for graph in self._graphs:
			graph.update()
	def _update_monitors(self):
		fmt = '{0}:\n{1!s:10}'
		for svar, label, func, period in self._monitors:
			if not self._iteration % period:
				svar.set( fmt.format(label, func()) )
	def notify(self, obj, event=None):
		if event=='click':
			fmt = '{0}: {1!s:>10}'
			cm =  self._clickmonitors
			for AgentType in cm:
				if isinstance(obj, AgentType):
					for cmlist in cm[AgentType]:
						svar, label, attributes = cmlist
						report = [label]
						for attr in attributes:
							try:
								val = getattr(obj, attr)
								line = fmt.format(attr, val)
							except AttributeError:
								val = '(does not exist)'
								line = fmt.format(attr, val)
							finally:
								report.append(line)
						svar.set('\n'.join(report))
		else:
			msg = '{0} is not a recongized event.'.format(event)
			logging.info(msg)
	def clean_up(self):
		#chk
		#self.mainloop()
		pass
	def kill(self, agent):
		"""Warning: there may be other references
		to the agent, which will remain!"""
		agent.hideturtle()
		agent.clear()
		screen = self._turtle_screen
		try:
			#thanks to Gregor Lingl for the next threee lines
			screen._delete(agent.currentLineItem)
			screen._delete(agent.drawingLineItem)
			screen._delete(agent.turtle._item)
			screen._delete(agent)
			screen._turtles.remove(agent)
			#chk remove from own lists of agents
		except KeyError:
			pass
		GridWorldBase.kill(self, agent)
		del agent
	def _create_rectangle(self):
		"""Create an invisible polygon item on canvas self.cv)
		"""
		cv = self._turtle_screen.getcanvas()
		return cv.create_rectangle(0, 0, 0, 0, fill="", outline="")
	def _draw_rectangle(self, item, coordlist, **kwargs):
		"""Configure rectangle according to provided arguments:
		fill=None, outline=None, width=None, top=False
		coordlist is sequence of coordinates
		fill is filling color
		outline is outline color
		top is a boolean value, which specifies if polyitem
		will be put on top of the canvas' displaylist so it
		will not be covered by other items.
		"""
		screen = self._turtle_screen
		cl = []
		for x, y in coordlist:
			cl.append(x * screen.xscale)
			cl.append(-y * screen.yscale)
		screen.cv.coords(item, *cl)
		screen.cv.itemconfigure(item, **kwargs)
	def create_rectangle(self, x1, y1, x2, y2, **kwargs):
		rect = self._create_rectangle()
		self._draw_rectangle(rect, [(x1, y1), (x2, y2)], **kwargs)
		return rect
	def exit(self):
		tk.Frame.destroy(self)
		if self.master:
			self.master.destroy()
	#PROPERTIES
	# read-only
	@property
	def screen(self):
		return self._turtle_screen
	# read-write
	@property
	def screen_updating(self, state):
		return self.__update_gui
	@screen_updating.setter
	def screen_updating(self, state):
		state = bool(state)
		screen = self._turtle_screen
		screen.tracer(state)
		self.__update_gui = state


#END WORLD CLASSES

#BEGIN AGENT CLASSES

class Agent(turtle.Turtle):
	def __init__(self, world=None):
		turtle.Turtle.__init__(self)
		self._world = world
		self._position = 0,0
		self._is_alive = True
		self.pen(pendown=False, speed=0)
		self.initialize()
		#note that more callbacks can be added!
		# see turtle.py documentation
		self.onclick(self.clicked_at, add=True)
		logging.debug('Agent initialized at position {0}'.format(self.pos()))
	def initialize(self):
		pass
	def set_position(self, *args):
		"""Return None.
		Move agent to coordinates.  2d only.
		"""
		if len(args) > 1:
			coordinates = args
		elif len(args) == 1:
			coordinates = args[0]
		else:
			msg = '{0} is not valid coordinates'.format(args)
			raise ValueError(msg)
		if self.world:
			coordinates = self.world.set_position(self, coordinates)
		self._position = coordinates
		turtle.Turtle.goto(self, coordinates)
	#aliases (to overrid turtle.Turtle)
	goto = setpos = setposition = set_position
	##patch related methods
	def neighborhood(self, shape, radius, keepcenter=False):
		"""Return generator, the neighborhood patches.
		"""
		locations = self._world.hood_locs(
			shape=shape,
			radius=radius,
			center=self._position,
			keepcenter=keepcenter)
		patches = self._world.patches_at(locations, preconstrained=True)
		return list(patches)
	def patch_here(self):
		return self._world.patch_at( self._position )
	def patch_at(self, location, relative=False):
		"""Return Patch or None, the patch at self.pos()+rloc.
		CAUTION: note the use of relative location is not the default!!
		"""
		pos = self._position
		assert len(location)==len(pos)
		if relative:
			location = tuple(x+dx for (x,dx) in zip(pos, location))
		return self._world.patch_at(location, preconstrained=False)	
	def agents_here(self, AgentType=None):
		return self._world.agents_at(self._position, AgentType=AgentType)	
	def agents_at(self, location, AgentType=None, relative=False):
		"""Return set, the agents on the patch at `location`.
		CAUTION: note the use of relative location is not the default!!
		"""
		pos = self._position
		assert len(location)==len(pos)
		if relative:
			location = tuple(x+dx for (x,dx) in izip(pos, location))
		return self._world.agents_at(location, AgentType=AgentType)	
	def clicked_at(self, *pos):
		"""Return None.  This is the default `onclick` action for an agent.
		"""
		if self._world:
			self._world.notify(self, 'click')
		else:
			self.report_state
	def die(self):
		"""Return None. Remove agent from simulation.
		"""
		if self._is_alive:
			self._world.kill(self)
			self._is_alive = False
		else:
			logging.warn('Trying to kill dead agent.')
	#properties
	# read-only
	@property
	def is_alive(self):
		return self._is_alive
	# read-write
	@property
	def world(self):
		return self._world
	@world.setter
	def world(self, val):
		if (val is None):
			self._world = None
		elif self._world is None:
			self._world = val
		else:
			raise ValueError('Attempting to reset `world`.')
	@property
	def position(self):
		return self._position
	@position.setter
	def position(self, loc):
		self.set_position(loc)
		assert self._position == turtle.Turtle.position(self)

#END AGENT CLASSES

class PatchBase(object):
	def __init__(self, world=None, position=None):
		self._world = world
		self._position = position
		self._agentset = set()
		self.initialize()
	def initialize(self):
		"""Override this method to add intializations."""
	def register(self, agent):
		self._agentset.add(agent)
	def unregister(self, agent):
		self._agentset.discard(agent)
	def report_state(self):
		pass
	def get_agents(self, AgentType=None):
		"""Return set, the agents of type `AgentType`
		or all agents if `AgentType` is None.
		"""
		if AgentType is None:
			result = list(self._agentset)
		else:
			result = list(a for a in self._agentset if isinstance(a, AgentType))
		return result
	#PROPERTIES
	# read-only
	@property
	def agents(self):
		return self._agentset
	@property
	def position(self):
		return self._position

class Patch(PatchBase):
	"""Provides a 2d patch for a Tkinter canvas."""
	def __init__(self, world, position, fill=''):
		self._fillcolor = fill
		self._rectangle = None
		self._canvas = world.screen.cv
		#PatchBase will call initialize
		PatchBase.__init__(self, world=world, position=position)
	def set_fillcolor(self, *color):
		"""Return None.  Set the fillcolor of the patch.
		Recommended: use r,g,b color scheme (0<=r,g,b<=1).
		"""
		if isinstance(color, str):
			color = self.world.screen._colorstr(color)
		else:
			r, g, b = color
			if not all( (0<=ci<=1) for ci in color ):
				raise ValueError('Color values must be in [0,1]')
			r,g,b = imap(round, ((ci*15.) for ci in (r,g,b) ) )
			#next line not needed in Python 3+
			r,g,b = imap(int, (ci for ci in (r,g,b)) )
			color = '#{0:01x}{1:01x}{2:01x}'.format(r,g,b)
			if not self._fillcolor == color: #reset color only if needed
				# (rectangle propery creates a rectangle if nec)
				rect = self.rectangle
				self._canvas.itemconfigure(rect, fill=color)
	def fillcolor(self, *color):
		"""Return color or None.
		If `color` is None, return the current fill color.
		Else set _fillcolor to  `color`.
		(This will create rectangle if needed.)
		"""
		if color is None:
			return self._fillcolor
		else:
			self.set_fillcolor(color)
	def clicked_at(self, *pos):
		"""Return None.
		This is the default `onclick` action for a patch.
		"""
		if self._world:
			self._world.notify(self, 'click')
		else:
			self.report_state
	#PROPERTIES
	# read-only
	@property
	def rectangle(self):
		rect = self._rectangle
		if not rect:
			x, y = self._position
			x1 = x - 0.5
			y1 = y - 0.5
			x2 = x + 0.5
			y2 = y + 0.5
			rect = self._world.create_rectangle(x1, y1, x2, y2)
			self._rectangle = rect
		return rect
	@property
	def world(self):
		return self._world
			


class TSPlot(FigureCanvasTkAgg):
	"""Provides a simple time-series plot of
	the most recent and previous 100 observations,
	where `datafunc` returns a single new observation.
	:note: this implementation relies on ideas discussed
		in the Matplotlib Cookbook
		http://www.scipy.org/Cookbook/Matplotlib/Animations
	"""
	def __init__(self, datafunc, master=None, title='', world=None, **kwargs):
		xlength = 101
		self._title = title
		self._world = world
		self._datafunc = datafunc
		self._background = None
		self._line = None
		self._ylim = (0,1)
		self._xlim = (-100,0)
		self._ydata = deque(maxlen=xlength)
		#Python 3 range object not sliceable
		self._xdata = [x+1-xlength for x in range(xlength)]
		self._fig = mpl.figure.Figure(figsize=(5,2.5), dpi=100)
		self._ax = self._fig.add_subplot(111)
		FigureCanvasTkAgg.__init__(self, self._fig, master=master)
		#grid the widget to master
		#self.get_tk_widget().grid(row=0,column=0, columnspan=2)
		#have we seen positive and negative values in the series?
		self._neg_yvals = False
		self._pos_yvals = False
	def setup(self):
		# create the initial "line" (a single observation)
		new_ydata = self.update_data()
		self.adjust_ylim(new_ydata)
		self.set_background()
	def adjust_ylim(self, datum):
		"""Return bool. Resets `_ylim`
		(if needed to accommodate `_ydata`).
		"""
		ylimlow, ylimhigh = self._ylim
		ymin, ymax = min(self._ydata), max(self._ydata) 
		ydiff = ymax-ymin
		adjust = False
		if not (ylimlow < datum < ylimhigh) \
			or (ylimhigh-ylimlow > 5*ydiff):
			ymax = max(self._ydata)
			ymin = min(self._ydata)
			ylimhigh = ymax + 0.5 * ydiff
			ylimlow = ymin - 0.5 * ydiff
			if ylimhigh == ylimlow:
				ylimhigh += 1
				ylimlow -= 1
			adjust = True
		#restrict limits to all pos or all neg if appropriate
		if not self._neg_yvals:
			if ymin < 0:
				self._neg_yvals = True
			else:
				ylimlow = max(0, ylimlow)
		if not self._pos_yvals:
			if ymax > 0:
				self._pos_yvals = True
			else:
				ylimhigh = min(0, ylimhigh)
		self._ylim = ylimlow, ylimhigh
		return adjust
	def update(self, *args):
		"""Return None. Update the line plot."""
		# update the data
		newdata = self.update_data()
		ydata = self._ydata
		xdata = self._xdata
		if len(ydata) < len(xdata):
			xdata = xdata[-len(ydata):]
		# restore the clean slate background
		self.restore_region(self._background)
		self._line.set_data([xdata,ydata])
		# draw just the animated artists
		self._ax.draw_artist(self._line)
		self._iterctr.set_text('Iteration {0:4d}'.format(self._world.iteration))
		self._ax.draw_artist(self._iterctr)
		# redraw just the axes rectangle
		self.blit(self._ax.bbox)
	def update_data(self):
		"""Return number, the new value from `_datafunc`.
		"""
		new_ydata = self._datafunc()
		self._ydata.append(new_ydata)
		if self.adjust_ylim(new_ydata):
			self.set_background()
		return new_ydata
	def set_background(self):
		"""Return None. Resets the background
		of the canvas.
		"""
		ax = self._ax
		ax.clear()
		ydata = self._ydata
		xdata = self._xdata[-len(ydata):]
		self._line, = ax.plot(xdata, ydata, animated=True)
		self._iterctr = ax.text(0.95, 0.1, 'Iteration: 0',
			horizontalalignment='right',
			verticalalignment='center',
			transform=self._ax.transAxes,
			animated=True)
		ax.set_title(self._title, fontsize='x-small')
		ax.set_xlim(self._xlim)
		ax.set_ylim(self._ylim)
		self.show()
		#save the background (everything but the animated line & ctr)
		# in `_background` (a pixel buffer)
		self._background = self.copy_from_bbox(ax.bbox)

class Histogram(FigureCanvasTkAgg):
	"""Provides a simple unnormed histogram.
	:thanks: John Hunter showed in detail how to do this with a PathPatch
		(Aug 8, 2009, Matplotlib users mailing list)
	"""
	def __init__(self, datafunc, bins, master=None, title='', world=None, **kwargs):
		"""
		Here `datafunc` must return a sequence (e.g., a list or array)
		containing a single iteration's data,
		and `bins` must be a sequence of bin edges.
		(Data outside the edges with be clipped into the lowest and highest bin.)
		:todo: allow specifying number of bins rather than edges
			(requires updating the rectverts)
		"""
		self._datafunc = datafunc
		self._tops = None
		self._edges = None
		self._rectverts = None
		self._clip = True
		self._bins = bins
		try:
			self._xlim = xlim = bins[0], bins[-1]
		except TypeError:
			self._xlim = xlim = None
		self._ylim = 0,1
		self._title = title
		self._world = world
		self._background = None
		self._kwargs = kwargs
		self._fig = mpl.figure.Figure(figsize=(5,2.5), dpi=100)
		self._ax = ax = self._fig.add_subplot(111, title=title)
		ax.set_title(self._title, fontsize='x-small')
		ax.set_ylim((0,1))
		if xlim:
			ax.set_xlim(xlim)
		#grid the widget to master
		FigureCanvasTkAgg.__init__(self, self._fig, master=master)
		#self.get_tk_widget().grid(row=0,column=1)
	def setup(self):
		logging.debug('Enter Histogram.setup.')
		# create the initial histogram
		newtops = self.update_data()
		self.create_rectangles_as_pathpatch()
		logging.debug('Exit Histogram.setup.')
	def update(self):
		"""Return None. Update the histogram."""
		logging.debug('Enter Histogram.update.')
		# ('update the data (-> _tops)' )
		self.update_data()
		#update the vertices
		newtops = self._tops
		self._rectverts[1::5,1] = newtops
		self._rectverts[2::5,1] = newtops
		self.show()  #crucial!
		logging.debug('Exit Histogram.update.')
	def update_data(self):
		"""Return sequence, the new data from `_datafunc`.
		"""
		logging.debug('Enter Histogram.update_data.')
		data = self._datafunc()
		if self._clip and self._xlim:
			data = np.clip(data, *self._xlim)
		tops, edges = np.histogram(data, bins=self._bins, normed=False, **self._kwargs)
		self._tops, self._edges = tops, edges
		if self.adjust_ylim(tops):
			self._ax.set_ylim(self._ylim)
		logging.debug('Exit Histogram.update_data.')
		return tops
	def create_rectangles_as_pathpatch(self):
		global rectverts
		"""
		The tricky part: we construct the rectangles as a `mpl.path`
		http://matplotlib.sourceforge.net/api/path_api.html
		and then add a mpl.patches.PathPatch to the axes.
		(Thanks to John Hunter, who posted this solution!!)
		"""
		ax = self._ax
		tops, edges = self._tops, self._edges
		# first create the vertices and associated rectvertcodes
		self._rectverts = rectverts = self.create_rectverts(tops, edges)
		numrects = len(tops) #keep it this way
		self._rectvertcodes = rectvertcodes = self.create_rectvertcodes(numrects)
		barpath = mpl.path.Path(rectverts, rectvertcodes)
		patch = mpl.patches.PathPatch(barpath, facecolor='green', edgecolor='yellow', alpha=0.5)
		self._patch = ax.add_patch(patch)
		self._xlim = xlim = (edges[0],edges[-1])
		ax.set_xlim(xlim)
	def create_rectverts(self, tops, edges):
		"""Return array, the vertices for rectangles with
		bottoms 0, tops `tops`, and edges `edges`.
		Please refer to `create_rectvertcodes`:
		although the vert for the closepoly is ignored,
		we still need it to align with the rectvertcodes.
		"""
		numrects = len(tops) #keep it this way
		nverts = numrects*(1+3+1)
		#we will replace the tops; bottoms remain 0
		rectverts = np.zeros((nverts, 2))
		# get the corners of the rectangles for the histogram
		left_edges = np.array(edges[:-1])
		right_edges = np.array(edges[1:])
		rectverts[0::5,0] = left_edges
		rectverts[1::5,0] = left_edges
		rectverts[1::5,1] = tops
		rectverts[2::5,0] = right_edges
		rectverts[2::5,1] = tops
		rectverts[3::5,0] = right_edges
		return rectverts
	def create_rectvertcodes(self, numrects):
		"""Return 1d array, the codes for rectangle creation.
		(Each rectangle is one moveto, three lineto, one closepoly.)
		"""
		numverts = numrects*(1+3+1)
		rectvertcodes = np.ones(numverts, int) * mpl.path.Path.LINETO
		rectvertcodes[0::5] = mpl.path.Path.MOVETO
		rectvertcodes[4::5] = mpl.path.Path.CLOSEPOLY
		return rectvertcodes
	def adjust_ylim(self, tops):
		"""Return bool. Resets `_ylim`
		(if needed to accommodate `_ydata`).
		"""
		adjust = False
		ymax = max(tops)
		ylimlow, ylimhigh = self._ylim
		if (ymax > ylimhigh) or (ymax < 0.3 * ylimhigh):
			ylimhigh = 1.5 * ymax
			adjust = True
		self._ylim = ylimlow, ylimhigh
		return adjust


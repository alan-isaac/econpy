"""A collection of simple classes for implementing
agent-based simulations.

  - Agent: a basic agent class (has a position that
    it can change).
  - Patch: a basic patch class (has a permanent
    position and knows what agents are "on" it).
  - GridWorld: a basic world class for gridlike
    worlds (initializes and runs the simulation)
  - GridWorldGUI: a basic observer for a GridWorld,
    but with a graphical display.  Easily add
    monitors and graphs.

Users of earlier versions should not that a ``GridWorldGUI``
no longer subclasses ``GridWorld``
but rather owns an instance of ``GridWorld``.

A note on observers: if you want to collect info from
or display your world, use an observer, like GridWorldGUI.
Note that a world observer will create agent observers
and patch observers using the class attributes
_PatchObserverType and _AgentObserverType.  If you
subclass a world observer, consider overriding these attributes.

:note: we draw the following semantic distinction:
  a world has locations, which can be occupied by
  objects, which have *positions*.  Coordinates that
  do not represent a world location may be replaced
  by None but are generally transformed
  into a world location (e.g., torus like objects will
  "wrap" the coordinates to produce a location).
:todo: Currently the main GUI (e.g., GridWorldGUI) controls
  plot and histogram updating.  It seems more natural to just
  let plots and histograms be other observers of the world and
  thus receive notifications from the world instead.
  Think about this. chk

:requires: Python 2.6+ (for itertools.product and for
  the new turtle.py module)
  with Matplotlib_ (for graphics) and NumPy_ (for Matplotlib_)
:author: Alan G Isaac <alan dot isaac @ gmail dot com>
:thanks: Kentaro Murayama suggested treating screen
  clicks as patch clicks, which allows patch clicks
  without any rectangle creation.
:thanks: John Hunter showed in detail how to create a
  dynamic histogram using a PathPatch
  (Aug 8, 2009, Matplotlib users mailing list)
:change: Agent.patch_here() replaced by patch property

.. _NumPy: http://numpy.scipy.org/
.. _Matplotlib: http://matplotlib.sourceforge.net/
"""
from operator import add, methodcaller
import logging, math, operator, random, turtle
from itertools import imap as map, izip, starmap, takewhile
from itertools import product as cartesian_product
from collections import defaultdict, deque
import Tkinter as tk


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
	"""Return list (default) or generator, the Moore neighborhood of `center`,
	where by default ``center=(0,0)`` is the 2d origin.
	(Equivalently. returns the Moore neighborhood of any point
	as characterized by offsets from its location).
	Change the center dimension to change the dimension of the hood.
	By default ``keepcenter=False``: hood does not include origin.

	Parameters
	----------
	radius : int
	  the radius of the neighborhood
	center : tuple
	  the center of the neighborhood
	keepcenter : bool
	  True to return center else False
	aslist : bool
	  True to force return as list; False to return unspecified iterable
	"""
	offsets = range(-radius, radius+1)
	dim = len(center)
	hood = cartesian_product(offsets, repeat=dim)
	if center != (0,)*dim:
		hood = ( tuple(map(add, center, nbr)) for nbr in hood )
	if not keepcenter:
		hood = (loc for loc in hood if loc != center)
	if aslist:
		hood = list(hood)
	return hood

def cached_moore_neighborhood(radius, center=(0,0), keepcenter=False, aslist=True, cache = dict()):
	"""Return list or tuple, the Moore neighborhood of `center`.
	Maintains a cache of produced neighborhoods.
	Use insted of `moore_neighborhood` when the cached can be valuable.
	:comment: be very careful if you use the default cache; there is only one!
	:comment: No maximum size is imposed on the cache!
	"""
	args = (radius,center,keepcenter)
	try:
		result = cache[args]
	except KeyError:
		result = moore_neighborhood(radius, center=center, keepcenter=keepcenter, aslist=False)
		result = list(result) if aslist else tuple(result)
		cache[args] = result
	return result

def register_person(screen):
	"""Return None. Register a simple person shape.
	"""
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

def round2int(coordinates):
	"""Return tuple of int, the rounded values of the coordinates.
	:note: The coordinates are *not* constrained to valid locations.
	:note: This is mostly for the use of patches and of gridlike subclasses.
	"""
	coordinates = map(round, coordinates)
	#chk next line not needed in Python 3
	coordinates = map(int, coordinates)
	return tuple(coordinates)

def rgb2str(r, g, b, colormode=1.0):
	#r, g, b = color
	if colormode == 1.0:
		if not all( (0<=ci<=1) for ci in (r,g,b) ):
			raise ValueError('Color values must be in [0,1]')
		r,g,b = round2int((ci*255) for ci in (r,g,b) )
	if not all( (0<=ci<=255) for ci in (r,g,b) ):
		raise ValueError('Color values must be in [0,255]')
	color = '#{0:02X}{1:02X}{2:02X}'.format(r,g,b)
	return color

def colorspec2colorstr(color, colormode=1.0):
	if not isinstance(color, str): #must be a 3-tuple of floats
		color = rgb2str(*color, colormode=colormode)
	return color

def categorize(func, seq):
	"""Return mapping from categories to lists
	of categorized items.
	:note: `func` must return hashable objects
	:note: `seq` can be any *finite* iterable
	"""
	d = defaultdict(list)
	for item in seq:
		d[func(item)].append(item)
	return d

def maximizers(func, seq):
	"""Return list,  the items in `seq` that maximize `func`.
	:note: `func` must return comparable (e.g., numeric) results
	:note: `func` is evaluated once for each item
	:note: `seq` can be any *finite* iterable
	"""
	best = []
	seq = iter(seq)
	try:
		item = next(seq)
		maxval = func(item)
		best.append(item)
	except StopIteration:
		pass
	for item in seq:
		val = func(item)
		if val > maxval:
			maxval = val
			best = [item]
		elif val == maxval:
			best.append(item)
	return best

		
	


################## BEGIN TOPOLOGIES
#Topologies are the spaces in which agents reside

class Observable(object):
	"""Provide a MixIn for observable classes.
	Ordinarily a subclass will initialize _observers
	to an empty set.
	"""
	_observers = tuple()
	def register_observer(self, observer):
		try:
			self.observers.add(observer)
		except AttributeError:
			msg = '{0} does not allow adding observers.'
			raise NotImplementedError(msg)
	def notify_observers(self, event=None, **kwargs):
		for observer in self._observers:
			observer.update(event=event, **kwargs)
	#PROPERTIES
	# read-only
	@property
	def observers(self):
		return self._observers

class LocationMap(dict):
	"""Maps agents to locations.
	Here coordinates are NOT constrained
	and multiple occupancy is allowed.
	Subclasses should override `location`
	to impose constraints.
	"""
	_shape = None
	def set_position(self, agent, coordinates):
		"""Return tuple, the constrained coordinates.
		Calls `location(coordinates)`,
		which should properly constrain the coordinates.
		:note: Ordinarily this method is *not* overridden.
			(Override `location` instead.)
		:note: does not change agent state!
		"""
		location = self.location(coordinates)
		self[agent] = location
		return location
	def location(self, coordinates):
		"""Return tuple, the coordinates.
		(I.e., the coordinates are not constrained.)
		:note: Override this in subclasses!
		"""
		return coordinates
	def locations(self, coordinates):
		"""Return iterable, the (possibly constrained) locations.
		Subclasses will generally constrain the valid locations
			(override `location` to do this)
			and may return ``None`` for invalid coordinates.

		coordinates : iterable of tuple
			a collection of coordinate tuples
		"""
		return map(self.location, coordinates)
	def is_empty(self, coordinates):
		"""Return bool,
		True if location not occupied else False."""
		location = self.location(coordinates)
		return location not in self.values()
	'''
	def place(self, objects, coordinates, constrain=True):
		"""Return None. Place `objects` at `coordinates`.
		Does **not** check for occupancy.
		Constrains to valid locations by default.
		"""
		logging.debug('Enter LocationMap.place.')
		if constrain:
			coordinates = self.locations(coordinates)
		for obj, loc in zip(objects, coordinates):
			if not hasattr(obj,'position'):
				logging.warn('Creating position attr for {0}.'.format(obj))
			obj.position = loc
			self[obj] = loc
		logging.debug('Exit LocationMap.populate.')
	'''

class BoundedLocationMap(LocationMap):
	"""Provides a bounded location map.
	Valid coordinates are nonnegative and less than shape.
	:todo: allow origin translation
	"""
	def __init__(self, shape):
		"""Return None.

		shape : tuple of int
			the extent of the map
		"""
		LocationMap.__init__(self)
		self._shape = shape
		self._ndim = len(shape)
	def location(self, coordinates):
		"""Return tuple or None, the location.
		(Overriding parent class to constrain location.)
		"""
		shape = self.shape
		if self._ndim != len(coordinates):
			msg = 'Shape {0} does not match coordinates {1}'
			raise ValueError(msg.format(shape,coordinates))
		ok = all( (0 <= cn <= sn) for (cn,sn) in zip(coordinates, shape) )
		if not ok:
			msg = 'Shape {0} does not match coordinates {1}'
			logging.warn(msg.format(shape,coordinates))
		return coordinates if ok else None
	#properties
	# read-only
	@property
	def shape(self):
		return self._shape

class FiniteGrid(BoundedLocationMap):
	"""Provides a mapping of agents to locations,
	where locations are constrained to a finite grid.
	Coordinates off the grid become ``None``.
	"""
	def location(self, coordinates):
		"""Return tuple or None,
		the corresponding location on the grid,
		or None if there is none.
		"""
		shape = self.shape
		if len(self.shape) != len(coordinates):
			msg = 'Shape {0} does not match coordinates {1}'
			raise ValueError(msg.format(self.shape,coordinates))
		coordinates = round2int(coordinates)
		location = tuple( xi%si for (xi,si) in izip(coordinates,shape) )
		if location != coordinates:
			msg = """Coordinates {0} are off the grid; location is None.
			(This can be a normal part of hood_locs computation.)"""
			logging.debug(msg.format(coordinates))
			location = None
		return location
	def random_locations(self, number, exclude=False):
		"""Return set of `number` random locations from the grid.
		If `exclude` is a tuple of agent types,
		only cells not containing these types are returned.
		If `exclude` is True, only empty cells are returned.
		If `exclude` is False, any cells may be returned.
		"""
		logging.debug('Enter FiniteGrid.random_locations.')
		if number != abs(int(number)):
			errmsg = '{0} is not a positive integer.'.format(number)
			raise ValueError(errmsg)
		shape = self._shape
		n_possible = reduce(operator.mul, shape)
		if exclude is True:
			occupied = set(self.values())
		elif exclude:
			occupied = set(val for key,val in self.items() if isinstance(key,exclude))
		else:
			occupied = set()
		n_possible -= len(occupied)
		if (number > n_possible):
			errmsg = '{0} is too many objects to add to this grid.'
			raise ValueError(errmsg.format(number))
		locations = set()
		while len(locations) < number:
			loc = tuple( map(random.randrange, shape) )
			if loc not in occupied:
				locations.add(loc)
				occupied.add(loc)
		assert len(locations) == number
		logging.debug('Exit FiniteGrid.random_locations.')
		return locations

RectangularGrid = FiniteGrid #alias

class TorusGrid(FiniteGrid):
	"""Maps agents to coordinates;
	coordinates are constrained to the torus by wrapping."""
	def location(self, coordinates):
		"""Return tuple, the constrained location.
		"""
		shape = self.shape
		if len(shape) != len(coordinates):
			msg = 'Shape {0} does not match coordinates {1}'.format(self.shape,coordinates)
			raise ValueError(msg)
		coordinates = round2int(coordinates)
		return tuple( xi%si for (xi,si) in izip(coordinates,shape) )


################## END TOPOLOGIES



#BEGIN WORLD CLASSES

class WorldBase(Observable):
	"""Provides a base class for worlds.
	"""
	_observers = set()
	_agents = set()
	_agentcounts = 0
	_iteration = 0
	_update_frequency = 1
	_topology = None
	_patches = None
	maxiter = None
	def __init__(self, topology=None):
		"""Return None.
		Ordinarily, a ``WorldBase`` will be initialized
		*with* a topology.
		"""
		logging.debug('Enter WorldBase.__init__.')
		self._topology = topology
		self.initialize()
		logging.debug('Leave WorldBase.__init__.')
	def setup(self):
		"""Return None.
		User should override this method to do model set up.
		(Oftened called by a SetUp button in a GUI.)"""
	def set_topology(self, topology):
		"""Return None.
		Called by `__init__`.
		"""
		if self._topology:
			logging.warn('Resetting topology. (Not usually desirable.)')
		self._topology = topology
		self.notify_observers('set_topology')
	def initialize(self):
		"""Return None.
		Commands to be executed at instance creation.
		Users should override this.
		"""
	def location(self, coordinates):
		"""Override this to constrain locations appropriately."""
		raise NotImplementedError
	def locations(self, coordinates):
		"""Return iterable, the (possibly constrained) locations.
		Subclasses will generally constrain the valid locations
			(override `location` to do this)
			and may return ``None`` for invalid coordinates.

		coordinates : iterable of tuple
			a collection of coordinate tuples
		"""
		return map(self.location, coordinates)
	def reset(self):
		self.stop()
		self._agents = set()
		self._agentcounts = 0
		self._iteration = 0
		self._topology.clear()  #remove agents from space
		self._patches = None
		self.notify_observers(event='reset')
	def run(self, maxiter=None):
		"""Return None.  Run the simulation
		by repeatedly calling the schedule.
		"""
		maxiter = maxiter or self.maxiter
		self._stop = False
		while self.keep_running() \
				and (self._iteration < (maxiter or self._iteration+1)):
			self._iteration += 1
			#logging.debug('Begin iteration {0}'.format(self._iteration))
			self.notify_observers('_begin_iteration')
			#schedule is run once each iteration
			self.schedule()
			#updating can be less frequent
			if not (self._iteration % self._update_frequency):
				#logging.debug('_update')
				self.notify_observers('update')
			self.notify_observers('_end_iteration')
			#logging.debug('End iteration {0}'.format(self._iteration))
		self.clean_up()
	def keep_running(self):
		return not self._stop
	def stop(self):
		"""Return None. Sets `_stop` to True,
		terminating the loop in `run`.
		"""
		self._stop = True
	def schedule(self):
		"""Return None. Schedule actions to be executed each iteration.
		User should override this method."""
		raise NotImplementedError('You must override ``schedule``.')
	def clean_up(self):
		"""Return None.
		Final WorldBase actions after stop running."""
		return NotImplemented
	#agent related methods
	def create_agents(self, AgentType, number=0, locations=None):
		"""Return list, the newly created agents.
		Locations are assigned by `place_randomly` if not specified.
		"""
		logging.debug('Enter WorldBase.create_agents.')
		if number==0:
			try:
				number = len(locations)
			except TypeError: #must be generator
				try:
					locations = tuple(locations)
				except TypeError:
					msg = 'Must provide a `number` of agents or `locations`.'
					raise ValueError(msg)
				number = len(locations)
		else:
			number = int(number)
		if locations is None:
			locations = self.random_locations(number)
		#need to know world to complete initialization!
		new_agents = tuple( AgentType(world=self, position=loc)
			for loc in locations )
		for agent in new_agents:
			self.register_agent(agent) #handles patch registration
			self.set_position(agent, agent.position)
		assert all(agent.world for agent in new_agents)
		assert self._agentcounts == len(self._agents)
		#observers create agent observers when notified
		self.notify_observers('create_agents', agents=new_agents)
		logging.debug('Exit WorldBase.create_agents.')
		return new_agents
	def register_agent(self, agent):
		"""Return None.  Register agent with world. """
		self._agents.add(agent)
		self._agentcounts += 1      #for error checking
		if self._patches:
			patch = self.patch_at(agent.position)
			patch.register_agent(agent)
	def unregister_agent(self, agent):
		"""Return None.  Unregister agent with world. """
		self._agents.remove(agent)
		self._agentcounts -= 1      #for error checking
		if self._patches:
			patch = self.patch_at(agent.position)
			patch.unregister_agent(agent)
		agent.world = None
	'''
	def place_randomly(self, agents):
		raise NotImplementedError()
	def place(self, agents, locations):
		logging.debug('Enter WorldBase.place.')
		#recall that agent.set_position calls world.set_position
		for agent, loc  in zip(agents, locations):
			agent.set_position(loc)
		logging.debug('Exit WorldBase.place.')
	'''
	def set_position(self, agent, coordinates):
		"""Return tuple, the location corresponding to `coordinates`.
		Sets the agent position in the topology
		and adjusts the patch registration.
		Does *not* change agent state.
		"""
		oldpos = agent.position
		#does *not* enforce single occupancy; does *not* change agent.position
		location = self.topology.set_position(agent, coordinates)
		occupants = self.agents_at(location, agent.__class__)
		occupants.discard(agent) #other occupants only
		if occupants: #warn if another occupant
			msg = '{0} is occupied; moving there anyway.'
			logging.warn(msg.format(coordinates))
		if self._patches and oldpos != location: #change patch registration
			oldpatch = self.patch_at(oldpos)
			newpatch = self.patch_at(location)
			oldpatch.unregister_agent(agent)
			newpatch.register_agent(agent)
		return location
	def agents_at(self, location, AgentType=None):
		"""Return set, the agents at `location`.
		"""
		if self._patches:
			all_agents = self.patch_at(location).agents
		else:
			all_agents = set(agent for (agent,loc) in self._topology.items() if loc==location)
		if AgentType:
			all_agents = set(agent for agent in all_agents if isinstance(agent,AgentType))
		return all_agents
	def get_agents(self, AgentType=None):
		"""Return list of agents:
		all instances of `AgentType`
		or all agents (if `AgentType` is None).
		:note: `AgentType` can be a tuple of agent types.
		"""
		if AgentType is None:
			return list(self._agents)
		else:
			return list(a for a in self.agents if isinstance(a,AgentType))
	#patch related methods
	def create_patches(self, PatchType):
		"""Return tuple of tuples.  Creates the patches for this world.
		Patch creation should take place **before** agent creation.
		:todo: chk generalize to Nd
		"""
		logging.debug('Enter create_patches.')
		width, height = self.topology.shape
		if self._patches is not None:
			logging.warn('This world already seems to have patches.')
		#chk should a patch know its world?
		#:note: rows correspond to first (x) coordinate!
		patches = tuple(tuple(PatchType(world=self, position=(r,k))
						for k in range(height)) for r in range(width))
		self._patches = patches
		self.notify_observers('create_patches')  #allow GUI observers display patches
		logging.debug('Leave create_patches.')
		return patches
	def patches_at(self, coordinates, preconstrained=True):
		"""Return iterable, the patches at the locations.
		"""
		patches = self._patches
		if not preconstrained: #get set of constrained locations
			locations = self.locations(coordinates)
		else:
			locations = coordinates
		patch_at = lambda loc: self.patch_at(loc,True)
		return map(patch_at, locations )
	def patch_at(self, coordinates, preconstrained=False):
		"""Return Patch if patch at location else None.
		If `preconstrained` is True, then `location` is not tested for constraint.
		"""
		patches = self._patches
		if not preconstrained:
			location = self.location(coordinates)
		else:
			location = coordinates
		"""
		:note: assumes _patches is a list!
		:note: thanks to Steven D'Aprano
		  for suggesting operator.getitem to replace list.__getitem__
		:note: can handle higher dimensions (e.g., 3d)
		"""
		if location is not None:
			location = round2int(location)
			result = reduce(operator.getitem, location, patches)
			return result
	#PROPERTIES
	# read-only
	@property
	def agents(self):
		"""Return list, the world's agents.  (Agents subsequently added
		to the world will *not* be included.)
		"""
		return list(self._agents)
	@property
	def patches(self):
		"""Return generator, all the patches in `_patches`."""
		if self._patches:
			return (patch for row in self._patches for patch in row)
	@property
	def iteration(self):
		return self._iteration
	@property
	def observers(self):
		return self._observers
	@property
	def topology(self):
		return self._topology
	# read-write
	@property
	def update_frequency(self):
		return self._update_frequency
	@update_frequency.setter
	def update_frequency(self, value):
		self._update_frequency = int(value)

class GridWorld(WorldBase):
	"""Provides a class for grid-world simulations."""
	def is_empty(self, coordinates):
		"""Return bool,
		True if location not occupied else False."""
		return self._topology.is_empty(coordinates)
	'''
	def place_randomly(self, agents, exclude=True):
		logging.debug('Enter GridWorld.place_randomly.')
		locations = self.random_locations(len(agents), exclude=exclude)
		self.place(agents, locations)
		logging.debug('Exit GridWorld.place_randomly.')
	'''
	def random_locations(self, number, exclude=False):
		return self._topology.random_locations(number, exclude=exclude)
	def location(self, coordinates):
		"""Return tuple or None, the constrained location (as a tuple)
		or None (if there is no corresponding constrained location).
		"""
		return self._topology.location(coordinates)
	def locations(self, coordinates):
		"""Return set, the constrained valid locations.
		Valid locations are determined by the topology,
		which will return None for invalid locations,
		which is discarded here.
		On some topologies two different sets of coordinates can
		map to the same location; only the one location is returned
		in this case.
		"""
		locations = set( self._topology.locations(coordinates) )
		locations.discard(None)
		return locations
	def hood_locs(self, shape, radius, center=(0,0), keepcenter=False):
		"""Return set, the coordinates of the neighborhood patches.
		Parameters
		----------
		shape : str
		  E.g., 'moore'
		radius : int
		  the radius of the neighborhood
		center : tuple
		  the center of the neighborhood
		keepcenter : bool
		  True to return center else False
		"""
		logging.debug('Enter GridWorld.hood_locs.')
		if shape.lower() == 'moore':
			coordinates = moore_neighborhood(radius=radius, center=center,
											keepcenter=keepcenter,
											aslist=False)
			locations = self.locations(coordinates)
		else:
			raise ValueError('Unsupported neighborhood type.')
		logging.debug('Exit GridWorld.hood_locs.')
		return locations
	def kill(self, agent):
		assert (not agent.defunct)
		del self._topology[agent]
		self.unregister_agent(agent) #unregisters from patch too
		self.notify_observers('kill_agent', agent=agent)
		del agent

#END WORLD CLASSES

#BEGIN OBSERVER CLASSES
class Observer(object):
	"""Provides an observer of a *single* subject.
	Maintains a reference to the subject.
	(Todo: make that a weak reference.)
	Registers itself with the subject as an observer.
	The subject will call the observer's `update` method.
	"""
	def __init__(self, subject):
		"""Return None.
		"""
		try:
			subject.register_observer(self)
		except AttributeError:
			msg = '{0} is not an observable type.'.format(type(subject))
			raise ValueError(msg)
		self._subject = subject
		self._active = True
	def update(self, event, **kwargs):
		"""Return None.
		Users should subclass and override the update method!
		"""
		if self.active: #what to do when the observer is "active"
			pass
		else: #what to do when the observer is not "active"
			pass
	def _tracer(self, val):
		"""Return None.
		Subclasses override the _tracer method!"""
		pass
	#methods for turning the observer off and on
	def off(self, ** kwargs):
		oldstate = self._active
		self._active = False
		self._tracer(False)
		return oldstate
	def on(self, **kwargs):
		oldstate = self._active
		self._active = True
		self._tracer(True)
		return oldstate
	def observe(self, newstate):
		"""Return bool, the old state.
		Turn observation on and off.
		"""
		oldstate = self._active
		newstate = self._active = bool(newstate)
		self._tracer(newstate)
		return oldstate
	#PROPERTIES
	# read-only
	@property
	def subject(self):
		return self._subject
	@property
	def active(self):
		return self._active

class AgentObserver(Observer, turtle.RawTurtle):
	def __init__(self, subject, screen=None, **kwargs):
		Observer.__init__(self, subject)
		turtle.RawTurtle.__init__(self, canvas=screen)
		self.pen(pendown=False, speed=0)
		# RawTurtle cannot yet be initialized with a position
		self._goto(subject.position)
	def update(self, event=None, **kwargs):
		if event == 'display':
			fillcolor = kwargs.get('fillcolor')
			if fillcolor is not None:
				self.fillcolor(fillcolor)
			shape = kwargs.get('shape')
			if shape is not None:
				assert isinstance(shape, str)
				self.shape(shape)
			shapesize = kwargs.get('shapesize')
			if shapesize is not None:
				self.shapesize(*shapesize)
		#observer is notified when subject moves
		elif event == 'goto':
			#coordinates = kwargs.get('coordinates',(0,0))
			coordinates = kwargs.get('coordinates')
			self._goto(coordinates)
		else:
			msg = '{0} is not a recongized event.'.format(event)
			logging.info(msg)

class PatchObserver(Observer):
	"""Provides a patch observer
	to display a `Patch` on a Tkinter canvas.
	The only visual characteristic of a patch is its color.
	Patches are clickable (but via canvas for now).
	"""
	'''
	def __init__(self, world, position, fill=''):
		self._fillcolor = fill
		self._rectangle = None
		self._canvas = world.screen.cv
		#PatchBase will call initialize
		PatchBase.__init__(self, world=world, position=position)
	'''
	def __init__(self, subject, screen=None):
		Observer.__init__(self, subject)
		self._turtle_screen = screen
		self._canvas = screen.cv #same as getcanvas()
		self._rectangle = None  #will be an int, the canvas item number
		self._make_rectangle()  #sets self._rectangle
	def _make_rectangle(self, **kwargs):
		"""Return None.
		Update the _patches_rectangles attribute.
		"""
		color = getattr(self.subject, 'fillcolor', None)
		if color:
			kwargs['fill'] = color
		cv = self._canvas
		#Create an invisible polygon item on canvas
		#   remember, rect is just an int (item number)
		rect = cv.create_rectangle(0, 0, 0, 0, fill="", outline="")
		self._rectangle = rect
		#next we can position and fill the rectangle
		x, y = self.subject.position  #chk 2d only
		x1 = x - 0.5
		y1 = y - 0.5
		x2 = x + 0.5
		y2 = y + 0.5
		self._draw_rectangle(rect, [(x1, y1), (x2, y2)], **kwargs)
	def _draw_rectangle(self, item, coordlist, **kwargs):
		"""Return None.
		Configure rectangle according to provided arguments:
		fill=None, outline=None, width=None, top=False
		coordlist is sequence of coordinates
		fill is filling color
		outline is outline color
		top is a boolean value, which specifies if polyitem
		will be put on top of the canvas' displaylist so it
		will not be covered by other items.
		:note: for Tk backend only
		:note: scaling!
		"""
		screen = self._turtle_screen
		cl = []
		#scale the rectangle to match screen!
		for x, y in coordlist:
			cl.append(x * screen.xscale)
			cl.append(-y * screen.yscale)
		screen.cv.coords(item, *cl)
		screen.cv.itemconfigure(item, **kwargs)
	def update(self, event=None, **kwargs):
		if event == 'display':
			fillcolor = kwargs.get('fillcolor')
			if fillcolor is not None:
				assert isinstance(fillcolor, str)
				rect = self._rectangle
				canvas = self._canvas
				canvas.itemconfigure(rect, fill=fillcolor)
		else:
			msg = '{0} is not a recongized event.'.format(event)
			logging.info(msg)
	'''
	#PROPERTIES
	# read-only
	@property
	def fillcolor(self):
		return self._fillcolor
	@fillcolor.setter
	def fillcolor(self, *color):
		"""Return None.  Set the fillcolor of the patch.
		Recommended: use r,g,b color scheme (0<=r,g,b<=1).
		"""
		if len(color) == 1:
			if isinstance(color[0], str):
				color = self.world.screen._colorstr(color)
			else:
				raise ValueError('bad color')
		else: #must be a 3-tuple of floats
			color = rgb2str(*color)
			if not self._fillcolor == color: #reset color only if needed
				# (rectangle propery will creates a rectangle if nec)
				rect = self.rectangle
				self._canvas.itemconfigure(rect, fill=color)
				self._fillcolor = color
	'''

class GridWorldCLI(Observer):
	_PatchObserverType = None
	def	__init__(self, topology):
		logging.debug('Enter GridWorldCLI.__init__.')
		self._topology = topology
		self.initialize()
		logging.debug('Leave GridWorldCLI.__init__.')


class GridWorldGUI(Observer, tk.Frame):
	"""Provides a an observe (with a screen) for a GridWorld."""
	_AgentObserverType = AgentObserver
	_PatchObserverType = PatchObserver
	def __init__(self, subject):
		logging.debug('Enter GridWorldGUI.__init__.')
		Observer.__init__(self, subject)
		tk.Frame.__init__(self)
		try: self.master.title('GridWorld')
		except AttributeError: pass
		#careful: a Frame has a grid attribute; NOT a topology!
		tk.Frame.grid(self)
		turtle._root = self
		#convenience declarations
		self._turtle_screen = None
		self._button_frame = None
		self._slider_frame = None
		self._monitor_frame = None
		self._graph_frame = None
		self._buttons = dict()  # maps labels to buttons
		self._setup_button = None
		self._monitors = list()
		self._clickmonitors = defaultdict(list)
		self._graphs = list()
		self._patches_rectangles = dict() #map patches to rectangles
		#GUI request lists
		self.__button_requests = list()
		self.__slider_requests = list()
		self.__clickmonitor_requests = list()
		self.__monitor_requests = list()
		self.__graph_requests = list()
		#initializations must come **before** display setup
		# button, slider, and monitor requests should be
		# made in the `gui` method
		self.gui()
		#setup_display will implement the
		# button, slider, and monitor requests
		# (must come **after** `initialize`!!)
		self.setup_display()
		self.set_topology()
		self._agent_observers = set()  #chk discard upon kill
		self._patch_observers = set()
		if subject.agents:
			self.add_agent_observers(subject.agents)
		logging.debug('Leave GridWorldGUI.__init__.')
	def gui(self):
		"""User can override this with desired initializations.
		This is the right place to add buttons, sliders, etc."""
	def setup_display(self):
		#setup screen
		self.setup_turtlescreen()
		self._setup_button_frame()
		self._setup_slider_frame()
		self._setup_monitor_frame()
		self._setup_graph_frame()
	def setup_turtlescreen(self):
		logging.debug('Enter GridWorldGUI.setup_turtlescreen')
		my_turtle_frame = tk.Frame(master=self, relief='raised', borderwidth=2)
		turtle._Screen._root = my_turtle_frame
		turtle._Screen._canvas = turtle.ScrolledCanvas(my_turtle_frame, 500, 500, 500, 500)
		my_turtle_frame.grid(row=0, column=1, rowspan=3)
		self._turtle_screen = screen = turtle.Screen()
		turtle.TurtleScreen.__init__(screen, screen._canvas)
		screen.onclick(self.clicked_at, add=True)
		screen_canvas = screen._canvas
		screen_canvas.grid(row=0, column=1)
		turtle.RawTurtle.screens = [screen]
		logging.debug('Exit GridWorldGUI.setup_turtlescreen')
	def set_topology(self):
		"""Return None.
		Called by `__init__`.
		"""
		x, y = self.subject.topology.shape #2d only!! chk
		#set screen coordinates
		screen = self._turtle_screen
		#leave a little (0.5) space at each edge
		screen_coordinates = -1, -1, x, y
		screen.setworldcoordinates(*screen_coordinates)
	def clicked_at(self, *pos):
		"""
		The following may seem a bit roundabout.
		Patches do not receive clicks (yet), so we report
		clicks received by the screen to the relevant patch.
		This is probably a good idea even if patches can receive clicks,
		since it avoids concerns about accuracy of rectangle
		placement, overlap, etc.
		"""
		logging.debug('Enter GridWorldGUI.clicked_at')
		#todo: change this if patches become turtles (unlikely)
		patch = self.subject.patch_at(pos)
		self.handle_click1(subject=patch, location=pos)
	def add_button(self, label, callback):
		"""Return None. Appends a button request,
		which will be acted upon during setup_display.
		If the callback is a string, it is assumed to be
		a callable attribute of the subject.
		Otherwise it is assumed to be an arbitrary callable.
		"""
		if isinstance(callback, str): #must be an attribut of the subject
			callback = getattr(self.subject, callback)
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
				setattr(self.subject, attr, float(x))
			return cmd
		#SLIDER FRAME
		slider_frame = tk.Frame(master=self, relief='flat', borderwidth=0)
		self._slider_frame = slider_frame
		slider_frame.grid(row=1,column=0)
		sliders = self.__slider_requests
		for ct, slider in enumerate(sliders):
			label, attr, from_, to, res = slider
			init_val = getattr(self.subject, attr)
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
		(User should call this method in an overridden `initialize` method.)
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
			#:note: _clickmonitors is a defaultdict(list), so we map from
			#  object types to a list of monitors
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
				graph = Histogram(datafunc=datafunc, master=graph_frame, title=title, **kwargs)
			elif kind == 'plot':
				graph = TSPlot(datafunc, master=graph_frame, title=title, world=self.subject, **kwargs)
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
		self._tracer(True)
		self._tracer(False)
		self._notify_monitors()
		self._setup_graphs()
	def _update(self):
		"""Return None.  Schedules the GUI updating.
		Note that we update the agent display via `turtle` module
		screen's tracer method.  This assumes we do not want a
		continuous update of the agent display.  
		"""
		self._tracer(True)
		self._tracer(False)
		self._notify_monitors()
		self._notify_graphs()
	def _setup_graphs(self):
		for graph in self._graphs:
			graph.setup()
	def _notify_graphs(self):
		logging.debug('Enter GridWorldGUI._notify_graphs')
		for graph in self._graphs:
			graph.update()
	def _notify_monitors(self):
		fmt = '{0}:\n{1!s:10}'
		for svar, label, func, period in self._monitors:
			if not self._iteration % period:
				svar.set( fmt.format(label, func()) )
	def on_click(self):
		pass # chkchk
	def reset(self):
		pass #chkchk
	def update(self, event=None, **kwargs):
		#a world can turn its observers on and off
		event_map = dict(
		_off = self.off,
		_on = self.on,
		_begin_iteration = self.off,
		_end_iteration = self.on,
		create_agents = self.add_agent_observers,
		create_patches = self.add_patch_observers,
		click = self.on_click,
		kill_agent = self.kill,
		reset = self.reset,
		)
		

		if event in ('_begin_iteration', '_off'):
			old_iter_state = self.off()
		elif event in ('_end_iteration', '_on'):
			self.on()
		elif event == 'set_topology':
			self.set_topology()
		elif event == 'create_agents':
			agents = kwargs.get('agents')
			self.add_agent_observers(agents)
			#self.update_agents()
		elif event == 'create_patches':
			self.add_patch_observers()
			#self.update_patches()
		elif event == 'kill_agent':
			agent = kwargs.get('agent')
			self.kill(agent)
		elif event == 'update':
			#if self._active: #problem: will stop graph updates
			self._update()
		elif event == 'reset':
			self.screen.clear()
			self._setup_button['state'] = 'normal'
		elif event == 'exit':
			self.exit()  #chk problem: update will be called after exit!
		else:
			msg = '{0} is not a recongized event.'.format(event)
			logging.info(msg)
	def add_agent_observers(self, agents):
		old_state = self.off()
		screen = self._turtle_screen
		AgentObserverType = self._AgentObserverType
		for agent in agents:
			#passing a canvas would require passing the scaling too
			observer = AgentObserverType(agent, screen=screen)
			#initialize display characteristics
			for attr in ('fillcolor', 'shape'):
				getattr(observer, attr)(getattr(agent, attr))
			getattr(observer, 'shapesize')(*getattr(agent, 'shapesize'))
			#note that more callbacks can be added!
			# see turtle.py documentation
			observer.onclick(self.click_reporter(observer), add=True)
			self._agent_observers.add(observer)
		self.observe(old_state)
	def click_reporter(self, observer):
		"""Return function, a click reporter.
		This is how we get around the fact that agents and patches are not
		actually clicked on, but rather their observers are.
		"""
		subject = observer.subject
		def report(*location):
			self.handle_click1(subject=subject, location=location)
		return report
	def handle_click1(self, subject, location):
		fmt = '{0}: {1!s:>10}'
		subject.clicked_at(*location)
		#get the click monitor map (type->monitor list)
		cmmap =  self._clickmonitors
		#iterate over the keys (object types)
		for ObjectType in cmmap:
			if isinstance(subject, ObjectType):
				#iterate over the list of monitors for that type
				for cm in cmmap[ObjectType]:
					svar, label, attributes = cm
					#create a report for this object+monitor
					report = [label]
					for attr in attributes:
						try:
							val = getattr(subject, attr)
							line = fmt.format(attr, val)
						except AttributeError:
							val = '(does not exist)'
							line = fmt.format(attr, val)
						finally:
							report.append(line)
					svar.set('\n'.join(report))
	def add_patch_observers(self):
		old_state = self.off()
		patches = self.subject.patches
		if patches is None:
			raise AttributeError('Create patches before adding patch observers.')
		screen = self._turtle_screen
		PatchObserverType = self._PatchObserverType
		observers = self._patch_observers
		for patch in patches:
			#passing a canvas would require passing the scaling too
			observer = PatchObserverType(patch, screen=screen)
			observers.add(observer)
		self.observe(old_state)
	def clean_up(self):
		#chk
		#self.mainloop()
		pass
	def kill(self, agent):
		"""Warning: there may be other references
		to the agent, which will remain!"""
		observers = list()
		for observer in agent.observers:
			observer.onclick(None) #remove reporter, which references agent
			if observer in self._agent_observers:
				self._agent_observers.discard(observer) #chk
				observers.append(observer) #error check
		assert len(observers)==1
		observer = observers[0]
		observer.hideturtle()
		observer.clear()
		screen = self._turtle_screen
		try:
			#thanks to Gregor Lingl for the next threee lines
			screen._delete(observer.currentLineItem)
			screen._delete(observer.drawingLineItem)
			screen._delete(observer.turtle._item)
			screen._delete(observer)
			screen._turtles.remove(observer)
			#chk remove from own lists of agents
		except KeyError:
			pass
	#patch related
	def update_patch_display(self):
		"""Return None.
		Updates the patch display.
		Users should override this method.
		"""
		patches = self.subject.patches
	def exit(self):
		self._active = False
		tk.Frame.destroy(self)
		if self.master:
			self.master.destroy()
	def _tracer(self, val):
		"""Return None.
		Set screen tracing.
		"""
		screen = self._turtle_screen
		try:
			screen.tracer(bool(val))
		except tk.TclError: #chk
			msg = """_tracer raised TclError.
			(This is normal when after observer exits.)"""
			logging.info(msg)
	#PROPERTIES
	# read-only
	@property
	def screen(self):
		return self._turtle_screen
#END OBSERVER CLASSES



#BEGIN AGENT CLASSES

class Agent(Observable):
	"""Provides a minimal agent.
	The only navigational capability is `set_position`!
	"""
	def __init__(self, world=None, position=(0,0)):
		self._defunct = False      #set to True as agent exits simulation
		self._observers = set()
		self._world = world
		self._initial_position = position
		self._position = position
		#convenience declarations for possible display
		self._fillcolor = 'black'
		self._shape = 'classic'
		self._shapesize = (0.3,0.3)
		#additional (user provided) initializations
		self.initialize()
		logging.debug('Agent initialized at position {0}'.format(self.position))
	def initialize(self):
		"""Dummy method for additional initializations in subclasses."""
	def _goto(self, coordinates):
		"""Return tuple.
		Move agent to coordinates represented by tuple.
		Notify observers of change in position

		:note: KEEP this design 
		  (may be called by turtle.Turtle methods in subclasses!)
		:note: need world.set_position *and* self._position
		:warning: 2d only.
		"""
		if not isinstance(coordinates, tuple):
			msg = '{0} is not valid coordinates'.format(args)
			raise ValueError(msg)
		if self.world:
			coordinates = self.world.set_position(self, coordinates)
		self._position = coordinates
		self.notify_observers('goto', coordinates=coordinates)
		return coordinates
	def set_position(self, *args):
		"""Return None.  Set the agent's position.
		Aliases: goto, setpos, setposition (in turtle.py).
		"""
		self._goto(*args)
	#####   patch related methods
	def neighborhood(self, shape, radius, keepcenter=False):
		"""Return generator, the neighborhood patches.
		The definition of a neighborhood depends on the world's topology.
		For example, points off the grid wrap for a TorusGrid topology
		but are discarded for a FiniteGrid topology.
		"""
		locations = self._world.hood_locs(
			shape=shape,
			radius=radius,
			center=self._position,
			keepcenter=keepcenter)
		patches = self._world.patches_at(locations, preconstrained=True)
		return list(patches)
	def patch_at(self, location, relative=False):
		"""Return Patch or None, the patch at self.position+rloc.
		CAUTION: note the use of relative location is not the default!!
		:note: also see the `patch` property
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
	def die(self):
		"""Return None. Remove agent from simulation.
		"""
		if not self._defunct:
			self._world.kill(self)
			self._defunct = True
		else:
			logging.warn('Trying to kill dead agent.')
	def display(self, **kwargs):
		"""Return None.  Set display attributes (by keyword).
		Note that these attributes have no visual meaning
		for an `Agent`: they are just ordinary attributes.
		(But observers may respond to them.)
		"""
		#restrict legal display keys
		dspkeys = ('fillcolor','shape', 'shapesize')
		for key, val in kwargs.items():
			if key in dspkeys:
				setattr(self, key, val)
			else:
				msg = """Unknown display attribute: {0}.
				Valid display attributes are {1}."""
				raise ValueError(msg.format(key,dspkeys))
	def clicked_at(self, *pos): #chkchk
		"""Return None.  This is the default `onclick` action for an agent.
		Naturally if the observer does not include a GUI,
		this method is not obviously useful.
		(Although equally naturally, it can still be called.)
		:note: don't notify observers; an observer can be the source of the click
		"""
		logging.debug('Enter Agent.clicked_at')
		pass
	#Agent properties
	# read-only
	@property
	def patch(self):
		return self._world.patch_at( self._position )
	@property
	def defunct(self):
		return self._defunct
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
	#convenience properties for possible display characteristics
	#(we could dispense with these) chk
	# read-write
	@property
	def shapesize(self):
		return self._shapesize
	@shapesize.setter
	def shapesize(self, tpl):
		old = self._shapesize
		if old != tpl:
			self._shapesize = tpl
			self.notify_observers('display', shapesize=tpl)
	@property
	def shape(self):
		return self._shape
	@shape.setter
	def shape(self, shape):
		old = self._shape
		if old != shape:
			assert isinstance(shape, str)
			self._shape = shape
			self.notify_observers('display', shape=shape)
	@property
	def fillcolor(self):
		return self._fillcolor
	@fillcolor.setter
	def fillcolor(self, rgb):
		old = self._fillcolor
		colorstr = colorspec2colorstr(rgb)
		if old != colorstr:
			self._fillcolor = colorstr
			self.notify_observers('display', fillcolor=colorstr)

class NavigatorAgent(Agent, turtle.TNavigator):
	"""Provides an agent with all the `turtle.Turtle` movement
	methods (but still no display characteristics).
	"""
	def __init__(self, world=None, position=(0,0)):
		turtle.NavigatorAgent.__init__(self)  #sets pos to (0,0)!
		Agent.__init__(self, world=world, position=position)


#END AGENT CLASSES

class PatchBase(Observable):
	def __init__(self, world=None, position=None):
		self._observers = set()
		self._world = world
		self._position = position
		self._agentset = set()
		self._agentcounts = 0      #for error checking
		#convenience declarations for possible display
		self._fillcolor = None
		#user initializations
		self.initialize()
	def initialize(self):
		"""Override this method to add intializations."""
	def register_agent(self, agent):
		if agent in self._agentset:
			raise ValueError('Registering agent that is already present.')
		self._agentset.add(agent)
		self._agentcounts += 1      #for error checking
	def unregister_agent(self, agent):
		try:
			self._agentset.remove(agent)
			self._agentcounts -= 1      #for error checking
		except KeyError:
			msg = 'Patch attempted to unregister agent that was not registered.'
			msg += ' Iteration {0}'.format(self.world.iteration)
			logging.warn(msg)
	def report_state(self):  #chk
		pass
	def get_agents(self, AgentType=None):
		"""Return set, the agents of type `AgentType`
		or all agents if `AgentType` is None.
		:note: `AgentType` can be a tuple of agent types.
		"""
		if AgentType is None:
			result = list(self._agentset)
		else:
			result = list(a for a in self._agentset if isinstance(a, AgentType))
		return result
	def display(self, **kwargs):
		"""Return None.  Set display attributes (by keyword).
		Note that these attributes have no visual meaning
		for a `PatchBase` (but `Patch` adds appropriate properties).
		"""
		#restrict legal display keys
		dspkeys = ('fillcolor',)
		for key, val in kwargs.items():
			if key in dspkeys:
				setattr(self, key, val) #will use any properties!
			else:
				msg = """Unknown display attribute: {0}.
				Valid display attributes are {1}."""
				raise ValueError(msg.format(key,dspkeys))
	#PROPERTIES
	# read-only
	@property
	def world(self):
		return self._world
	@property
	def position(self):
		return self._position
	@property
	def agents(self):
		return self._agentset
	# read-write
	@property
	def fillcolor(self):
		return self._fillcolor
	@fillcolor.setter
	def fillcolor(self, rgb):
		old = self._fillcolor
		colorstr = colorspec2colorstr(rgb)
		if old != colorstr:
			self._fillcolor = colorstr
			self.notify_observers('display', fillcolor=colorstr)


class Patch(PatchBase):
	def clicked_at(self, *pos):  #chkchk
		"""Return None.
		This is the default `onclick` action for a patch.
		"""
		logging.debug('Enter Patch.clicked_at')
		#self.notify_observers('click', coordinates=pos)



class TSPlot(FigureCanvasTkAgg):
	"""Provides a simple time-series plot of
	the most recent and previous 100 observations,
	where `datafunc` returns a single new observation.
	:note: this implementation relies on ideas discussed
		in the Matplotlib Cookbook
		http://www.scipy.org/Cookbook/Matplotlib/Animations
	"""
	def __init__(self, datafunc, master=None, title='', world=None, **kwargs):
		xlength = 101  #length of x-axis (max number of points plotted)
		self._did_setup = False
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
		self._did_setup = True
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
		if not self._did_setup:
			self.setup()
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
	"""
	def __init__(self, datafunc, bins, master=None, title='', **kwargs):
		"""
		Here `datafunc` must return a sequence (e.g., a list or array)
		containing a single iteration's data,
		and `bins` must be a sequence of bin edges.
		(Data outside the edges will be clipped into the lowest and highest bin.)
		:todo: allow specifying number of bins rather than edges
			(requires updating the rectverts)
		"""
		self._did_setup = False
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
		if not self._did_setup:
			newtops = self.update_data()
			self.create_rectangles_as_pathpatch()
			self._did_setup = True
		else:
			logging.warn('Ignoring multiple calls to Histogram.setup.')
		logging.debug('Exit Histogram.setup.')
	def update(self):
		"""Return None. Update the histogram."""
		logging.debug('Enter Histogram.update.')
		# ('update the data (-> _tops)' )
		if not self._did_setup:
			self.setup()
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
		"""
		The tricky part: we construct the histogram rectangles as a `mpl.path`
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


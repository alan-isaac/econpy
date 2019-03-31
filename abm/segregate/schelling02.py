"""
:note:
    The original Schelling model placed agents on a small grid.
    Here agents can occupy any point on the screen,
    as in Allen Downey's misnamed ``RacistWorld`` model.

:requires: Python 2.6+ (for new turtle.py)
"""
from __future__ import division
import turtle
import random, math
import time

class SchellingWorld(object):
    def __init__(self, n_agents=250):
        self.n_agents = n_agents
        self.history = list()
        self.screen = turtle.Screen()
        self.screen.tracer(False)
        agents = [SchellingAgent() for i in range(self.n_agents)]
        self.screen.tracer(True)
    def run(self, maxiter=200, trace_all=False):    
        screen = self.screen
        agents = list(screen._turtles)
        ct = 0
        while ct < maxiter:
            screen.tracer(trace_all)
            random.shuffle(agents)
            for t in agents:
                t.step()
            screen.tracer(True)
            self.add2history()
            ct += 1
    def add2history(self):
        """Return None.  Calculate segregation ratio
        and store in `history`.
        """
        agents = self.screen._turtles
        n = len(agents)
        seg_stat = sum(t.segregation_ratio() for t in agents) / n
        self.history.append(seg_stat)

        
class SchellingAgent(turtle.Turtle):
    """A SchellingAgent moves if there
    aren't enough nearby agents like himself.
    """
    def __init__(self, **kw):
        turtle.Turtle.__init__(self, **kw)
        color = random.choice(['red','black'])
        self.tags = set()
        self.tags.add(color)
        self.color(color)
        self.penup()
        width, height = self.canvas_size()
        x = random.randint(-width//2, width//2)
        y = random.randint(-height//2, height//2)
        self.goto(x,y)
        self.setheading(random.randint(0,360))
        self.onclick(self.show_neighbors)

    def forward(self, distance=1, constrain=True):
        """Return None. Move agent by amount
        `distance` using current heading,
        but stay on the canvas."""
        my_heading = self.heading()
        if constrain:
            while not self.on_canvas():
                self.setheading(self.towards(0,0))
                turtle.Turtle.forward(self, 1)
        self.setheading(my_heading)
        turtle.Turtle.forward(self, distance)
        if constrain:
            while not self.on_canvas():
                self.back(1)
    
    fd = forward

    def canvas_size(self):
        """Return tuple, canvas width and height."""
        width = self.screen.window_width()
        height = self.screen.window_height()
        return width, height

    def on_canvas(self):
        """Return bool; True if turtle on canvas.
        """
        x, y = self.position()
        width, height = self.canvas_size()
        if (abs(x) >= width//2 or abs(y) >= height//2):
            return False
        return True

    def constrained_position(self):
        x, y = self.position()
        width, height = self.canvas_size()
        if abs(x) >= width//2:
            x = math.copysign(width//2, x)
        if abs(y) > height//2:
            y = math.copysign(height//2, y)
        return x, y

    def step(self):
        if not self.is_content():
            self.setheading(random.randint(0,360))
            self.fd(5)

    def is_content(self, threshold=0.33):
        """Return bool, True if content.
        Find the `k` closest neighbors.
        Determine the fraction of these that are the same "kind".
        This is called the segregation_ratio.
        If segregation_ratio>threshold, the agent is content.
        Schelling threshold: "each wants something
        more than one-third of his neighbors to be like himself" (p.148).
        """
        ratio = self.segregation_ratio()
        is_content = True if (ratio > threshold) else False
        return is_content

    def segregation_ratio(self):
        nbrs = self.neighbors()
        n_alike = sum(self.is_like(other) for other in nbrs)
        ratio = float(n_alike) / len(nbrs)
        return ratio
        
    def neighbors(self):
        """Return list, the neighbors.
        Schelling had 8 neighbors (Moore neighborhood on a grid).
        """
        return self.nearest(8)

    def nearest(self, k):
        """Return list, the k nearest neighbors."""
        agents = self.screen._turtles
        others = (t for t in agents if t is not self)
        sortkey = self.distance
        nearest = sorted(others, key=sortkey)[:k]
        return nearest

    def add_tag(self, s):
        self.tags.add(s)

    def remove_tag(self, s):
        self.tags.remove(s)

    def is_like(self, other):
        return bool(self.tags & other.tags)

    def show_neighbors(self, x=0, y=0):
        mycolor = self.color()
        self.fillcolor('green')
        x1, y1 = self.position()
        nbrs = self.neighbors()
        """
        #assume neighbors sorted by distance
        radius = self.distance(nbrs[-1])
        self.right(90)
        self.fd(radius, constrain=False)
        self.left(90)
        self.pendown()
        self.circle(radius)
        self.pu()
        self.goto(x1,y1)
        """
        nbr_colors = dict()
        for nbr in nbrs:
            nbr_colors[nbr] = nbr.color()
            nbr.pencolor('green')
        time.sleep(2)
        self.clear()
        #restore colors
        self.color(*mycolor)
        for nbr in nbrs:
            nbr.color(*nbr_colors[nbr])


if __name__ == "__main__":
    world = SchellingWorld()
    world.run()
    print(world.history)
    turtle.mainloop()


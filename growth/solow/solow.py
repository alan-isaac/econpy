"""
Solow Growth Model
==================

[solow-1956-qje] presents a simple but influential model of economic growth.
Here is a three equation summary of the model:

.. math::

	Y_t = F(K_t, N_t, t)
	K_{t+1} = K_t + I_t
	I_t = s Y_t

Here is a simple summary of the model:

.. math::

	K_{t+1} = K_t + s F(K_t, N_t, t)

This is a first order difference equation in `K`.
Given an initial value of `K` and the evolution of `N`,
we can determine the time path of `K` (and of `Y`).
The resulting series can be compared with actual data.

Some stylized facts explained by the model [solow-1970]:

- real output per worker hour shows roughly constant growth
- the capital/output ratio is roughly constant
- capital's share of income is roughly constant
- output per worker and the real wage grow at roughly the same rate

[solow-1957-restat] used the model to suggest a decomposition of
output growth into its sources.
He attributed around four-fifths of the growth in output per worker
to technological change.

[prescott-1988-scanje] adopts this accounting perspective to note a key business cycle fact:
at business cycle frequencies, fluctuations in output are attributable to fluctuations in labor input.
[kydland.prescott-1982-e] suggest this suggest an important role for the time allocation
between market and non-market activities.
Another inconvenient fact is that variations in `N` are due mostly to changes in the number of people employed.
[hansen-1985] adds a nonconvex relationship between labor hours and productivity to adapt the neoclassical model to the puzzle.

A natural question: what determines the saving rate `s`.
One answer: [cass-1965] derived `s` from an infinite horizon optimization problem.

Brock, W. A. & Mirman, L. J.: Optimal economic growth under uncertainty: The discounted
case. Journal of Economic Theory 4, 479-513, 1972.
Cass, D.: Optimum growth in an aggregate model of capital accumulation. Review of
Economic Studies 32, 233-240, 1965.
Christiano, L. J.: Is consumption insufficiently sensitive to innovations in income? American
Economic Review 77 (A.E.A. Papers and Proceedings), 337-341, 1987.
Grossman, S. J. & Shiller, R. J.: The determinants of the variability of stock market prices.
American Economic Review 71, 222-227, 1981.
Hansen, G. D.: Indivisible labor and the business cycle. Journal of Monetary Economics 16,
309-327,1985.
Judd, K. L.: The welfare cost of factor taxation in a perfect-foresight model. Journal of Political
Economy 95, 675-709, 1987.
Kydland, F. E. & Prescott, E. C.: Time to build and aggregate fluctuations. Econometrica 50,
1345-1370,1982.



This module presents a simple simulation of a growth model
based on [solow-1956-qje].
We can easily use this simulation to illustrates the effects
on the growth path and the long run outcomes of changes in the

- saving rate
- population growth rate
- technological progress
- depreciation rate

Solow proves that the economy converges to a balanced growth rate.
Simulation offers visual and numerical illustrations of both comparative static and convergence results.

Balanced Growth Path
--------------------

Balanced growth occurs when capital (K) grows at the same rate of the effective  labor supply (AN).
(This is the labor supply adjusted for the level productivity.)
Solow shows that an economy will converge to a steady state,
which follows a balanced growth path.

Constants
~~~~~~~~~

gN
	the labor force growth rate
gA
	labor productivity growth
s
	saving rate
d
	capital depreciation rate
`\alpha`
	elasticity of output (`Y`) with respect to capital (`K`)

We will initially assume the following values.

.. code::

	gN=0.015; gA=0.01; s=0.25; d=0.05; alpha=0.3; A=1.0

Predetermined Variables
~~~~~~~~~~~~~~~~~~~~~~~

AN
K

We will assume the following initial values:

.. code::

	N = 10; K = 2; A = 1

Contemporaneously Determined Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once we know `N`, `K`, and `A`,
we can determine the following:

Y
	production
S
	real saving
I
	real investment

Causal View
~~~~~~~~~~~

AN, K -> Y -> S -> \delta K




Summing the labor force growth rate and the labor productivity growth,
we find the effective labor supply grows at rate (gn + gA).

.. math::

	AN(t) = (1 + gN + gA) * AN(t-1)

Production is consumed or saved as capital,
which is put into production the following period.
(There are no Keynesian worries about the equality of desired investment and saving.)

.. math::

	I(t) = s * Y(t)

Net investment (`\Delta K`) is thus gross investment (`I`) less depreciation (`d * K`).

Balanced Growth
---------------

Balanced growth requires the same growth rate for the capital stock and for effective labor,
in which case

.. math::

	K(t) = (1 + gN + gA) * K(t-1)

This in turn requires gross investment of

.. math::

	I(bgp) = (gN + gA + d) K(bgp)

or equivalently

.. math::


	s * Y(bgp) = (gN + gA + d) * K(bgp)

Note that along a balanced growth path, `K/Y` is constant:

.. math::

	K(bgp)/Y(bgp) = s / (gN + gA + d)

	Y = K^\alpha  (AN)^{1-\alpha}

	K(bgp) = s Y(bgp) / (gN + gA + d)

	K(bgp) = s K^\alpha  (AN)^{1-\alpha} / (gN + gA + d)

	K^{1-\alpha} = s (AN)^{1-\alpha} / (gN + gA + d)

	K = [s (AN)^{1-\alpha} / (gN + gA + d)]^{1/(1-\alpha)}


Production
----------

The aggregate production function is given a standard Cobb-Douglas representation:
output depends on a technology parameter (`A`), capital (`K`), and effective labor (`AN`).
There is also a key production parameter, `\alpha < 1`.

	Y = K^\alpha  (AN)^{1-\alpha}

GDP Over Time
-------------

Given initial values of `N`, `K`, and `A`,
we can simulate the evolution of GDP over time.
If we wish to display this graphically,
a ratio scale is a good choice.

Simulation
==========

We can use a programming languate to simulate a numerical example of the Solow growth model.
To illustrate Solow's convergence result,
we will produce both the balanced growth path and an actual GDP path.

To begin the simulation, we need initial values for `N` and `K`.
From then on, both grow as discussed above.
Each period, Y is determined by K and N,
and S is determined by Y.

For the balanced growth path, we use the same initial `N` but we compute the implied initial level of `K`
(so as to be on the BGP).

Figure 1:  Solow Model: Convergence to the BGP after a Saving Shock

Figure 1 depicts an economy that is initially on its balanced growth path.
Since Y grows exponentially, we want to plot it against a ratio scale.
With no shocks, the economy will stay on the balanced growth path.
Along the BGP, we find that K/AN and Y/AN remain at their steady state values.

However we shock the economy in period 5 with a fall in the saving rate `s`.
This affect the BGP immediately:
the balanced growth path shifts down, but along it `Y` grows at the same rate.
Of course the actual capital stock adjusts slowly to its long run level,
and correspondingly the growth of actual GDP slows.
Both variables converge back to their long run path.
This convergence illustrates part of Solow's proof of the stability of the balanced growth path.
 
What has simulation added to the analytical results?

- students must understand the Solow model in order to simulate it
- students can test their intuition for analytical problems by comparing to simulated results
- results that are relatively hard to determine analytically, such as speed of convergence, are easy to simulate (do it!)
- we can look at the simulated path for plausible values of the constants and even for initial values of N and K
- the simulation model allows variety of applications and modifications (see the Malthusian version)

.. [solow-1956-qje]
   Solow, Robert M. (1956):
   "A Contribution to the Theory of Economic Growth." Quarterly Journal of Economics, 70:65-94.
"""
from __future__ import division
import sys
sys.path.insert(0,'../../')  #assumes econpy install
from itertools import izip
from random import random as health_shock
from econpy.pytrix.utilities import permutations, calc_gini
gN=0.015; gA=0.01; s=0.025; d=0.05; alpha=0.3; A=1.0
N0 = 100
AN = A * N0
#choose K to start on balanced growth path
K0 = ((s*(AN)**(1-alpha)) / (gN + gA + d))**(1/(1-alpha))
K = K0
def f(K, AN): return K**(alpha) * AN**(1-alpha)
Y = f(K, AN)
KNY = list()
for _ in range(10):
	Y_1 = Y
	Y = f(K, AN)
	KNY.append((K,AN,Y))
	print Y, (Y-Y_1)/Y_1
	AN *= 1 + gN + gA
	K += s * Y - d * K
for item in KNY:
	print "K: %5.2f,  AN: %5.2f,  Y: %5.2f"%item
#add plot for BGP and decline in `s`

# switch to object-oriented treatment
# objects:
#	representative consumer (owns factors)
#	representative firm (just a blueprint)

class SolowConsumer:
	def __init__(self, k, n, s=0.2, health=1):  #change the saving rate default!
		self.k = k
		self.n = n
		self.s = s
		self.health = health
	def get_kn(self):
		#labor supply is n unless health below threshold
		shock = health_shock()
		self.health = (0.8*self.health + 0.2) * 2 * shock
		#self.health =  health_shock()
		#print "health: ", self.health,
		#return self.k, self.n * (self.health > health_threshold)
		return self.k, self.n * shock**4 * (self.health > health_threshold)
	def receive(self, amt):
		# this is the consumption and saving decision
		# for a simple Solow consumer
		self.k += self.s * amt
	def adjust_kn(self, d, g):
		self.k *= 1 - d
		if self.health > health_threshold:
			self.n *= 1+g
class CompositeSolowConsumer:
	def __init__(self, k, n):
		self.k = k
		self.n = n
		print type(n)
		kpc = k/n
		#start with equal capital shares and one unit of labor
		# later we will use consumers as keys
		self.consumers = list(SolowConsumer(k=kpc, n=1) for _ in range(n))
	def get_kn(self):
		kn = [c.get_kn() for c in self.consumers]
		self.kn = kn
		k, n = [sum(f) for f in izip(*kn)] 
		self.k, self.n = k,n
		return k, n
	def receive(self, amt, pmt_type=''):
		# this is the consumption and saving decision
		# for a simple Solow consumer
		consumers = self.consumers
		#get aggregate factor supplies
		if pmt_type == 'rents':
			r = amt/self.k
			# note that self.kn holds that actual factor supplies
			for c, ck in izip(self.consumers, (kn[0] for kn in self.kn)):
				c.receive(r*ck)
		elif pmt_type == 'wages':
			w = amt/self.n
			for c, cn in izip(self.consumers, (kn[1] for kn in self.kn)):
				c.receive(w*cn)
		else:
			raise ValueError("unknown payment type")
	def adjust_kn(self, d, g):
		for consumer in self.consumers:
			consumer.adjust_kn(d, g)
	def get_unemployment(self):
		kn = self.kn
		return sum(f[1]==0 for f in kn)/len(kn)
	
print

# health_threshold currently global! not good!
health_threshold = 1.0
health_threshold = 0.1
consumer = CompositeSolowConsumer(K0, N0)
for _ in range(1000):
	K, N = consumer.get_kn()
	Y = f(K, N)
	#print "K: %5.2f,  AN: %5.2f,  Y: %5.2f"%(K,N,Y)
	#print consumer.kn
	if not _%50:
		print "unemployment: ", consumer.get_unemployment(), "inequality: ", calc_gini(c.k for c in consumer.consumers)
		#print [(c.health < health_threshold) for c in consumer.consumers]
	#TODO: d and g and alpha are currently global: not good!
	consumer.adjust_kn(d, gN+gA)  #timing crucial! (fix that?)
	consumer.receive(alpha*Y, 'rents')
	print
	consumer.receive((1-alpha)*Y, 'wages')
	print



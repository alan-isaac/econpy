""" DETERMINISTIC CAKE EATING MODEL
**  Follows Chapter 2 of Adda and Cooper (See Section 2.4.1, Page 16)
**  This code modifies detcake.m (as provided by the book authors 22 Dec 03)
**  to improve efficiency and avoid propagating missing values.


:contact: aisaac AT american DOT edu
:since:   29 Dec 2003

Comments:
Some simplifying tricks are used:
i.  Following Adda & Cooper (and many others) restrict possible
    consumption levels so that K(t+1) = K(t)-c is in the
    discrete domain of the numerical value function,
    thereby avoiding interpolation.
ii. Note that the value function iterates as
	V[K(t),iter+1] = max_ik2 {ln(K(t)-K(t+1))+beta*V[K(t+1),iter]}
    where K takes a discrete set of values
	[Kmin,Kmin+inc,Kmin+2inc,...,Kmax].
    Problem: suppose K(t) = Kmin.  Then K(t+1) = Kmin and c(t) = 0.
    (This includes the case where Kmin = 0.)
    Adda and Cooper set the value to missing (-inf wd work the same).
    Problem: consider K(t) = Kmin+inc.  Then K(t+1) = Kmin and c(t) = inc.
    (This includes the case where Kmin = 0.)  But if V(Kmin) = missing,
    missing values will propogate to V(Kmin+inc) upon iteration,
    and these in turn will propogate.
    So: we extrapolate V(Kmin) instead of setting it to missing.
    Problem: gives a silly answer at the boundary when Kmin = 0.
	     We can live with this.
"""
import numpy as np
from matplotlib import pyplot as plt

dimIter = 40     # number of iterations
dimK = 101
K = np.arange(dimK)     # grid over cake size (starts at 0; see notes above)
# Note: grid over consumption is the same
# Note: graph appearance depends on grid!

#Define payoff:
# any continuous, strictly increasing, strictly concave function shd be ok
def u(x): return np.log(x)     #single period payoff
beta = 0.9     # discount factor

"""
V stores the value function iterations.
Rows are cake sizes, columns the iteration.
Only initialization of the first column matters (iteration 0)"""
V = np.zeros( (dimK, dimIter+1) )
#note:                 ^

#tempind stores best index (of K) after each iteration
tempind = np.zeros( (dimK,) ) * np.nan
#doe dimIter iterations
for iter in range(dimIter):
	temp = np.zeros( (dimK,) ) * np.nan     #stores values during iteration
	for ik in range(dimK-1):    #loop over initial (endowment) cake sizes
		ik += 1
		#max u over next period cake sizes (which imply c)
		c = K[ik]-K[:ik]    #positive possible consumption values
		Vk = u(c)+beta*V[:ik,iter] #current payoff plus value of remaining cake
		#store best value this iteration (ik, iteration over K)
		temp[ik] = np.nanmax(Vk)
		if iter == dimIter-1:    #on last iter, save index of best size
			tempind[ik] = np.argmax(Vk)
	V[:,iter+1] = temp     # optimizing over size of next period cake
	#Next: a crude extrapolation just to avoid propogating missing values from V(0):
	V[0,iter+1] = 2*V[1,iter+1]-V[2,iter+1]

# computing the optimal consumption as a function of initial cake size
tempind[np.isnan(tempind)] = 1
Ind = tempind.astype(np.int)
optK = K[Ind]+temp*0     #Note: Ind[r] = 1 when cakesize r is all missing values
optC = K-optK

# ** Plotting the value function after each iterations **
fig1 = plt.figure(1)
fig1ax = fig1.gca()
fig1ax.set_xlabel("Size of Cake")
fig1ax.set_ylabel("Value Function")
fig1ax.plot(K,V[:,1:])

# ** Plotting the optimal consumption levels **
fig2 = plt.figure(2)
fig2ax = fig2.gca()
fig2ax.set_xlabel("Size of Cake")
fig2ax.set_ylabel("Optimal Consumption (vs. 45 degree line)")
fig2ax.plot(K,optC)
fig2ax.plot(K,K)

plt.show()



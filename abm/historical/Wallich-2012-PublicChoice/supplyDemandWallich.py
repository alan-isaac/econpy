"""
This model of supply and demand in a single market
is based on the Appendix of Wallich-2012-PublicChoice
(A model of supply and demand, in Python)
Refactored by Alan G. Isaac in 2021.

Example usage:
    python supplyDemand.py

:needed: Python 3.6+, numpy, matplotlib
"""

import itertools
from typing import NamedTuple
import numpy as np
from matplotlib import pyplot as plt

#class for model parameters, with defaults
class Parameters(NamedTuple):
    buyerType: 'HomogeneousBuyer'
    sellerType: 'Seller'
    nBuyers: int = 1000 #number of buyers
    nSellers: int = 50  #number of sellers
    nPeriods: int = 200 #number of periods
    nReps: int = 10     #number of replicates
    # Qs = a + bP
    a: float = 100.0
    b: float = 10.0
    # Qd = c - dP
    c: float = 20.0
    d: float = 7.0
    # demand shock (effectively changes c) 
    tShock: float = nPeriods // 4 #date of shock
    demand_shock: float = -3.0

# homogeneous buyers 
class HomogeneousBuyer(object): 
    # initialize the buyer
    def __init__(self, mkt=None):
        self.mkt = mkt
        self.shift: float = 0.0
        self.c: float = mkt.prms.c
        self.d: float = mkt.prms.d
    def quantity(self, price) -> float:
        """Quantity demanded is a function of price
        (where `shift` represents a demand shock).
        """
        return max(self.shift + self.c - self.d * price, 0) 
    # receive a demand shock
    def shock(self, shock):
        self.shift += shock


class Seller(object):
    def __init__(self, mkt):
        self.mkt = mkt
        self.inventory: float = 0.0 #initialize inventory
        self.sales: float = 0.0     #initialize sales
        self.prevsales: float = 0.0
        self.a: float = mkt.prms.a
        self.b: float = mkt.prms.b

    def quantity(self, price: float) -> float:
        # offer quantity is a function of price
        return max(self.a + self.b * price, 0.0)

    def set_nextPrice(self):
        return NotImplemented

    def price(self) -> float:
        return self.nextprice 

    # produce goods
    def produce(self):
        self.set_nextPrice()
        quantity = self.quantity(self.nextprice)
        if self.inventory < quantity:
            self.inventory += (quantity - self.inventory) 
        (self.prevsales, self.sales) = (self.sales, 0)

    def sell(self, quantity):
        # sell goods from inventory
        qty: float = min(quantity, self.inventory)
        self.inventory -= qty
        self.sales += qty 

# price-taking seller 
class WalrasianSeller(Seller): 
    """A WalrasianSeller always offers the clearing price.
    """
    def set_nextPrice(self):
        self.nextprice = self.mkt.pXA

class LearningSeller(Seller):
    """Provides Wallich-type a learning seller.
    """
    # offer the Walrasian price initially and then use history
    def set_nextPrice(self):
        if self.sales > 0 and self.prevsales > 0:
            padjust: float = (self.sales - self.prevsales) / self.prevsales
            self.nextprice *= (1.0 + padjust)
        elif self.sales == 0 and self.prevsales > 0:
            self.nextprice *= 0.5
        else:
            self.nextprice = self.mkt.pXA

#this computation was in Wallich's Auctioneer class
def auctioneerPriceW(buyers, sellers): 
    price: float = 0.0       #initialize price 
    increment: float = 100.0 #initialize price adjustment
    supply = sum(seller.quantity(price) for seller in sellers)
    demand = sum(buyer.quantity(price) for buyer in buyers)
    positive = (supply < demand) # whether the equilibrium price is positive
    # discover the equilibrium price
    while abs(supply - demand) > 0.0000001:
        if supply < demand:
            price += increment
            if not positive: increment /= 2
        else:
            price -= increment
            if positive: increment /= 2
        #update supply and demand at new price
        supply = sum(seller.quantity(price) for seller in sellers)
        demand = sum(buyer.quantity(price) for buyer in buyers) 
    return price 
 
 
def auctioneerPriceAlt(buyers, sellers): 
    """An alternative (faster) function for computing
    the Walrasian equilibrium price.
    solve a + b P == shift + c - d P for P.
    """
    buyerInfo = ((buyer.shift, buyer.c, buyer.d) for buyer in buyers)
    (sumshift, sumc, sumd) = (sum(xs) for xs in zip(*buyerInfo))
    sellerInfo = ((seller.a, seller.b) for seller in sellers)
    (suma, sumb) = (sum(xs) for xs in zip(*sellerInfo))
    return (sumshift + sumc - suma) / (sumb + sumd)

# for speed use auctioneerPriceAlt; for replication use auctioneerPriceW
auctioneerPrice = auctioneerPriceAlt

class Market(object):
    def __init__(self, prms):
        self.prms = prms
        self.setup(prms)
    def setup(self, prms):
        self.results = list() #initialize results list
        buyerType = prms.buyerType
        nBuyers = prms.nBuyers
        self.buyers = buyers = \
            tuple(buyerType(mkt=self) for b in range(nBuyers))
        sellerType = prms.sellerType
        nSellers = prms.nSellers
        self.sellers = sellers = \
            tuple(sellerType(mkt=self) for s in range(nSellers))
        self.pXA = pWalras = auctioneerPrice(buyers, sellers)
        self.tShock = prms.tShock
        self.setupComplete = True
        self.runComplete = False
    def shockDemand(self, period):
        if period == self.tShock: # introduce a demand shock
            for buyer in self.buyers:
                buyer.shock(self.prms.demand_shock) 
    def runsim(self): #replace Wallich's `model` procedure
        prms = self.prms
        # create the buyers and sellers
        buyers = self.buyers
        sellers = self.sellers
        # for each period...
        for period in range(prms.nPeriods) : 
            self.shockDemand(period) #mutates buyers
            #determine Walrasian equilibrium price
            self.pXA = pWalras = auctioneerPrice(buyers, sellers)
            # engage in production
            for s in sellers:
                s.produce()
            # initialize running totals
            units: float = 0.0
            sales: float = 0.0
            # for each buyer...
            for buyer in buyers: #ai: first mover advantage?
                # identify the seller offering the best deal
                quantity = 0
                for s in sellers:
                    if min(buyer.quantity(s.price()), s.inventory) > quantity:
                        quantity = min(buyer.quantity(s.price()), s.inventory)
                        seller = s 
                # buy from this seller
                if (quantity > 0):
                    seller.sell(quantity)
                    units += quantity
                    sales += quantity * seller.price( ) 

            inventory = sum(s.inventory for s in sellers)  #end-of-period inventory
            self.results.append((period, units, sales, inventory)) #one period's results
        self.runComplete = True

# utility to create and run model and return results
def getResults(prms):
    mkt = Market(prms)
    mkt.runsim()
    return mkt.results


# run a model multiple times
# (but note the current model is deterministic)
def runReplicates(prms) : 
    # execute the model multiple times
    nReps = prms.nReps
    allresults = [getResults(prms) for i in range(nReps)] 
    # initialize totals
    nPeriods = prms.nPeriods
    units = [0 for p in range(nPeriods) ]
    sales = [0 for p in range(nPeriods) ]
    inventory = [0 for p in range(nPeriods) ] 
    # calculate totals
    for r in allresults:
        for (p, u, s, i) in r :
            units[p] += u
            sales[p] += s
            inventory[p] += i 
    # calculate averages
    for p in range(nPeriods) :
        units[p] /= nReps
        sales[p] /= nReps
        inventory[p] /= nReps 
    return (units, sales, inventory)

def writeFile(fpath, units, sales, inventory):
    file = open(fpath, "w", encoding="utf-8") 
    header = "Period, Volume, AvgPrice, Inventory\n"
    file. write(header) 
    # write results, period by period
    for (p, (u,s,i)) in enumerate(zip(units, sales, inventory)):
        file.write(f"{p:d}, {u:f}, {s:f}, {i:f}\n")
    file.close()
 

if __name__ == "__main__":
    if True:  #one replicate, with plotting
        #use either WalrasianSeller or LearningSeller as sellerType
        prms = Parameters(buyerType=HomogeneousBuyer,sellerType=WalrasianSeller)
        results = getResults(prms)
        fig, (ax1,ax2,ax3) = plt.subplots(3,1)
        ts, qs, pqs, invs = zip(*results)
        ax1.plot(ts, np.array(pqs)/np.array(qs))
        ax2.plot(ts, qs)
        ax3.plot(ts, invs)
        plt.show()
    if False: #### True -> run the models, with replicates
        classical = runReplicates(Parameters(buyerType=HomogeneousBuyer,sellerType=WalrasianSeller))
        writeFile("D:/temp/temp01.csv", *classical)
        learning = runReplicates(Parameters(buyerType=HomogeneousBuyer,sellerType=LearningSeller)) 
        writeFile("D:/temp/temp02.csv", *learning)


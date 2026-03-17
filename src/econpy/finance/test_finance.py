'''
Test functions for numpy.lib.financial

All are taken from the OpenDocument Open Formula project

http://www.oasis-open.org/committees/documents.php
'''

import numpy.lib.financial as finance
import numpy as np
from numpy.testing import *
import finance as f

### Additional tests for existing functions

class TestFinancial(TestCase):

    def test_rate(self):
#        +- .001
#        assert_almost_equal(np.rate(12,-100,1000),0.0292285,3)
#       needs 4 values default should assume fv = 0
        assert_almost_equal(np.rate(12,-100,1000,100),0.01623133, 3)
    
    def test_rate(self):
        assert_almost_equal(np.rate(12,-100,1000,100,1), 0.01996455, 3)

    def test_rate(self):    
        assert_almost_equal(np.rate(12,-100,1000,100,1,.01), 0.01996455, 3)
#        assert_almost_equal(np.rate(0,-100,1000),) This should raise an error
        # High Precision test +- .00000000001

    def test_rate(self):
        assert_almost_equal(np.rate(48,-50,2000,0,1,0),0.0080529819239056, 16)

    def test_rate(self):
        assert_almost_equal(np.rate(48,-50,2000,50,0,0),0.0080529819239056, 16)

    def test_rate(self):
        # Note Gnumeric truncates Nper is it is not an integer
        # OO Does not truncate and uses the fractional part in the calculation
        # OO behavior
        assert_almost_equal(np.rate(12.9,-100,1000, 0),.0388, 4)

    def test_rate(self):
        # Gnumeric behavior
        assert_almost_equal(np.rate(12.9,-100,1000, 0),.0292, 4)

# rate notes
# Excel allows fractional values of PayType
# It appears to be an offset to the end date of the payment period
# towards the start date of the period

    def test_irr(self):
       I =  [-29, 20, 30]
       assert_almost_equal(np.irr(I), 0.418787000165341, 5)

    def test_pv(self):
        assert_almost_equal(np.pv(.10,12,-100,100), 649.51, 2)

    def test_fv(self):
        assert_almost_equal(np.fv(.10,12,-100,100),1824.59, 2)

    def test_pmt(self):
        assert_almost_equal(np.pmt(.05,12,1000),-112.82541, 3)

    def test_pmt(self):
        assert_almost_equal(np.pmt(.05,12,1000,100),-119.10795, 3)

    def test_pmt(self):
        assert_almost_equal(np.pmt(.05,12,1000,100,1), -113.43614, 3)

    def test_pmt(self):
        assert_almost_equal(np.pmt(0,10,1000),-100)

    def test_nper(self):
        assert_almost_equal(np.nper(.05,-100,1000),14.2067, 3)

    def test_nper(self):
        assert_almost_equal(np.nper(.05,-100,1000,100),15.2067, 3)
    
    def test_nper(self):
        assert_almost_equal(np.nper(.05,-100,1000,100,1),14.2067, 3)

    def test_nper(self):
        assert_almost_equal(np.nper(0,-100,1000),10)

    def test_nper(self):
        assert_almost_equal(np.nper(-.01,-100,1000),9.483283066, 3)

    def test_npv(self):
#        assert_almost_equal(np.npv(1.00,4,5,7), 4.125, 3)
#       cannot take values like this
        assert_almost_equal(np.npv(1.00,[4,5,7]), 4.125, 3)
#        assert_almost_equal(np.npv(.1,100,200), 256.198347107438, 3)
#       cannot take values like this

    def test_mirr(self):
        assert_almost_equal(np.mirr((100, 200,-50, 300,-200), .05, .06), 
                            0.342823387842, 8)

### EconPy Functions
    def test_ipmt(self):
        assert_almost_equal(f.ipmt(.05/12,10,360,100000),-412.0850243, 4)

#    def test_ipmt(self):
    # Gnumeric and KSpread result
    # Note: kspread seems to have deprecated the beginning of period option
    # Check Gnumeric on Gnome at school
#        assert_almost_equal(f.ipmt(.05/12,10,360,100000,0,1), -412.1699604, 4)
#   This value is wrong.  It is equivalent to finding the payments
#   of m=pmt(.05/12,10,360,100000,0,1) and using this beginning of period
#   value to calculate -(.05/12)*(100000)*(1+.05/12)**9 - m*((1+.05/12)**9-1)

    def test_impt(self):
    # Excel and OO results
        assert_almost_equal(f.ipmt(.05/12,10,360,100000,0,1), -410.38, 2)
#   This is correct and is based on the value of
#   -(.05/12)*(100000+m)*(1+.05/12)**9 - m*((1+/05/12)**9-1)

    def test_ppmt(self):
        assert_almost_equal(f.ppmt(.03,1,12,100), -7.046208547, 4)

    def test_ppmt(self):
        assert_almost_equal(f.ppmt(.03,1,12,100,200), -21.138625642, 4)

    def test_ppmt(self):
        assert_almost_equal(f.ppmt(.03,1,12,100,200,1), -23.435558876, 4)

    def test_ppmt(self):
        assert_almost_equal(f.ppmt(.08,5,24,10000,0), -203.773514049, 4)

    def test_ppmt(self):
        assert_almost_equal(f.ppmt(.08,10,24,100000,20), -359.292174601, 4)

    def test_ppmt(self):
        assert_almost_equal(f.ppmt(.08,10,24,10000,2000,1), -332.677939445, 4)


if __name__=="__main__":
    run_module_suite()



        

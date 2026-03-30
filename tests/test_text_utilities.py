'''
Unit tests for econpy.utilities.text.

'''

import unittest
import random

from tests_config import econpy  #tests_config.py modifies sys.path to find econpy
from econpy.utilities.table import SimpleTable

mydata = [[11,12],[21,22]]
myheaders = "Column 1", "Column 2"
mystubs = "Row 1", "Row 2"
txt_result='''
         Title         
=======================
      Column 1 Column 2
-----------------------
Row 1    11       12   
Row 2    21       22   
-----------------------
'''
"""
tbl = text.SimpleTable(mydata, myheaders, mystubs, title="Title")
print( tbl )
print( tbl.as_html() )
# set column specific data formatting
tbl = text.SimpleTable(mydata, myheaders, mystubs,
	fmt={'data_fmt':["%3.2f","%d"]})
print( tbl.as_csv() )
with open('c:/temp/temp.tex','w') as fh:
	fh.write( tbl.as_latex_tabular() )
"""

class testUtilities(unittest.TestCase):
	def setUp(self):
		pass
	def test_simple_table_text(self):
		tbl = SimpleTable(mydata, myheaders, mystubs, title="Title")
		self.assertEqual(str(tbl), txt_result[1:],
		msg=f"Problem:\n{str(tbl)}\nis not identical to\n{txt_result[1:]}")

if __name__=="__main__":
	unittest.main()




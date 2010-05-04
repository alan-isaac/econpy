'''
Unit tests table.py.

:see: http://docs.python.org/lib/minimal-example.html for an intro to unittest
:see: http://agiletesting.blogspot.com/2005/01/python-unit-testing-part-1-unittest.html
:see: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/305292
'''
from __future__ import absolute_import
import unittest

__docformat__ = "restructuredtext en"

from table import Cell, Row, SimpleTable
from table import default_latex_fmt

ltx_fmt1 = default_latex_fmt.copy()

txt_fmt1 = dict(
	data_fmts = ['%3.2f', '%d'],
	data_fmt = "%s",  #deprecated; use data_fmts
	empty_cell = ' ',
	colwidths = 1,
	colsep=' * ',
	row_pre = '* ',
	row_post = ' *',
	table_dec_above='*',
	table_dec_below='*',
	header_dec_below='*',
	header_fmt = '%s',
	stub_fmt = '%s',
	title_align='r',
	header_align = 'r',
	data_aligns = "r",
	stubs_align = "l",
	fmt = 'txt'
)		
cell0data = 0.0000
cell1data = 1
row0data = [cell0data, cell1data]
row1data = [2, 3.333]
table1data = [ row0data, row1data ]
test1stubs = ('stub1', 'stub2')
test1header = ('header1', 'header2')
tbl = SimpleTable(table1data, test1header, test1stubs, txt_fmt=txt_fmt1, ltx_fmt=ltx_fmt1)

class test_Cell(unittest.TestCase):
	def test_celldata(self):
		celldata = cell0data, cell1data, row1data[0], row1data[1]
		cells = [Cell(datum, datatype=i%2) for i, datum in enumerate(celldata)]
		for cell, datum in zip(cells, celldata):
			self.assertEqual(cell.data, datum)

class test_SimpleTable(unittest.TestCase):
	def test_txt_fmt1(self):
		"""Limited test of custom txt_fmt"""
		desired = """
*****************************
*       * header1 * header2 *
*****************************
* stub1 *    0.00 *       1 *
* stub2 *    2.00 *       3 *
*****************************
"""
		actual = '\n%s\n' % tbl.as_text()
		#print(actual)
		#print(desired)
		self.assertEqual(actual, desired)
	def test_ltx_fmt1(self):
		"""Limited test of custom ltx_fmt"""
		desired = r"""
\begin{tabular}{lcc}
\toprule
               & \textbf{header1} & \textbf{header2}  \\
\midrule
\textbf{stub1} &       0.0        &        1          \\
\textbf{stub2} &        2         &      3.333        \\
\bottomrule
\end{tabular}
"""
		actual = '\n%s\n' % tbl.as_latex_tabular()
		#print(actual)
		#print(desired)
		self.assertEqual(actual, desired)

if __name__=="__main__":
	unittest.main()


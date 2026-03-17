"""Tests of binary floating point simulation

Author: Robert Clewley, August 2008.
"""

import numpy as npy
import math
import decimal
from decimal import Decimal
from copy import copy, deepcopy

from binary import *

def display(bf, linefeed=False):
    """Pretty printer for binary float representations
    """
    if linefeed:
        print "Binary:", bf, "\n  Decimal:", bf.as_decimal()
    else:
        print "Binary:", bf, "  Decimal:", bf.as_decimal()

# Invalid literals
invalid = ["Binary('-0.111e-4.')", "Binary('-.11-e-5')", "Binary('.11.')",
           "Binary('e-4')", "Binary('1e.4')", "Binary('0.111a3')",
           "Binary('')", "Binary('.')", "Binary('-')", "Binary('-.')",
           "Binary('0-')", "Binary(' 1')"]
for lit in invalid:
    try:
        eval(lit)
    except ValueError:
        pass
    else:
        print lit
        raise "Invalid literal was accepted!"

valid = ["Binary('1.', double)", "Binary('.1')", "Binary()", "Binary('0')",
         "Binary('-0')", "Binary('-1.e-1')", "Binary('001.110011')",
         "Binary('11e01')"]

for lit in valid:
    eval(lit)

zero_double = double(0)
smallest_denormalized_double = zero_double.next()
assert abs(smallest_denormalized_double.as_decimal() - Decimal("4.94e-324")) \
       < Decimal("1e-327")
assert smallest_denormalized_double.as_decimal().adjusted() == -324
smallest_normalized_double = double(double.largest_denorm).next()
assert abs(smallest_normalized_double.as_decimal() - Decimal("2.23e-308")) \
       < Decimal("1e-310")
assert smallest_normalized_double.as_decimal().adjusted() == - 308

assert double(npy.float64(1.3)) == double(Decimal("1.3"))
assert double(npy.float64(1.3e30)) == double(Decimal("1.3e30"))
assert double(npy.float64(1.3e-30)) ==  double(Decimal("1.3e-30"))
assert double(npy.float64(1.3e-305)) ==  double(Decimal("1.3e-305"))

i = npy.finfo(npy.double)

assert i.eps == float(double(i.eps).dec_value)

one = double(1)
next_one = one.next()

eps_double = next_one - one
assert float(eps_double.as_decimal()) == i.eps

z = single(0)
z1 = z.next()
z1m = z.prev()
z2 = z1.next()
z3 = z2.next()
print "Smallest representable non-negative value in IEEE single precision"
display(z1, 1)
print "Smallest representable non-positive value in IEEE single precision"
display(z1m, 1)
assert z1m == -z1 == -abs(z1m)

print "This x is precisely representable as a native IEEE double precision "
print "  64-bit float: 25.56640625"
x_native = 25.56640625
assert float(double(x_native).as_decimal()) == x_native
x_bf = double(x_native)
assert --x_bf == x_bf
assert -abs(-x_bf)*double(-1) == x_bf
x_bf_next = x_bf.next()
x_bf_prev = x_bf.prev()
print "Initial value x:"
display(x_bf, 1)
print "Next representable value to x:"
display(x_bf_next, 1)
print "Previous presentable value to x:"
display(x_bf_prev, 1)
assert x_bf < x_bf_next
assert x_bf > x_bf_prev
assert float((x_bf ** double(2)).as_decimal()) == x_native**2
assert float(x_bf.sqrt().as_decimal()) == math.sqrt(x_native)


# Coercion
q = quadruple(Decimal("3.00005235236e350"))
print "\nQuadruple precision value closest to 3.00005235236e350:"
display(q, 1)
q_converted_double = Binary(q, double)
print "\nCoerced quadruple value to double precision representation:"
print "Internal binary overflow renders Inf result"
assert q_converted_double.as_decimal() == Decimal("Inf")
display(q_converted_double, 1)


# copying
assert copy(x_bf) == x_bf
assert deepcopy(x_bf) == x_bf


print "\n\nShowing all values in a 6-bit (1,2,2) representation:"
con_1_2_2 = define_context(2, 2)
s = con_1_2_2('01111')
while True:
    display(s)
    try:
        s=s.prev()
    except ValueError, e:
        print e
        break
print "\nGoing back the other way... (note the -0 instead of 0)"
while True:
    display(s)
    try:
        s=s.next()
    except ValueError, e:
        print e
        break

print "\nTesting denormalized number representations..."
tiny_double = double('0' + '0'*10 + '1' + '0'*52)
assert i.tiny == float(tiny_double.as_decimal())
tiny2_double = double(str(tiny_double))
assert tiny2_double == tiny_double
tiny_double_prev = tiny_double.prev()
assert tiny_double_prev.is_denormalized()
assert tiny_double_prev == double('0' + '0'*11 + '1'*52)

try:
    assert npy.isinf(float(double(1.2e600).as_decimal()))
except ValueError:
    print "If this is python 2.5, cannot create float instances from string"
    print "  literals 'infinity', 'nan', etc."
    pass

print "\n\nInf in IEEE 754 single precision mode:"
single_inf = single(' '.join(['0', '1'*8, '0'*23]))
display(single_inf, 1)

try:
    print single_inf > tiny_double
except ValueError, e:
    print "\nsingle_inf > tiny_double ??"
    print " Exception raised:", e, "(cannot compare floats of different" \
               " precisions)"
else:
    raise "Comparison failed!"

print "\n\nComparing representations of 1/10 ..."
n01_dec = Decimal("0.1")
n01_double = double(0.1)
x = n01_double.as_decimal()
print "in IEEE 754 double:", x, "\n rounding error =", x - n01_dec
n01_single = single(0.1)
x = n01_single.as_decimal()
print "in IEEE 754 single:", x, "\n rounding error =", x - n01_dec
bf = define_context(8, 8)
n01_bf = bf(0.1)
x = n01_bf.as_decimal()
print "in a (1,8,8) representation:", x, "\n rounding error =", x - n01_dec

b1 = Binary('-.000011010110', double)
b2 = Binary('-0.011', double)
b_sum = double(b1.as_decimal()+b2.as_decimal())
b_sum2 = b1 + b2
assert b_sum == b_sum2
assert b_sum2 == b_sum    # not the same __eq__ method called!
print "\n\nb1 =",
display(b1, 1)
print "b2 =",
display(b2, 1)
print "b1 + b2 =",
display(b_sum, 1)

# mixed type arithmetic involving Binary objects
b1_dec = b1.as_decimal()
b1_double = double(b1_dec)
b1_re = eval(repr(b1_double))
assert b1_re.context == b1_double.context

b_sum3 = b1_dec + b2
assert b_sum3 == b_sum
b_sum4 = b1_double + b2
assert b_sum4 == b_sum
b_sum5 = b2 + b1_dec
assert b_sum4 == b_sum
b_sum6 = b2 + b1_double
assert b_sum6 == b_sum
try:
    b_sum7 = b2 + float(b1_dec)
except TypeError:
    # invalid comparison
    pass
else:
    raise "Invalid comparison succeeded!"

# complicated checks to make sure everything cross-references OK
assert b1 == Binary(double(b1_dec))
assert b1 == Binary(b1.as_binary())
assert b1 == Binary(b1)
assert b1 == b1_re
assert b1_double.as_binary() == b1
# mismatched precision, but Binary values can be compared (just not added, etc.)
assert b1 == Binary(b1, single)

b1_fromrepr = eval(repr(b1))
assert b1.as_decimal() == Decimal("-0.05224609375")
assert b1_fromrepr == b1
print "\n\nb1 in binary fraction form =", b1.as_binary()
print "6th digit of b1's representation's significand is ", \
      b1.rep.significand[6-1]


print "\n\nRounding mode tests on a (1,2,2) context"
r_half_up = define_context(2, 2, rounding=ROUND_HALF_UP)
r_up = define_context(2, 2, rounding=ROUND_UP)
r_down = define_context(2, 2, rounding=ROUND_DOWN)
r_half_down = define_context(2, 2, rounding=ROUND_HALF_DOWN)
r_ceiling = define_context(2, 2, rounding=ROUND_CEILING)
r_floor = define_context(2, 2, rounding=ROUND_FLOOR)

expected_results = {
   r_half_up: {
    '0.0100': '0.01',
    '0.0101': '0.01',
    '0.0110': '0.1',
    '0.0010': '0.01',
    '0.0011': '0.01',
    '-0.0100': '-0.01',
    '-0.0101': '-0.01',
    '-0.0110': '-0.1',
    '-0.0010': '-0.01',
    '-0.0011': '-0.01'},
   r_up: {
    '0.0100': '0.01',
    '0.0101': '0.1',
    '0.0110': '0.1',
    '0.0010': '0.01',
    '0.0011': '0.01',
    '-0.0100': '-0.01',
    '-0.0101': '-0.1',
    '-0.0110': '-0.1',
    '-0.0010': '-0.01',
    '-0.0011': '-0.01'},
   r_down: {
    '0.0100': '0.01',
    '0.0101': '0.01',
    '0.0110': '0.01',
    '0.0010': '0.0',
    '0.0011': '0.0',
    '-0.0100': '-0.01',
    '-0.0101': '-0.01',
    '-0.0110': '-0.01',
    '-0.0010': '-0.0',
    '-0.0011': '-0.0'},
   r_half_down: {
    '0.0100': '0.01',
    '0.0101': '0.01',
    '0.0110': '0.01',
    '0.0010': '0.0',
    '0.0011': '0.01',
    '-0.0100': '-0.01',
    '-0.0101': '-0.01',
    '-0.0110': '-0.01',
    '-0.0010': '-0.0',
    '-0.0011': '-0.01'},
   r_ceiling: {
    '0.0100': '0.01',
    '0.0101': '0.1',
    '0.0110': '0.1',
    '0.0010': '0.01',
    '0.0011': '0.01',
    '-0.0100': '-0.01',
    '-0.0101': '-0.01',
    '-0.0110': '-0.01',
    '-0.0010': '-0.0',
    '-0.0011': '-0.0'},
   r_floor: {
    '0.0100': '0.01',
    '0.0101': '0.01',
    '0.0110': '0.01',
    '0.0010': '0.0',
    '0.0011': '0.0',
    '-0.0100': '-0.01',
    '-0.0101': '-0.1',
    '-0.0110': '-0.1',
    '-0.0010': '-0.01',
    '-0.0011': '-0.01'}
   }

for con in (r_half_up, r_up, r_down, r_half_down, r_ceiling, r_floor):
    print "\nTesting rounding mode %s:" % con.round_mode.lower()
    expected = expected_results[con]
    for in_val, out_val in expected.items():
        rb = Binary(in_val, con)
        print " Value ", in_val, "->", out_val
        assert rb == Binary(out_val)

try:
    r32 = r_half_up(1.6) + r_down(1.6)
except ValueError:
    # mismatched rounding modes despite same precision
    pass
else:
    raise "Mismatched rounding modes added OK!"

print "\n\nUp-conversion test:"
rb = Binary('0.01', r_ceiling)
qrb = quadruple(rb)
qrb2 = Binary(rb, quadruple)
display(qrb, 1)
assert qrb == qrb2
print "\nConverted (2,2,CEILING) representation of 0.01b to quadruple precision:"
print repr(rb), "->", repr(qrb)

xs = Binary('-1111.001', single)
xd1 = Binary(xs, double)
xd2 = Binary(double(xs))
assert xd1 == xd2
assert xd1/xd2 == double(1)

bd = Binary(double(1.5))
bq = Binary(quadruple(0.1))
c = bd + bq
assert c - bd == bq
assert (c * bd)/bd == c

assert x_bf == x_bf.max(x_bf_prev)
assert rb == rb.min(rb-b1)

assert eval(repr(double(npy.inf))) == double(npy.inf)

"""
Simulation of binary floating point representation at arbitrary fixed or
infinite precision (including greater than 64 bit).

:name: Simfloat
:author: Robert Clewley
:version: 0.1
:contact: rob <dot> clewley <at> gmail <dot> com
:date: August 2008
:license: New BSD


***** Features

* Primarily intended for teaching purposes, e.g. in a numerical analysis course.
  Demonstrates representation formats and facilitates exploration of the
  distribution of represented values along the real number line.

* Not intended to be the most efficient implementation, but transparency of
  implementation helpful for learning about issues in IEEE representation, e.g.
  denormalized numbers.

* Open source code, released under the BSD license. Please improve this code
  for clarity, bug-fixes and feature improvements, but only to improve
  efficiency where it is not at the expense of a reader's easy comprehension of
  the algorithms and binary representation.

* Can represent any (sign, characteristic, significand) IEEE 754-style format,
  and is not restricted to representations with total precision less than 64
  bits. The internal representations and arithmetic are done using arbitrary
  precision and do not depend on the python 'float' (64 bit) class.

* Rounding modes offered are 'up', 'down', 'floor', 'ceiling', 'half_up',
  and 'half_down'.

* Arithmetic operations are only permitted between numbers represented in
  exactly the same format.

* A binary integer class is also implemented with its associated integer
  arithmetic and shift operations (no logical operations).

* max, min, sqrt, power functions are defined for the appropriate numeric
  classes.


See the following for details, and references therein:
http://en.wikipedia.org/wiki/Floating_point
http://en.wikipedia.org/wiki/Rounding
http://en.wikipedia.org/wiki/IEEE_754
http://en.wikipedia.org/wiki/Binary_numeral_system



***** Known issues

* Binary floating point arithmetic not simulated in its native form, but through
  internal use of arbitrary precision Decimal floating point numbers. It would
  be preferable to have a pure binary arithmetic implementation that
  demonstrates shifting of exponents, etc. before addition.

* Does not directly simulate the algorithmic implementations by which
  IEEE 754 arithmetic and rounding is performed in CPUs. e.g. rounding up
  is *not* achieved by adding 0.5 and then truncating in this code.

* Creation of higher precision floats is slow due to python implementation of
  frexp function.

* Boolean operations on binary floating point numbers are not supported at this
  time.

* Please note that float(Decimal("Inf")) will not work in Python 2.5 due to a
  problem in Python itself. This has been fixed in Python 2.6 and above
  (http://bugs.python.org/issue3188).

* ContextClass does not support initialization from numpy float128 values. Needs
  additional code to extract byte-by-byte hex representation from the 'data'
  attribute of such a value, and conversion into equivalent binary string.

* eval(repr(x)) when x is a ContextClass instance creates a Binary object with
  the same representation (fixed precision, rounding) as x, not another
  ContextClass instance. However, x == eval(repr(x)).

* decimal context precision value must not be changed by the user to be less
  than the precision required by any ContextClass instances (Binary numbers of a
  fixed precision), otherwise arithmetic on those numbers may be inaccurate.
  In Python 2.5 and above, local context could be established for these
  calculations using the with statement (see here for implementation details:
  http://docs.python.org/lib/decimal-decimal.html). See binary_py25.py.

* mod, floordiv, divmod methods are not supported.

* Can be slow to evaluate expressions involving high precision values.

* Can hash a binary context (ContextClass instance), but cannot hash
  a decimal.context instance.

* Requires numpy to be installed, in order to use numpy.sign, numpy.zeros
  and provide compatibility with numpy.float32, numpy.float64, and
  numpy.float128 values. The sign function and array use provide better speed
  in key parts of the algorithms, but could be easily replaced to make
  numpy installation optional.

* Does not support use of minifloats (IEEE-754 style formats with very low
  bit lengths for the exponent and characteristic) for integer-only
  representations. (This is a common application of such values, according to
  http://en.wikipedia.org/wiki/Minifloat.)



***** Usage

** Constructors:

>>> context = define_context(5, 12, ROUND_DOWN)


Equivalent binary float values in a given context:

>>> x = Binary('-0.1111', context)          # binary fraction assumed by default

>>> x = Binary(Decimal("-0.9375"), context) # decimal fraction

The following represent the same binary number (in context) but are a way
to directly specify the representation in terms of the underlying context

>>> a = context('1 01110 111000000000')   # (sign, characteristic, significand)

>>> a = context('101110111000000000')     # (sign, characteristic, significand)

These alternative forms are also valid, for convenience:

>>> a = context(Decimal("-0.9375"))

>>> a = context(Binary('-0.1111'))

If the python float literal -0.9375 is exactly representable in the context,
then this is also equivalent:

>>> a = context(-0.9375)

>>> a = context(numpy.float64(-0.9375))

Otherwise, the resulting representation in a will be to the "nearest"
representable value under the rules of the context's precision and rounding
mode.

The values in a are instances of the context, and are not Binary class
instances.

Note that a context instance cannot be initialized directly using a string
literal for a binary fraction, to avoid ambiguity with the primary use
case, namely with input strings for (sign, characteristic, significand).


The Binary constructor can also represent *arbitrary* precision binary values in
the absence of a given context. After any of the above definitions of x:

>>> x.context
<class 'binary.Float_5_12_D'>

However:

>>> y = Binary('0.110100101010101011110001111100001e5')

>>> y.context is None
True

Note that infinite binary precision is not possible to specify from a
Decimal object, in case the binary representation is non-terminating.

>>> b = Binary(Decimal("0.1"))
ValueError: Cannot create arbitrary precision binary value without a
   representation context



** Views:

For a context instance x (not a Binary instance), we slightly break the
tradition that eval(repr(x)) is identically the same type as x. However,
eval(repr(x)) == x and the evaluation leads to a Binary object with the same
context.

>>> x = context(Decimal("-0.9375"))

>>> x                 # default 'view' is as binary
Binary("-0.1111E0", (5, 12, ROUND_DOWN))

>>> bx = eval(repr(x))
>>> bx == x
True

>>> bx.context
<class 'binary.Float_5_12_D'>

>>> bx.context == x.context   # bx really quacks like a duck
True

>>> x.as_binary()     # output always in scientific notation with 0 before radix
Binary("-0.1111E0")

>>> x.as_binary() == bx  # x.as_binary() keeps the same context
True

>>> x.as_decimal()
Decimal("-0.9375")

>>> print x
1 01110 111000000000



** Comparisons:

Can only compare like representations from a given context.

>>> d = double(1)
>>> q = quadruple(1)
>>> d == q
ValueError: Mismatched precision

If you want to compare the actual values that these objects represent, convert
them to a Binary number first

>>> bd = Binary(double(1))
>>> bq = Binary(quadruple(1))
>>> bd == bq
True

>>> bd == 1.0   # cannot compare with python-native floats
TypeError: Invalid object for comparison

>>> bd > 1
False

>>> bd == Decimal("1")
True



** Conversions:

For high precision floats with long mantissas, convert them accurately to
Decimal type. Note that Decimal(str(f)) will not be accurate for floats f
with mantissas longer than the displayable length of f by the str function.
Thus float(Decimal(str(f))) != f for some f. To avoid this, create the
representation of the float in the appropriate context by

double(f)

which will be a precise representation of f in double precision, where f
can be a python float, numpy.float64. For numpy.float32 use single(f).

Binary values in one context can be converted (coerced) to another thus:

>>> xs = Binary('-1111.001', single)
>>> xd = Binary(xs, double)

or

>>> xd = Binary(double(xs))

** Arithmetic:

Can only perform arithmetic on representations from a given context with
other instances of the same context (including Binary instances with
identical context).

To perform arbitray precision arithmetic with mixed representations,
first convert to Binary type, which does not care about the precision of
the operands: the operation returns a new Binary value of the precise
result, without context if neither operand had context, otherwise with
the highest precision context. In a tie, arithmetic is not possible unless
the rounding is the same.

>>> bd = Binary(double(1.5))
>>> bq = Binary(quadruple(0.1))
>>> c = bd + bq
>>> print c
0.11001100110011001100110011001100110011001100110011001101E1

>>> c.__class__
<class 'binary.Binary'>

>>> c.context   # coerced to the higher precision
<class 'binary.Float_15_112_HU'>


Also see test_simfloat.py for many more examples and validations.

"""

import numpy as npy
import math
import decimal
from decimal import Decimal

__all__ = ['Decimal', 'Binary', 'ContextClass', 'BinaryIntClass',
           'quadruple', 'double', 'define_context', 'frexp', 'dec_context',
           'single', 'half', 'test', 'binstr2dec', 'decfrac2binrep',
           'decint2binstr', 'binfracstr2decfrac', 'dec2binstr', 'binvalstr2dec',
           'ROUND_UP', 'ROUND_DOWN', 'ROUND_CEILING', 'ROUND_FLOOR',
           'ROUND_HALF_UP', 'ROUND_HALF_DOWN',
           'BinaryOverflow', 'BinaryUnderflow', 'BinaryOverflow',
           'BinaryNegativeValue', 'BinaryRemainderValue', 'BinaryException']

# Rounding
# up = always away from 0
ROUND_UP = 'ROUND_UP'
# down = always towards 0 (truncate)
ROUND_DOWN = 'ROUND_DOWN'
# ceiling = always towards +inf
ROUND_CEILING = 'ROUND_CEILING'
# floor = always towards -inf
ROUND_FLOOR = 'ROUND_FLOOR'
# half up = to nearest, 0.1b (0.5d) rounds away from 0 (standard and default)
ROUND_HALF_UP = 'ROUND_HALF_UP'
# half down = to nearest, 0.1 (0.5d) rounds towards 0
ROUND_HALF_DOWN = 'ROUND_HALF_DOWN'

_round_code = {ROUND_UP: 'U', ROUND_DOWN: 'D', ROUND_CEILING: 'C',
               ROUND_FLOOR: 'F', ROUND_HALF_UP: 'HU', ROUND_HALF_DOWN: 'HD'}

dec_context = decimal.getcontext()
dec_context.prec = 128


class BinaryIntClass(object):
    """Abstract class for non-negative binary integer values only, with a fixed
    number of digits given by class attribute 'digits'. Set digits in a concrete
    subclass. The initialization value string will cause an exception if the
    binary value is longer than the class' digits setting.
    """
    digits = None

    def __init__(self, value):
        """Initialize with a value made up of a string of binary digits.
        """
        dec_value = int(value, base=2)
        if dec_value < 0:
            raise BinaryNegativeValue("Invalid binary value: out of range of %d-digit number"%self.digits)
        elif dec_value > self.largest:
            raise BinaryOverflow("Invalid binary value: out of range of %d-digit number"%self.digits)
        self.bin_value = pad(value, self.digits)
        self.dec_value = Decimal(dec_value)
        self.tuple_rep = tuple([int(bit) for bit in self.bin_value])

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.bin_value)

    def __str__(self):
        return self.bin_value

    def as_decimal(self):
        return self.dec_value

    def as_binary(self):
        return 'Binary("%s")' % self.bin_value

    def as_tuple(self):
        return self.tuple_rep

    def _op_return_class(self, other):
        try:
            other_digits = other.digits
        except AttributeError:
            raise TypeError("Invalid Binary object")
        if other_digits > self.digits:
            new_class = other.__class__
        else:
            new_class = self.__class__
        return new_class

    def max(self, other):
        return self.dec_value.max(other)

    def min(self, other):
        return self.dec_value.min(other)

    def __add__(self, other):
        new_class = self._op_return_class(other)
        result = self.dec_value + other.dec_value
        try:
            return new_class(decint2binstr(result))
        except ValueError:
            raise BinaryOverflow(result)

    def __sub__(self, other):
        new_class = self._op_return_class(other)
        result = self.dec_value - other.dec_value
        if result < 0:
            raise BinaryNegativeValue(result)
        return new_class(decint2binstr(result))

    def __mul__(self, other):
        new_class = self._op_return_class(other)
        result = self.dec_value * other.dec_value
        try:
            return new_class(decint2binstr(result))
        except ValueError:
            raise BinaryOverflow(result)

    def __div__(self, other):
        new_class = self._op_return_class(other)
        result_dm = divmod(self.dec_value, other.dec_value)
        if result_dm[1] != 0:
            raise BinaryRemainderValue(result_dm)
        return new_class(decint2binstr(result_dm[0]))

    def __rshift__(self, y):
        result = self.dec_value >> y
        return self.__class__(decint2binstr(result))

    def __lshift__(self, y):
        result = self.dec_value << y
        try:
            return self.__class__(decint2binstr(result))
        except ValueError:
            raise BinaryOverflow(result)

    def __hash__(self):
        """Hash as per the precise decimal representation.
        """
        return hash(self.dec_value)

    def next(self):
        try:
            return self.__class__(decint2binstr(int(self.bin_value,
                                                base=2) + 1))
        except BinaryOverflow:
            raise BinaryOverflow(int(self.bin_value, base=2) + 1)

    def prev(self):
        try:
            return self.__class__(decint2binstr(int(self.bin_value,
                                                    base=2) - 1))
        except:
            raise BinaryNegativeValue(int(self.bin_value, base=2) - 1)

    def __hash__(self):
        return hash(repr(self))

    def __getitem__(self, i):
        return int(self.bin_value[i])

    ## could provide boolean operator methods but not needed for arithmetic

    def __reduce__(self):
        return (self.__class__, (repr(self),))

class SignBit(BinaryIntClass):
    digits = 1
    largest = 1



class BinaryCharacteristic(BinaryIntClass):
    """Abstract class for floating point representation's characteristic,
    a.k.a. exponent.
    """
    def __init__(self, value):
        """value is a binary string representatino of the exponent (so may be
        negative)"""
        BinaryIntClass.__init__(self, value)
        # interpretation-related attributes
        interp_dec_value = self.dec_value - self.bias
        if interp_dec_value < self.exp_lowest:
            raise BinaryNegativeValue("Invalid binary value: out of range of %d-digit number"%self.digits)
        if interp_dec_value > self.exp_largest:
            raise BinaryOverflow("Invalid binary value: out of range of %d-digit number"%self.digits)
        self.interp_dec_value = interp_dec_value

    def interpret(self, denorm=False):
        """Interpret raw binary value as a signed decimal integer.
        """
        if denorm:
            # bias needs to be adjusted by 1
            return self.interp_dec_value + 1
        else:
            return self.interp_dec_value


class BinarySignificand(BinaryIntClass):
    """Abstract class for floating point representation's significand,
    a.k.a. fraction, or mantissa.
    """
    def interpret(self):
        """Interpret raw binary value as a decimal fraction.
        """
        return binfracstr2decfrac(self.bin_value)


class ContextClass(object):
    """Abstract class for immutable binary floating point number using
    (sign, characteristic, significand) representation.
    """
    def __init__(self, value):
        """Initialize with decimal value (either of type 'float' or 'Decimal')
        or a binary digit string of total length = <this_class>.digits or the
        same string with spaces between sign, characteristic, and significand
        elements (total length <this_class>.digits+2).
        """
        try:
            assert self.significandClass.digits is not None
        except AssertionError:
            raise NotImplementedError("Create concrete sub-type of ContextClass")

        # round_dir may be overwritten by init_from_dec
        # round_dir =  None  => no rounding needed
        #             'next' => use next towards +inf
        #             'prev' => use next towards -inf
        round_dir = None

        if isinstance(value, (float, npy.float64)):
            if not npy.isfinite(value):
                val_str = str(value)
                # val_str may be '1.#INF' rather than 'inf' on some platforms
                val_str = val_str.replace('.', '').replace('#', '').replace('1',
                                                                            '')
                round_dir = self.init_from_dec(Decimal(val_str))
            else:
                if value < 0:
                    fval = -value
                    s = '1'
                else:
                    fval = value
                    s = '0'
                # extract full binary representation of the value
                # (which is not accessible from str(value) or repr(value)
                valstr = pad(decint2binstr(npy.int64( \
                                npy.array(fval).view(long))), 64)
                e = valstr[1:12]
                f = valstr[12:]
                denorm = int(e) == 0 and int(f) > 0
                if denorm:
                    bias = 1022
                    expo = Decimal(2)**Decimal(int(e, base=2) - bias)
                    frac = binfracstr2decfrac(f)
                else:
                    bias = 1023
                    expo = Decimal(2)**Decimal(int(e, base=2) - bias)
                    frac = 1 + binfracstr2decfrac(f)
                try:
                    round_dir = self.init_from_dec((-1)**int(s) * expo * frac)
                except:
                    raise BinaryOverflow("Invalid representation for this class: %s"%value)

        elif isinstance(value, npy.float32):
            if not npy.isfinite(value):
                val_str = str(value)
                # val_str may be '1.#INF' rather than 'inf' on some platforms
                val_str = val_str.replace('.', '').replace('#', '').replace('1',
                                                                            '')
                round_dir = self.init_from_dec(Decimal(val_str))
            else:
                if value < 0:
                    fval = -value
                    s = '1'
                else:
                    fval = value
                    s = '0'
                # extract full binary representation of the value
                # (which is not accessible from str(value) or repr(value)
                valstr = pad(decint2binstr(npy.int32( \
                              npy.array(fval).view(int))), 32)
                e = valstr[1:9]
                f = valstr[9:]

                denorm = int(e) == 0 and int(f) > 0
                if denorm:
                    bias = 126
                    expo = Decimal(2) ** Decimal(int(e, base=2) - bias)
                    frac = binfracstr2decfrac(f)
                else:
                    bias = 127
                    expo = Decimal(2) ** Decimal(int(e, base=2) - bias)
                    frac = 1 + binfracstr2decfrac(f)
                try:
                    round_dir = self.init_from_dec((-1)**int(s) * expo * frac)
                except:
                    raise BinaryOverflow("Invalid representation for this class: %s"%value)


        elif isinstance(value, (int, long, npy.int64, npy.int32)):
            try:
                round_dir = self.init_from_dec(Decimal(value))
            except OverflowError:
                raise BinaryOverflow()

        elif isinstance(value, Decimal):
            try:
                round_dir = self.init_from_dec(value)
            except OverflowError:
                raise BinaryOverflow()

        elif isinstance(value, Binary):
            try:
                round_dir = self.init_from_dec(value.dec)
            except OverflowError:
                raise BinaryOverflow()


        elif isinstance(value, str):
            if len(value) == self.digits:
                # e.g. "11101001111010000"
                s = value[0]
                e = value[1:self.characteristicClass.digits+1]
                f = value[self.characteristicClass.digits+1:]
            elif len(value) == self.digits + 2:
                # e.g. "1 1101 001111010000"
                try:
                    s, e, f = value.split(' ')
                except:
                    raise ValueError("Invalid string representation for this class: %s"%value)
            else:
                raise ValueError("Invalid string representation for this class: %s"%value)
            try:
                self.init_from_string(s, e, f)
            except:
                raise ValueError("Invalid string representation for this class: %s"%value)

        else:
            raise TypeError("Invalid initialization type")

        self.tuple_rep = tuple((self.signbit.as_tuple(),
                                self.characteristic.as_tuple(),
                                self.significand.as_tuple()))

        # treat special cases for 0, Inf, NaN, and denormalized values
        if self.characteristic.dec_value == 0:
            if self.significand.dec_value == 0:
                # zeros
                if self.signbit.dec_value == 0:
                    self.dec_value = Decimal("0")
                    self.bin_value = "0"
                else:
                    self.dec_value = Decimal("-0")
                    self.bin_value = "-0"
            else:
                # denormalized values
                self.dec_value = (-1)**self.signbit.dec_value * \
                      2**(self.characteristic.interpret(denorm=True)) * \
                     (0 + self.significand.interpret())
                # lazy determination of bin_value when it is requested
                # (slow calculation)
                self.bin_value = ""
        elif self.characteristic.dec_value == self.characteristic.largest:
            if self.significand.dec_value == 0:
                # +/- Inf
                if self.signbit.dec_value == 0:
                    self.dec_value = Decimal("Inf")
                    self.bin_value = "Inf"
                else:
                    self.dec_value = Decimal("-Inf")
                    self.bin_value = "-Inf"
            else:
                # NaN
                self.dec_value = Decimal("NaN")
                self.bin_value = "NaN"
        else:
            # normalized values
            self.dec_value = (-1)**self.signbit.dec_value * \
                        2**(self.characteristic.interpret()) * \
                        (1 + self.significand.interpret())
            # lazy determination of bin_value when it is requested
            # (slow calculation)
            self.bin_value = ""

        if round_dir is not None:
            new = getattr(self, round_dir)()
            self.signbit = new.signbit
            self.characteristic = new.characteristic
            self.significand = new.significand
            self.bin_value = new.bin_value
            self.dec_value = new.dec_value
            self.tuple_rep = new.tuple_rep

        # for compatibility with Binary attribute
        self.context = self.__class__


    def init_from_string(self, s, char_str, mant_str):
        self.signbit = SignBit(s)
        self.characteristic = self.characteristicClass(char_str)
        self.significand = self.significandClass(mant_str)


    def init_from_dec(self, d):
        """d is a Decimal object"""
        if d._isnan():
            self.signbit = SignBit('0')
            self.characteristic = \
                self.characteristicClass("1"*self.characteristicClass.digits)
            self.significand = \
                self.significandClass("1"*self.significandClass.digits)
            return None
        elif d._isinfinity() != 0:
            self.signbit = SignBit(str(bin_sign(d._isinfinity())))
            self.characteristic = \
                self.characteristicClass("1"*self.characteristicClass.digits)
            self.significand = \
                self.significandClass("0"*self.significandClass.digits)
            return None
        if d < 0:
            s = '1'
            d = -d
        elif d == 0:
            self.signbit = SignBit('0')
            self.characteristic = \
                self.characteristicClass("0"*self.characteristicClass.digits)
            self.significand = \
                self.significandClass("0"*self.significandClass.digits)
            # no rounding, so return None
            return None
        else:
            s = '0'
        if d <= self.largest_denorm:
            bias = self.characteristicClass.bias-1
            frac_leading = 0
        else:
            bias = self.characteristicClass.bias
            frac_leading = 1

        # acquire precise fraction, exponent (given that exponent must be
        # representable in this class)
        f_dec, e_dec = frexp(d, self)
        e_dec += bias

        # convert to binary and round to precision of significand
        i = 0
        max_bits = self.characteristicClass.exp_largest + \
                   self.significandClass.digits + 2
        bfrac = npy.zeros(max_bits, int)
        i_stop = max_bits
        not_seen_one = True
        # make sure we use extra precision (given that might adjust for
        # leading 0's)
        while f_dec > 0 and i < max_bits:
            f_dec *= 2
            bit = int(f_dec)
            if not_seen_one and bit == 1:
                # first time seen a 1 know that we only need up to
                # significand's more digits + 2 (speed optimization)
                i_stop = i + self.significandClass.digits + 2
                not_seen_one = False
            bfrac[i] = bit
            f_dec -= bit
            i += 1
            if i >= i_stop:
                break
        # binary string representation of fraction to full precision
        f = ''.join([str(b) for b in bfrac[:i]])
        if frac_leading == 1:
            try:
                one_pos = f.index('1')
            except ValueError:
                # f is all 0's
                pass
            else:
                # adjust for leading zeros
                f = f[one_pos+1:]
                e_dec -= one_pos+1
            c = decint2binstr(e_dec)
        else:
            # denormalized, inevitable lost precision in f
            c = '0'*self.characteristicClass.digits
            f = '0'*abs(e_dec) + f
        #print len(f), f
        #print 2**Decimal(e_dec - bias) * (frac_leading + binfracstr2decfrac(f))

        round_dir = None   # default
        if len(c) < self.characteristicClass.digits:
            c = pad(c, self.characteristicClass.digits)
        if len(f) < self.significandClass.digits:
            f = pad(f, self.significandClass.digits, to_right=True)
        elif len(f) > self.significandClass.digits:
            next_bit = int(f[self.significandClass.digits])
            try:
                remaining_bits = f[self.significandClass.digits+1:]
            except IndexError:
                remaining_bits = '0'
            else:
                if remaining_bits == '':
                    remaining_bits = '0'
            round_dir = self._round(int(s), next_bit, int(remaining_bits) > 0)
            f = f[:self.significandClass.digits]

        self.signbit = SignBit(s)
        self.characteristic = self.characteristicClass(c)
        self.significand = self.significandClass(f)
        return round_dir

    def _round(self, sign, next_bit, non_zero_remainder):
        r = self.round_mode
        if r == ROUND_DOWN:
            return None
        elif r == ROUND_UP:
            if next_bit == 1 or non_zero_remainder:
                # > 0.0b in magnitude
                if sign == 0:
                    return 'next'
                else:
                    return 'prev'
            else:
                return None
        elif r == ROUND_HALF_UP:
            if next_bit == 1:
                # >= 0.1b in magnitude, round away from 0
                if sign == 0:
                    return 'next'
                else:
                    return 'prev'
            else:
                return None
        elif r == ROUND_HALF_DOWN:
            if next_bit == 1:
                if non_zero_remainder:
                    # > 0.1b in magnitude, round away from 0
                    if sign == 0:
                        return 'next'
                    else:
                        return 'prev'
                else:
                    # = 0.1b, round towards 0
                    return None
            else:
                return None
        elif r == ROUND_CEILING:
            if sign == 0:
                if next_bit == 1 or non_zero_remainder:
                    # > 0.0b in magnitude, round towards +inf
                    return 'next'
                else:
                    return None
            else:
                return None
        elif r == ROUND_FLOOR:
            if sign == 1:
                if next_bit == 1 or non_zero_remainder:
                    # > 0.0b in magnitude, round towards +inf
                    return 'prev'
                else:
                    return None
            else:
                return None
        else:
            raise ValueError("Invalid rounding type")

    def is_denormalized(self):
        return self.dec_value <= self.largest_denorm

    def as_tuple(self):
        return self.tuple_rep

    def as_binary(self):
        """Lazy evaluation of bin_value in case it's never used.
        This is done because the calculation is slow!
        """
        if self.bin_value == "":
            self.bin_value = dec2binstr(self.dec_value, self)
        return Binary(self.bin_value, self.__class__)

    def as_decimal(self):
        return self.dec_value

    def __repr__(self):
        if self.bin_value == "":
            self.bin_value = dec2binstr(self.dec_value, self)
        return 'Binary("%s", (%s, %s, %s))' % \
                         (self.bin_value,
                          self.characteristicClass.digits,
                          self.significandClass.digits,
                          self.round_mode)

    def __str__(self):
        return "%s %s %s" % (str(self.signbit), str(self.characteristic),
                             str(self.significand))

    def next(self):
        """Return the successive representable float value in the more
        positive direction.
        """
        if self.signbit.dec_value == 1:
            method = 'prev'
        else:
            method = 'next'
        return self._step(method)

    def prev(self):
        """Return the successive representable float value in the more
        negative direction.
        """
        if self.signbit.dec_value == 0:
            method = 'prev'
        else:
            method = 'next'
        return self._step(method)

    def _step(self, method):
        """
        Internal method for stepping to successive representable values,
        either in the increasing or decreasing direction, according to the
        method passed.
        """
        # default value, unless switches
        new_signbit = self.signbit
        try:
            new_signif = getattr(self.significand, method)()
        except BinaryNegativeValue:
            # CARRY
            try:
                new_char = getattr(self.characteristic, method)()
            except BinaryNegativeValue:
                # CHANGE SIGN
                new_char = self.characteristic
                new_signbit = SignBit(str(1-self.signbit.dec_value))
                # have to reset new_signif in this case
                new_signif = self.significandClass(pad('1',
                                                       self.significand.digits))
            except BinaryOverflow:
                raise ValueError("No more representable values")
            else:
                new_signif = self.significandClass('1'*self.significand.digits)
        except BinaryOverflow:
            # CARRY
            # representation of one in the same number of significant digits
            new_signif = self.significandClass('0'*self.significand.digits)
            try:
                new_char = getattr(self.characteristic, method)()
            except BinaryOverflow:
                raise ValueError("No more representable values")
        else:
            new_char = self.characteristic
        return self.__class__(" ".join([str(new_signbit), str(new_char),
                                       str(new_signif)]))

    def _op_check(self, other):
        try:
            # may be another ContextClass with matching precision
            other_sig_digits = other.significand.digits
            other_char_digits = other.characteristic.digits
        except AttributeError:
            # may be a Binary object with matching precision
            try:
                other_sig_digits = other.context.significandClass.digits
                other_char_digits = other.context.characteristicClass.digits
            except AttributeError:
                raise TypeError("Invalid Context object")
            else:
                ox = other.dec
                c = other.context
        else:
            ox = other.dec_value
            c = other
        if other_sig_digits != self.significand.digits or \
           other_char_digits != self.characteristic.digits:
            raise ValueError("Mismatched precision")
        elif c.round_mode != self.round_mode:
            raise ValueError("Mismatched rounding modes")
        return ox

    def __eq__(self, other):
        ox = self._op_check(other)
        return self.dec_value == ox

    def __ne__(self, other):
        ox = self._op_check(other)
        return self.dec_value != ox

    def __le__(self, other):
        ox = self._op_check(other)
        return self.dec_value <= ox

    def __lt__(self, other):
        ox = self._op_check(other)
        return self.dec_value < ox

    def __ge__(self, other):
        ox = self._op_check(other)
        return self.dec_value >= ox

    def __gt__(self, other):
        ox = self._op_check(other)
        return self.dec_value > ox

    def __neg__(self):
        return self.__class__(str(1-self.signbit.dec_value) + str(self)[1:])

    def __abs__(self):
        return self.__class__('0' + str(self)[1:])

    def __add__(self, other):
        ox = self._op_check(other)
        return self.__class__(self.dec_value + ox)

    __radd__ = __add__

    def __sub__(self, other):
        ox = self._op_check(other)
        return self.__class__(self.dec_value - ox)

    def __rsub__(self, other):
        ox = self._op_check(other)
        return self.__class__(ox - self.dec_value)

    def __mul__(self, other):
        ox = self._op_check(other)
        return self.__class__(self.dec_value * ox)

    __rmul__ = __mul__

    def __div__(self, other):
        ox = self._op_check(other)
        return self.__class__(self.dec_value / ox)

    def __rdiv__(self, other):
        ox = self._op_check(other)
        return self.__class__(ox / self.dec_value)

    __rtruediv__ = __rdiv__

    def __pow__(self, other):
        ox = self._op_check(other)
        return self.__class__(self.dec_value ** ox)

    def __rpow__(self, other):
        ox = self._op_check(other)
        return self.__class__(ox ** self.dec_value)

    def sqrt(self):
        return self.__class__(self.dec_value.sqrt())

    def __nonzero__(self):
        return self.dec_value != 0

    def max(self, other):
        """Respects NaN and Inf"""
        ox = self._op_check(other)
        r = self.dec_value.max(ox)
        if r == self.dec_value:
            return self
        else:
            return other

    def min(self, other):
        """Respects NaN and Inf"""
        ox = self._op_check(other)
        r = self.dec_value.min(ox)
        if r == self.dec_value:
            return self
        else:
            return other

    def __copy__(self):
        if type(self) == ContextClass:
            return self     # I'm immutable; therefore I am my own clone
        return self.__class__(str(self))

    def __deepcopy__(self, memo):
        if type(self) == ContextClass:
            return self     # My components are also immutable
        return self.__class__(str(self))



class context_registry(object):
    """Registry saves re-creating temporary copies of the same context classes
    during eval() calls, etc., by keeping a registry of all created
    contexts in the present session.
    """
    def __init__(self):
        self.contexts = {}

    def __call__(self, char_digits, sig_digits, rounding=ROUND_HALF_UP):
        try:
            return self.contexts[(char_digits, sig_digits, rounding)]
        except KeyError:
            return self.make_context(char_digits, sig_digits, rounding)

    def make_context(self, char_digits, sig_digits, rounding):
        """Class factory for binary float arithmetic using the given number of
        digits for the characteristic (exponent) and significand (mantissa, or
        fraction).

        rounding type defaults to rounding up (away from 0).
        """
        if rounding not in _round_code:
            raise ValueError("Invalid rounding type specified")

        class CharacteristicClass(BinaryCharacteristic):
            digits = char_digits
            largest = 2**char_digits-1
            bias = 2**(char_digits-1)-1
            exp_largest = 2**(char_digits-1)
            exp_lowest = -2**(char_digits-1) + 1

        class SignificandClass(BinarySignificand):
            digits = sig_digits
            largest = 2**sig_digits-1

        class context(ContextClass):
            characteristicClass = CharacteristicClass
            significandClass = SignificandClass
            largest_denorm = (Decimal(2) ** Decimal(-2**(char_digits-1)+2) ) * \
                                (1 - Decimal(2)**(-sig_digits))
            largest_norm = (1 - Decimal("0.5")**(sig_digits+1)) * \
                                  2 ** (2**(char_digits - 1))
            digits = 1 + char_digits + sig_digits
            round_mode = rounding
            Etop = 2**(char_digits-1)
            Etiny = -2**(char_digits-1) + 1

        context.__name__ = "Float_%d_%d_%s" % (char_digits, sig_digits,
                                       _round_code[rounding])

        self.contexts[(char_digits, sig_digits, rounding)] = context
        return context

define_context = context_registry()

single = define_context(8, 23)  # IEEE 754 32 bit float
double = define_context(11, 52)  # IEEE 754 64 bit float
quadruple = define_context(15, 112)  # IEEE 754 128 bit float
half = define_context(5, 10)  # IEEE 754 16 bit float

test = define_context(4, 6, ROUND_DOWN)  # for learning purposes


class Binary(object):
    """Constructor for binary floating point representation from a binary string
    or Decimal class representation of a real number: e.g. -1101.100011 or
    Decimal("-13.546875000"). The value may also be an instance of an existing
    context.

    If a context is given as a Context class, the return value will be an
    instance of that class (a IEEE 754 representation of that binary value).
    If the value given was from a different context it will be coerced.

    The context may also be provided as the tuple: (characteristic_digits,
                                                    significand_digits,
                                                    rounding mode string)
    although this is intended primarily for internal use or for eval(repr(x))
    for a Context object x.

    Binary() is the same as Binary('0') to be functionally compatible with
    the Decimal class.
    """
    def __init__(self, x='0', context=None):
        if isinstance(context, tuple):
            self.context = define_context(context[0], context[1],
                                          rounding=context[2])
        else:
            self.context = context

        # placeholder for representation of x
        self.rep = None

        if isinstance(x, Binary):
            self.dec = x.dec
            self.bin = x.bin
            if context is None:
                self.context = x.context
                # in case x.context is not None (otherwise gets
                # overwritten by x.dec == x.rep anyway)
                self.rep = x.rep
        elif isinstance(x, ContextClass):
            if context is None:
                # optimization -- don't recreate self.rep later
                # from this context, keep it now.
                self.context = x.__class__
                self.rep = x
                self.dec = x.as_decimal()
                self.bin = str(x.as_binary())
            else:
                x_dec = x.as_decimal()
                if abs(x_dec) > self.context.largest_norm:
                    if x_dec < 0:
                        self.bin = "-Inf"
                        seld.dec = Decimal("-Inf")
                    else:
                        self.bin = "Inf"
                        self.dec = Decimal("Inf")
                    self.rep = self.context(self.dec)
        elif isinstance(x, Decimal):
            self.dec = x
            if self.context is None:
                raise ValueError("Cannot create arbitrary precision binary "
                                 "value without a representation context")
            if x._isnan() or x._isinfinity() != 0:
                if x._isnan():
                    self.bin = "NaN"
                else:
                    if x < 0:
                        self.bin = "-Inf"
                    else:
                        self.bin = "Inf"
            elif abs(x) > self.context.largest_norm:
                if x < 0:
                    self.dec = Decimal("-Inf")
                    self.bin = "-Inf"
                else:
                    self.dec = Decimal("Inf")
                    self.bin = "Inf"
            else:
                self.bin = dec2binstr(x, self.context)
        else:
            # string
            bstr = x.lower()
            if bstr in ['-inf', 'inf', 'nan']:
                self.bin = x
                self.dec = Decimal(x)
            else:
                self.bin = x
                self.dec = binvalstr2dec(bstr)

        if self.context is None:
            self.rep = self.dec
        else:
            if self.rep is None:
                try:
                    self.rep = self.context(self.dec)
                except BinaryOverflow:
                    if self.dec < 0:
                        self.dec = Decimal("-Inf")
                        self.bin = "-Inf"
                    else:
                        self.dec = Decimal("Inf")
                        self.bin = "Inf"
                    self.rep = self.context(self.dec)
            self.dec = self.rep.dec_value
            if self.rep.bin_value == "":
                # lazy evaluation hasn't been performed yet
                self.bin = dec2binstr(self.dec, self.rep)
                # might as well update the representation
                self.rep.bin_value = self.bin
            else:
                self.bin = self.rep.bin_value

    def __hash__(self):
        return hash(self.rep)

    def __str__(self):
        return self.bin

    def __repr__(self):
        if self.context:
            return 'Binary("%s", (%d, %d, %s))' % (self.bin,
                        self.context.characteristicClass.digits,
                        self.context.significandClass.digits,
                        self.context.round_mode)
        else:
            return 'Binary("%s")' % self.bin

    def as_binary(self):
        return self

    def as_decimal(self):
        return self.dec

    def _op_check(self, other):
        if isinstance(other, (int, long, npy.int32, npy.int64)):
            ox, c = Decimal(other), None
        elif isinstance(other, Binary):
            ox, c = other.dec, other.context
        elif isinstance(other, Decimal):
            ox, c = other, None
        elif isinstance(other, ContextClass):
            # ContextClass is strict about comparing only with others
            # of the same representation, so ensure self is
            if self.context == other.__class__:
                ox, c = other.as_decimal(), other.__class__
            else:
                raise TypeError("Invalid object for comparison")
        else:
            raise TypeError("Invalid object for comparison")
        if self.context:
            s_digits = self.context.digits
        else:
            s_digits = 0
        if c:
            c_digits = c.digits
        else:
            c_digits = 0
        if s_digits > c_digits:
            ctx = self.context
        else:
            if s_digits > 0 and s_digits == c_digits:
                # contexts have the same precision, but what about
                # rounding?
                if self.context.round_mode == c.round_mode:
                    ctx = c
                else:
                    raise ValueError("Clash of rounding modes for "
                                     "equal-precision comparison")
            else:
                ctx = c
        return ox, ctx

    def __eq__(self, other):
        ox, c = self._op_check(other)
        return self.dec == ox

    def __ne__(self, other):
        ox, c = self._op_check(other)
        return self.dec != ox

    def __le__(self, other):
        ox, c = self._op_check(other)
        return self.dec <= ox

    def __lt__(self, other):
        ox, c = self._op_check(other)
        return self.dec < ox

    def __ge__(self, other):
        ox, c = self._op_check(other)
        return self.dec >= ox

    def __gt__(self, other):
        ox, c = self._op_check(other)
        return self.dec > ox

    def __neg__(self):
        return self.__class__(-self.rep)

    def __abs__(self):
        return self.__class__(abs(self.rep))

    def __add__(self, other):
        ox, ctx = self._op_check(other)
        return self.__class__(self.dec + ox, ctx)

    __radd__ = __add__

    def __sub__(self, other):
        ox, ctx = self._op_check(other)
        return self.__class__(self.dec - ox, ctx)

    def __rsub__(self, other):
        ox, ctx = self._op_check(other)
        return self.__class__(ox - self.dec, ctx)

    def __mul__(self, other):
        ox, ctx = self._op_check(other)
        return self.__class__(self.dec * ox, ctx)

    __rmul__ = __mul__

    def __div__(self, other):
        ox, ctx = self._op_check(other)
        return self.__class__(self.dec / ox, ctx)

    def __rdiv__(self, other):
        ox, ctx = self._op_check(other)
        return self.__class__(ox / self.dec, ctx)

    __rtruediv__ = __rdiv__

    def __pow__(self, other):
        ox, ctx = self._op_check(other)
        return self.__class__(self.dec ** ox, ctx)

    def __rpow__(self, other):
        ox, ctx = self._op_check(other)
        return self.__class__(ox ** self.dec, ctx)

    def __nonzero__(self):
        return self.dec != 0

    def sqrt(self):
        return self.__class__(self.dec.sqrt(), self.context)

    def max(self, other):
        """Respects NaN and Inf"""
        ox, ctx = self._op_check(other)
        r = self.dec.max(ox)
        if r == self.dec:
            return self
        else:
            return other

    def min(self, other):
        """Respects NaN and Inf"""
        ox, ctx = self._op_check(other)
        r = self.dec.min(ox)
        if r == self.dec:
            return self
        else:
            return other

    def __reduce__(self):
        return (self.__class__, (repr(self),))

    def __copy__(self):
        if type(self) == Binary:
            return self     # I'm immutable; therefore I am my own clone
        return self.__class__(str(self))

    def __deepcopy__(self, memo):
        if type(self) == Binary:
            return self     # My components are also immutable
        return self.__class__(str(self))


def binvalstr2dec(x):
    """Convert signed real numbers in binary string form to decimal
    value (no special values Inf, NaN), including values in scientific notation.
    """
    if not isbinstr(x):
        raise ValueError("Invalid string representation of binary"
                             " float: %s" % x)
    if x[0] == '-':
        x = x[1:]
        sign = -1
    else:
        sign = 1
    if 'e' in x:
        x, estr = x.split('e')
        e = int(estr)
    elif 'E' in x:
        x, estr = x.split('E')
        e = int(estr)
    else:
        e = 0
    if '.' in x:
        try:
            whole, frac = x.split('.')
        except ValueError:
            raise ValueError("Invalid string representation of binary"
                             " float")
        else:
            if frac == "":
                frac = '0'
            if whole == "":
                whole = '0'
    else:
        whole = x
        frac = '0'
    try:
        dec_whole = Decimal(int(whole, base=2)) * Decimal(2)**e
    except ValueError:
        dec_whole = Decimal(0)
    dec_frac = binfracstr2decfrac(frac) * Decimal(2)**e
    return sign*(dec_whole+dec_frac)


def isbinstr(arg):
    # supports unary + / - at front, and checks for usage of exponentials
    # (using 'E' or 'e')
    s = arg.lower()
    try:
        if s[0] in ['+','-']:
            s_rest = s[1:]
        else:
            s_rest = s
    except IndexError:
        return False
    if '0' not in s_rest and '1' not in s_rest:
        return False
    pts = s.count('.')
    exps = s.count('e')
    pm = s_rest.count('+') + s_rest.count('-')
    if pts > 1 or exps > 1 or pm > 1:
        return False
    if exps == 1:
        exp_pos = s.find('e')
        pre_exp = s[:exp_pos]
        # must be numbers before and after the 'e'
        if not npy.sometrue([n in ('0','1') for n in pre_exp]):
            return False
        if s[-1]=='e':
            # no chars after 'e'!
            return False
        if not npy.sometrue([n in ('0','1','2','3','4','5','6','7','8','9') \
                             for n in s[exp_pos:]]):
            return False
        # check that any additional +/- occurs directly after 'e'
        if pm == 1:
            pm_pos = max([s_rest.find('+'), s_rest.find('-')])
            if s_rest[pm_pos-1] != 'e':
                return False
            e_rest = s_rest[pm_pos+1:]   # safe due to previous check
            s_rest = s_rest[:pm_pos+1]
        else:
            e_rest = s[exp_pos+1:]
            s_rest = s[:exp_pos+1]
        # only remaining chars in s after e and possible +/- are numbers
        if '.' in e_rest:
            return False
    # cannot use additional +/- if not using exponent
    if pm == 1 and exps == 0:
        return False
    return npy.alltrue([n in ('0', '1', '.', 'e', '+', '-') for n in s_rest])


def binstr2dec(bstr):
    """Convert binary string representation of an integer to a decimal integer.
    """
    return int(bstr, base=2)


def decint2binstr(n):
    """Convert decimal integer to binary string.
    """
    if n < 0:
        return '-' + decint2binstr(-n)
    s = ''
    while n != 0:
        s = str(n % 2) + s
        n >>= 1
    return s or '0'


def binfracstr2decfrac(bstr):
    """Convert non-negative binary string fraction (without radix) to decimal
    fraction.
    e.g. to convert ".1101", binfracstr2decfrac('1101') -> Decimal("0.8125")
    """
    assert bstr[0] != '-', "Only pass non-negative values"
    dec_value = 0
    half = Decimal("0.5")
    for place, bit in enumerate(bstr):
        if int(bit) == 1:
            dec_value += half**(place+1)
    return dec_value


def frexp(d, context):
    """Implementation of 'frexp' for arbitrary precision decimals.
    Result is a pair F, E, where 0 < F < 1 is a Decimal object,
    and E is a signed integer such that

    d = F * 2**E

    context specifies the maximum absolute value of the exponent
    to ensure termination of the calculation. e.g. for double precision
    pass the 'double' Context class which defines a characteristic
    of 11 bits, with maximum exponent size of 1024.
    """
    e_largest = context.characteristicClass.exp_largest
    if d < 0:
        res = frexp(-d, e_largest)
        return -res[0], res[1]

    elif d == 0:
        return Decimal("0"), 0

    elif d >= 1:
        w_dec = int(d)
        e_dec = 0
        while w_dec > 0 and abs(e_dec) <= e_largest:
            d /= 2
            w_dec = int(d)
            e_dec += 1
        return d, e_dec

    else:
        # 0 < d < 1
        w_dec = 0
        e_dec = 0
        while w_dec == 0 and abs(e_dec) <= e_largest:
            w_dec = int(d*2)
            if w_dec > 0:
                break
            else:
                d *= 2
                e_dec -= 1
        return d, e_dec


def dec2binstr(x, context=None):
    if x < 0:
        signstr = '-'
        valstr = -x
    elif x == 0:
        return '0.0'
    else:
        signstr = ''
        valstr = x
    # convert to binary fraction representation
    e, f = decfrac2binrep(valstr, context)
    return signstr + '0.' + f + 'E' + str(int(e, base=2))


def decfrac2binrep(x, context):
    """Convert positive decimal float to the nearest representable
    "<characteristic> <significand>" binary string representation (natural
    format, where characteristic may be negative), using an exponent no bigger
    than permitted in the given context.

    """
    assert x > 0, "Provide only positive Decimal float value"
    assert isinstance(x, Decimal), "Provide only positive Decimal float value"
    fraction, exponent = frexp(x, context)
    max_bits = context.characteristicClass.exp_largest + \
                 context.significandClass.digits
    bfrac = npy.zeros(max_bits, int)
    i = 0
    i_stop = max_bits
    not_seen_one = True
    while fraction > 0 and i < max_bits:
        fraction *= 2
        bit = int(fraction)
        if not_seen_one and bit == 1:
            # speed optimization
            i_stop  = i + context.significandClass.digits + 2
        bfrac[i] = bit
        fraction -= bit
        i += 1
        if i >= i_stop:
            break
    # negative exponents OK for this usage
    return decint2binstr(exponent), "".join([str(bit) for \
                                             bit in bfrac[:i]])


def pad(value, digits, to_right=False):
    """Only use for positive binary numbers given as strings.
    Pads to the left by default, or to the right using to_right flag.

    Inputs: value -- string of bits
            digits -- number of bits in representation
            to_right -- Boolean, direction of padding

    Output: string of bits of length 'digits'

    Raises exception if value is larger than digits in length.

    Example:
      pad('0010', 6) -> '000010'
      pad('0010', 6, True) -> '001000'
    """
    len_val = len(value)
    assert len_val <= digits
    rem_digits = digits - len_val
    if to_right:
        return value + "0"*rem_digits
    else:
        return "0"*rem_digits + value

def bin_sign(x):
    """Binary representation of sign: x < 0 is represented as 1, 0 otherwise.
    """
    s=npy.sign(x)
    if s >= 0:
        return 0
    else:
        return 1


## exceptions

class BinaryException(ArithmeticError):
    def __init__(self, value=None):
        self.value = value
        self.code = None

    def __str__(self):
        return repr(self.value)

    def __repr__(self):
        return repr(self.value)

class BinaryOverflow(BinaryException):
    pass

class BinaryUnderflow(BinaryException):
    pass

class BinaryNegativeValue(BinaryException):
    pass

class BinaryRemainderValue(BinaryException):
    pass

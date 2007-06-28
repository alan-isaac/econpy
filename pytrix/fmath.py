from __future__ import absolute_import
import math


## radix
float_radix = 0

def calc_float_radix():
	float_radix = 0
	a = 1.0
	test = True
	while test:
		a += a
		temp1 = a + 1.0
		temp2 = temp1 - a
		test = (temp2 - 1.0 != 0.0)
	b = 1.0
	while float_radix == 0:
		b += b
		temp1 = a + b
		float_radix = int(temp1 - a)
	return float_radix

def get_float_radix():
	global float_radix
	if float_radix == 0:
		float_radix = calc_float_radix()
	return float_radix

## machine precision
machine_precision = 0.0

def calc_machine_precision():
	float_radix = get_float_radix()
	inverse_radix = 1.0/float_radix
	machine_precision = 1.0
	temp = 1.0 + machine_precision
	while (temp - 1.0 != 0.0):
		machine_precision *= inverse_radix
		temp = 1.0 + machine_precision
	return machine_precision

def get_machine_precision():
	global machine_precision
	if machine_precision == 0:
		machine_precision = calc_machine_precision()
	return machine_precision

## default_numerical_precision
default_numerical_precision = 0.0

def get_default_numerical_precision():
	global default_numerical_precision
	if default_numerical_precision == 0:
		default_numerical_precision = math.sqrt(get_machine_precision())
	return default_numerical_precision


def feq(a, b, precision=get_default_numerical_precision()):
	inf_norm = max(abs(a), abs(b))
	return inf_norm < precision or abs(a-b) < precision * inf_norm


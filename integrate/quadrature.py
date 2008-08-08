def riemann_p(f, p, tags):
	"""Return float,
	a Riemann sum for the partition `p`."""
	x1x2 = zip(p[:-1],p[1:])
	if tags == 'left':
		result = sum( (x2-x1)*f(x1) for x1,x2 in x1x2 )
	elif tags == 'right':
		result = sum( (x2-x1)*f(x2) for x1,x2 in x1x2 )
	elif tags in ('center','middle'):
		result = sum( (x2-x1)*f((x1+x2)/2.0) for x1,x2 in x1x2 )
	elif tags == 'trapz': #delay division by 2
		result = sum( (x2-x1)*(f(x1)+f(x2)) for x1,x2 in x1x2 )
	else:
		raise ValueError("Unknown tag type: %s" % (tags))
	if tags == 'trapz':
		result *= 0.5
	return result

def riemann_n(f, a, b, n, tags):
	"""Return float,
	a Riemann sum for `n` equal intervals."""
	dx = (b - a) / float(n)
	if tags in ('left','right','trapz'):
		pt = a + dx
	elif tags in ('middle','center'):
		pt = a + dx/2.0
	else:
		raise ValueError("unknown tag type"%(tags))
	result = sum(f(pt + i*dx) for i in range(n-1) )
	if tags == 'left':
		result += f(a)
	elif tags == 'right':
		result += f(b)
	elif tags == 'trapz':
		result += (f(a) + f(b)) / 2.0
	else:   # tags in ('middle','center'):
		result += f(b - dx/2.0)
	result *= dx
	return result

def iterative_trapz(f, a, b, maxiter=100, prt=False):
	"""Return float,
	quadrature of `f` based on iterative trapezoid rule.

	:requires: `riemann_n`
	"""
	refine = True; n = 1; iter = 0
	area = (b - a) * (f(a)+f(b)) / 2.0
	while(refine and iter<maxiter):
		area_new = 0.5*(area + riemann_n(f, a, b, n, 'middle'))
		n *= 2; iter += 1
		diff = abs(area_new - area)
		if prt:
			print "Old: %f \t New: %f \t Change: %f"%(area,area_new,diff)
		refine = diff > 1e-9
		area = area_new
	return area


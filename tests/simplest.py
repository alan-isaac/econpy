#BEGIN orderedpartitions
def ordered_partitions(n, nparts):
	result = list()
	if (nparts == 1):
		result.append([n])
	else:
		for n1 in range(n+1):
			for rest in ordered_partitions(n-n1, nparts-1):
				result.append([n1] + rest)
	return result
#END orderedpartitions


# vim: set noet:ts=4:sw=4

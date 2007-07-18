try:
	import econpy
except ImportError:
	import os, sys
	package4tests = os.path.abspath(__file__)
	for _ in range(3):
		package4tests = os.path.split(package4tests)[0]
	sys.path.insert(0,package4tests)  #need location of econpy
	import econpy

import logging
logging.basicConfig(level=logging.INFO,format='%(levelname)-10s %(message)s')
script_logger = logging.getLogger('script_logger')

'''Used by tests to find the econpy package,
either as installed or relative to script location.
'''
try:
    import econpy
except ImportError:
    import os, sys
    package4tests = os.path.abspath(__file__)
    for _ in range(3):
        package4tests = os.path.split(package4tests)[0]
    sys.path.insert(0,package4tests)  #need location of econpy
    import econpy


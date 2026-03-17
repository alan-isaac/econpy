This README accompanies the code used in the paper entitled
"The ABM Template Models: A Reformulation with Reference Implementations".
The code is copyright 2011 by Alan G. Isaac, but is released under
the MIT license: http://www.opensource.org/licenses/mit-license
(Roughly that means you can do as you wish with the code,
as long as you acknowledge this copyright and do not expect any warranty.)

To run this code you need:

- Python 2.6 or 2.7 (including Tkinter)
- the gridworld module: 
  http://econpy.googlecode.com/svn-history/r176/trunk/abm/gridworld/gridworld.py
- the cell data file for template model 15
  from http://condor.depaul.edu/~slytinen/abm/

To run template model 8 and above, you need write privileges
on your computer: the models will attempt to write to
/temp/temp.csv.  (This location is easily changed at
the top of template08.py.)

Each model is designed to be run separately,
but later models import from earlier models.
So unzip all of the template models into a common directory.
Also, copy gridworld.py into this same directory
(or make it available on your PYTHONPATH).
Finally, unzip the cell data file into the same directory,
giving the name Cell.Data to the unzipped file.

Note that gridworld uses Tkinter.  Do not try to run the
template models in IDLE, which is also written in Tkinter.
It is best to run them from a command shell.


ADDENDUM 2018-08-12: Thanks to Steve Railsback for permitting
the addition of the file Cell.Data to this repository, also
under the MIT license.

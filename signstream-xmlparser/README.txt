# $Id: README-ss.txt 815 2009-07-09 11:44:23Z Christian Vogler $

This package contains everything to read a SignStream XML file into memory,
and to query and manipulate the annotations contained therein.

No installation is required; just place the analysis directory in the
same directory as your main script, or in some other place where Python
looks for packages.

test/ contains the test cases for this package. If you would like to run
them, the python-nose package must be installed (or see
http://code.google.com/p/python-nose/). Then run "nosetests" from the
top-level directory.

showglosses.py and glosses_n_head.py are two example scripts that show the
basics of reading XML files and displaying some annotations. They each
expect the name of a SignStream XML file as a command line argument. One
such file can be found in test/resources/accident.ss3.xml.

For further documentation see the Python docstrings, e.g.
pydoc analysis.signstream and pydoc analysis.signstream.dom,
or equivalently help(analysis.signstream) from within the Python
interpreter.

Any questions, fixes, comments, please contact me at
christian.vogler@gmail.com.

 
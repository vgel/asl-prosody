# Prosodic Pausing in ASL Analysis

Prosodic analysis on NCSLGR corpus data, using an algorithm described in the
paper *Pauses and Syntax in American Sign Language* by Francois Grosjean and Harlan Lane (1977).

I am not the author of the NCSLGR corpus data. It is from http://www.bu.edu/asllrp/ncslgr-for-download/download-info.html. It's worth checking there to see if a more up-to-date version is available, however I have been having issues connecting to the fileserver that hosts the zip file, so I copied it into this repository in case someone else has the same problem.

The `signstream-xmlparser` library was written by Christian Vogler.

Usage: `python analyze.py ncslgr-xml/ncslgr10a.xml`.

By default, the script will print out a bracketed tree format that will work in several different online syntax tree viewers. My favorite is http://mshang.ca/syntree/. It should also work with the TeX qtree package, with a bit of modification.

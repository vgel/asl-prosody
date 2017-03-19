#!/usr/bin/python

# -*- coding: utf-8 -*-
# $Id$

# Compares two SignStream XML files.
# Note that this comparison does not cover every attribute, but it does
# touch on all the useful ones.

import sys
import analysis.signstream as ss

if len(sys.argv) != 3:
  sys.stderr.write("Usage: ss-compare.py <XML file1> <XML file2>\n")
  sys.exit(2)

db1 = ss.SignStreamDatabase.read_xml(sys.argv[1])
db2 = ss.SignStreamDatabase.read_xml(sys.argv[2])
if db1 == db2:
  sys.stderr.write("same\n")
  sys.exit(0)
else:
  sys.stderr.write("different\n")
  sys.exit(1)

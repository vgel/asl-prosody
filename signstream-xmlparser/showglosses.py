#!/usr/bin/python

# -*- coding: utf-8 -*-
# $Id$

# Simple example showing how to display the glosses track of a signstream database

import sys
import analysis.signstream as ss

if len(sys.argv) != 2:
  sys.stderr.write("Usage: showglosses.py <XML file>\n")
  sys.exit(1)

db = ss.SignStreamDatabase.read_xml(sys.argv[1])

for participant in db.get_participants():
  print unicode(participant)
  for token in participant.get_tokens("main gloss"):
    (start, end) = token.get_timecodes()
    text = token.get_text()
    filenames = [m.get_filename() for m in token.get_utterance().get_media()]
    print u"%6d-%6d %s (in %20s)" % (start, end, text, ", ".join(filenames))

#!/usr/bin/python

# -*- coding: utf-8 -*-
# $Id$

# Simple example showing how to display the media for each utterance

import sys
import analysis.signstream as ss

if len(sys.argv) != 2:
  sys.stderr.write("Usage: showmedia.py <XML file>\n")
  sys.exit(1)

db = ss.SignStreamDatabase.read_xml(sys.argv[1])
for participant in db.get_participants():
  for utterance in participant.get_utterances():
    print "Utterance #%d" % utterance.get_id()
    media = utterance.get_media()
    for video in media:
      print "-- %s" % video.get_filename()


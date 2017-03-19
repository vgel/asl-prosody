# -*- coding: utf-8 -*-
# $Id$

#@PydevCodeAnalysisIgnore

import nose.tools as nt
import nose
import analysis.signstream as ss
import analysis.xmlbase as xmlbase
from analysis.xmlbase import XMLException

def test_duplicate_participant():
  try:
    data = ss.SignStreamDatabase.read_xml("test/resources/bad_participant.ss3.xml")
    nt.assert_true(False) # the previous line should throw, so we never get here
  except XMLException, e:
    print e
    nt.eq_(type(e), xmlbase.ContentHandlerError)
    nt.eq_(type(e.exception), ss.DuplicateParticipant)
    nt.eq_(e.line, 9)

def test_duplicate_field():
  try:
    data = ss.SignStreamDatabase.read_xml("test/resources/bad_field.ss3.xml")
    nt.assert_true(False) # the previous line should throw, so we never get here
  except XMLException, e:
    print e
    nt.eq_(type(e), xmlbase.ContentHandlerError)
    nt.eq_(type(e.exception), ss.DuplicateField)
    nt.eq_(e.line, 63)

def test_duplicate_value():
  try:
    data = ss.SignStreamDatabase.read_xml("test/resources/bad_value.ss3.xml")
    nt.assert_true(False) # the previous line should throw, so we never get here
  except XMLException, e:
    print e
    nt.eq_(type(e), xmlbase.ContentHandlerError)
    nt.eq_(type(e.exception), ss.DuplicateFieldValue)
    nt.eq_(e.line, 34)

def test_duplicate_media():
  try:
    data = ss.SignStreamDatabase.read_xml("test/resources/bad_media.ss3.xml")
    nt.assert_true(False) # the previous line should throw, so we never get here
  except XMLException, e:
    print e
    nt.eq_(type(e), xmlbase.ContentHandlerError)
    nt.eq_(type(e.exception), ss.DuplicateMediaFile)
    nt.eq_(e.line, 54)

def test_duplicate_utterance():
  try:
    data = ss.SignStreamDatabase.read_xml("test/resources/bad_utterance.ss3.xml")
    nt.assert_true(False) # the previous line should throw, so we never get here
  except XMLException, e:
    print e
    nt.eq_(type(e), xmlbase.ContentHandlerError)
    nt.eq_(type(e.exception), ss.DuplicateUtterance)
    nt.eq_(e.line, 61)

def test_dom():
  data = ss.SignStreamDatabase.read_xml("test/resources/accident.ss3.xml")
  
  p = list(data.get_participants())
  nt.eq_(len(p), 1)
  nt.eq_(p[0], data.get_participant(p[0].get_label()))
  nt.eq_(p[0], data.get_participant(0))
  nt.eq_(p[0].get_name(), "Michael Eric Schlang")
  
  m = list(data.get_media())
  nt.eq_(len(m), 2)
  nt.eq_(m[0].get_id(), 478)
  nt.eq_(m[0].get_filename(), "accident_1065_small_0.mov")
  nt.eq_(m[1].get_filename(), "accident_1065_small_2.mov")
  
  f = list(data.get_fields())
  nt.eq_(len(f), 36)
  nt.eq_(f[10], data.get_field(f[10].get_label()))
  nt.eq_(f[10], data.get_field(f[10].get_id()))
  nt.assert_raises(ss.InvalidField, data.get_field, "advx")
  nt.eq_(f[23].get_id(), 26)
  nt.eq_(f[35].get_id(), 20001)
  nt.eq_(f[23].get_name(), "adverbial")
  nt.eq_(f[23].get_label(), "adv")
  
  fv = list(f[23].get_values())
  nt.eq_(len(fv), 9)
  nt.eq_(fv[0].get_id(), 2)
  nt.eq_(f[23][2], fv[0])
  nt.eq_(fv[0].get_label(), "far")
  nt.eq_(fv[0].get_name(), "far")
  nt.eq_(fv[-3].get_label(), None)
  nt.eq_(fv[-3].get_name(), "HOLD")
  
  u = list(p[0].get_utterances())
  nt.eq_(len(u), 72)
  nt.eq_(u[0].get_id(), 0)
  nt.eq_(u[0].get_timecodes(), (0, 7066))
  nt.eq_(u[0].get_participant(), p[0])
  ml = u[0].get_media()
  nt.eq_(len(ml), 2)
  nt.assert_true(ml[0] in m)
  nt.assert_true(ml[1] in m)
  gloss = data.get_field("main gloss")
  gloss_t = list(u[0].get_tokens_for_field(gloss.get_id()))
  nt.eq_(gloss_t, list(u[0].get_tokens_for_field("main gloss")))
  nt.eq_(len(gloss_t), 10)
  field_tokens = list(u[0].get_tokens())
  nt.eq_(len(field_tokens), 14)
  nt.eq_(field_tokens[-3], gloss_t)
  
  gloss_t2 = list(u[1].get_tokens_for_field(gloss.get_id()))
  nt.eq_(len(gloss_t2), 9)
  all_glosses = list(p[0].get_tokens("main gloss"))
  nt.eq_(all_glosses[10:19], gloss_t2)
  
  ttext = gloss_t2[0]
  tstandard = gloss_t2[1]
  nt.eq_(ttext.get_text(), '5"that\'s the way it is"')
  nt.eq_(ttext.get_field(), gloss)
  nt.eq_(ttext.get_utterance(), u[1])
  nt.assert_raises(ss.dom.NonStandardToken, ttext.get_field_value)
  nt.assert_false(ttext.is_standard())
  nt.eq_(tstandard.get_text(), 'HOLD')
  nt.eq_(tstandard.get_field(), gloss)
  nt.eq_(tstandard.get_utterance(), u[1])
  fv = tstandard.get_field_value()
  nt.eq_(fv, gloss[400000])
  nt.assert_true(tstandard.is_standard())
  nt.eq_(ttext.get_timecodes(), (7200, 7666))
  nt.eq_(tstandard.get_timecodes(), (7200, 7800))
  
  thats = gloss_t2[0]
  head_tok = thats.get_coinciding_tokens("hp: tilt fr/bk")
  nt.eq_(len(head_tok), 1)
  nt.eq_(head_tok[0].get_text(), "front")
  jut_tok = thats.get_coinciding_tokens("hp: jut")
  nt.eq_(len(jut_tok), 2)
  nt.eq_(jut_tok[0].get_text(), "ONSET")
  nt.eq_(jut_tok[1].get_text(), "slightly back")
  
  hold = gloss_t2[1]
  head_tok = hold.get_coinciding_tokens("hp: tilt fr/bk")
  nt.eq_(len(head_tok), 1)
  nt.eq_(head_tok[0].get_text(), "front")
  
  really = gloss_t2[2]
  head_tok = really.get_coinciding_tokens("hp: tilt fr/bk")
  nt.eq_(len(head_tok), 1)
  nt.eq_(head_tok[0].get_text(), "ONSET")
  
  yesterday = gloss_t2[3]
  head_tok = yesterday.get_coinciding_tokens("hp: tilt fr/bk")
  nt.eq_(len(head_tok), 1)
  nt.eq_(head_tok[0].get_text(), "ONSET")
  
  ix1 = gloss_t2[4]
  jut_tok = ix1.get_coinciding_tokens("hp: jut")
  nt.eq_(len(jut_tok), 0)
  
  work = gloss_t2[5]
  head_tok = work.get_coinciding_tokens("hp: tilt fr/bk")
  nt.eq_(len(head_tok), 2)
  nt.eq_(head_tok[0].get_text(), "ONSET")
  nt.eq_(head_tok[1].get_text(), "front")
  
  nt.assert_raises(ss.InvalidField, work.get_coinciding_tokens, "asdf")
  nt.eq_(len(work.get_coinciding_tokens("adv")), 0)

def test_equality():
  db1 = ss.SignStreamDatabase.read_xml("test/resources/accident.ss3.xml")
  db1a = ss.SignStreamDatabase.read_xml("test/resources/accident.ss3.xml")
  db2 = ss.SignStreamDatabase.read_xml("test/resources/ali.ss3.xml")
  nt.assert_true(db1 == db1)
  nt.assert_true(db1 == db1a)
  nt.assert_false(db1 == db2)
  
def test_inequality():
  db1 = ss.SignStreamDatabase.read_xml("test/resources/accident.ss3.xml")
  db1a = ss.SignStreamDatabase.read_xml("test/resources/accident.ss3.xml")
  db2 = ss.SignStreamDatabase.read_xml("test/resources/ali.ss3.xml")
  nt.assert_true(db1 != db2)
  nt.assert_false(db1 != db1)
  nt.assert_false(db1 != db1a)

def test_missing_field_label():
  db = ss.SignStreamDatabase.read_xml("test/resources/ncslgr10a.ss3.xml")
  hm_jut = db.get_field(7)
  lean = db.get_field(8)
  lean2 = db.get_field("body lean")
  nt.eq_(hm_jut.get_label(), "hm: jut")
  nt.eq_(hm_jut.get_name(), "head mvmt: jut")
  nt.eq_(lean.get_name(), "body lean")
  nt.eq_(lean.get_label(), "body lean")
  nt.eq_(lean, lean2)

def test_slice():
  ssdb = ss.SignStreamDatabase()
  ssdb._add_participant(1, 29, 'ASL', 'Ben', 'Benjamin Bahan', 'male')
  ssdb._add_media(1, 'blabla')
  ssdb._add_field(2, 'main gloss', 'main gloss', None)
  ssdb._add_utterance(1, 1, 1000, 2000, [1])
  ssdb._add_token(1, 1, 2, 100, 400, None, "TREE")
  u = list(ssdb.get_participant(1).get_utterances())[0]
  t = list(u.get_tokens())[0][0]
  nt.eq_(u.slice(60.0), slice(60, 121))
  nt.eq_(t.slice(60.0), slice(66, 85))

  
if __name__ == '__main__':
  nose.runmodule()

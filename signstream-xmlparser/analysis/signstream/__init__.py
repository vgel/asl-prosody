# -*- coding: utf-8 -*-
# $Id$

from __future__ import absolute_import

import xml.sax as sax
import analysis.xmlbase as xmlbase

from analysis.signstream.dom import *

class SignStreamDatabase(object):
  """Represents a SignStream database"""
  
  def __init__(self):
    """Constructs a new database object"""
    super(SignStreamDatabase, self).__init__()
    self.participants = dict()
    self.fields = dict()
    self.media = dict()
    self.p_order = None
    self.p_index = None
    self.f_order = None
    self.f_index = None
    self.m_order = None
    
  @classmethod
  def read_xml(cls, fileobj, warn_on_error=False):
    """Reads a SignStream database from an XML file.
       fileobj can be either a file name, or a file object.
       If warn_on_error is true, XML parser errors are ignored
          with a warning message, instead of causing an exception to be raised.
    """
    parser = sax.make_parser()
    handler = _SignStreamHandler(cls, warn_on_error)
    parser.setContentHandler(handler)
    parser.parse(fileobj)
    return handler.get_database()
  
  def get_participant(self, participant):
    """Returns a particular particpant by id or label, depending on the
       type of the "participant" argument.
    """
    if isinstance(participant, basestring):
      # lookup by label
      return self.participants[self._get_participant_index()[participant]]
    else:
      # lookup by id
      return self.participants[participant]
  
  def get_participants(self):
    """Returns an iterable over all participants in order"""
    return (self.participants[pid] for pid in self._get_participant_order())
  
  def get_field(self, field):
    """Returns the field, either by id or by label, depending on the type
       of the "field" argument.
    """
    if isinstance(field, basestring):
      # lookup by name
      try:
        return self.fields[self._get_field_index()[field]]
      except KeyError:
        raise InvalidField(field)
    else:
      # lookup by id
      try:
        return self.fields[field]
      except KeyError:
        raise InvalidField(unicode(field))
    
  def get_fields(self):
    """Returns an iterable over all fields, ordered by id"""
    return (self.fields[fid] for fid in self._get_field_order())

  def get_media(self):
    """Returns an iterable over all media, ordered by id"""
    return (self._get_media(mid) for mid in self._get_media_order())
  
  def has_media(self, media_id):
    """Returns true if the given media id is in the database"""
    return self.media.has_key(media_id)
    
  def __eq__(self, other):
    """test for self == other"""
    return self.participants == other.participants and \
           self.fields == other.fields and \
           self.media == other.media
  
  def __ne__(self, other):
    """test for self != other"""
    return not (self == other)
  
  def _add_participant(self, pid, age, language, label, name, gender):
    """Adds a participant to the database"""
    if self.participants.has_key(pid):
      raise DuplicateParticipant(pid)
    self.participants[pid] = Participant(db=self, pid=pid, age=age, language=language,
                                         label=label, name=name, gender=gender)
    self.p_order = None
    self.p_index = None

  def _add_field(self, fid, name, label, constraint):
    """Adds a field (tier) to the database"""
    if self.fields.has_key(fid):
      raise DuplicateField(fid)
    self.fields[fid] = Field(fid=fid, name=name, label=label, constraint=constraint)
    self.f_order = None
    self.f_index = None
  
  def _add_value(self, fid, vid, name, label=None):
    """Adds a field value to the database"""
    self.fields[fid]._add_value(vid=vid, label=label, name=name)
  
  def _add_media(self, mid, path):
    """Adds a video to the database"""
    if self.media.has_key(mid):
      raise DuplicateMediaFile(mid)
    self.media[mid] = MediaFile(mid=mid, path=path)
    self.m_order = None
  
  def _get_media(self, mid):
    if self.media.has_key(mid):
      return self.media[mid]
    else:
      raise UnknownMediaId(mid)
  
  def _add_utterance(self, uid, pid, start, end, media):
    """Adds an utterance to the database"""
    self.participants[pid]._add_utterance(uid=uid, start=start, end=end,
                                         media=[self._get_media(mid) for mid in media])
  
  def _add_token(self, uid, pid, fid, start, end, vid, text):
    """Adds a token for a specific field (fid), in a specific utterance
       (uid, pid) to the database.
    """
    self.participants[pid]._add_token(uid=uid, field=self.fields[fid], start=start,
                                     end=end, vid=vid, text=text)

  def _get_field_order(self):
    if self.f_order is None:
      self.f_order = self.fields.keys()
      self.f_order.sort()
    return self.f_order
    
  def _get_field_index(self):
    if self.f_index is None:
      self.f_index = dict((self.fields[fid].get_label(), fid) for fid in self.fields)
    return self.f_index
  
  def _get_participant_order(self):
    if self.p_order is None:
      self.p_order = self.participants.keys()
      self.p_order.sort()
    return self.p_order

  def _get_participant_index(self):
    if self.p_index is None:
      self.p_index = dict((self.participants[pid].get_label(), pid) \
                          for pid in self.participants)
    return self.p_index
  
  def _get_media_order(self):
    if self.m_order is None:
      self.m_order = self.media.keys()
      self.m_order.sort()
    return self.m_order


# Handler class for reading SignStream databases from XML
class _SignStreamHandler(xmlbase.ContentHandlerWithDefaults):
  # Note that XML is case-sensitive, so we have to work with uppercase here.
  allowed_elements = set(["SIGNSTREAM-DATABASE", "DISTRIBUTOR", "AUTHOR", "PARTICIPANTS",
                          "PARTICIPANT", "BACKGROUND", "CODING-SCHEME", "FIELD", "PARENTS",
                          "VALUE", "MEDIA-FILES", "MEDIA-FILE", "UTTERANCES", "CITATION",
                          "UTTERANCE", "NOTES", "MEDIA-REF", "SEGMENT", "TRACK", "A",
                          "REFERENSES", "CODING-SCHEMES", "REF", "AUTHORS", "IMGS",
                          "IMG", "TEMPLATES", "TEMPLATE", "PALETTE", "ITEM", "FIELD_TYPES",
                          "FIELD_TYPE", "FIELDS", "VALUES_DFLT", "VALUE_COLLECTIONS",
                          "VALUE_COLLECTION", "SYNTACTIC_GROUP", "DEFAULT-SEGMENT", "F",
                          "SELECTED_FIINGERS", "NONSELECTED_FINGERS", "BASE_JOINTS",
                          "SPREAD", "NONBASE_JOINTS", "THUMB_CONTACT"])
  
  ignored_value_groups = set(['VALUES_DFLT',  'VALUE_COLLECTION', 'SYNTACTIC_GROUP'])
  
  def __init__(self, model_class, warn_on_error=False):
    """Initializes a handler for parsing a SignStream file.
       model_class is the class object for the database that should
       be instantiated.
    """
    xmlbase.ContentHandlerWithDefaults.__init__(self, self.allowed_elements, warn_on_error)
    self.model_class = model_class
    self.db = None
    self.current_field = None
    self.current_utterance = None
    self.current_token = None
    
  def _check_db(self):
    if self.db is None:
      raise xmlbase.UnexpectedElement(self.current_element, self.element_stack)

  def _check_field(self):
    if self.current_field is None:
      raise xmlbase.UnexpectedElement(self.current_element, self.element_stack)
  
  def _check_utterance(self):
    if self.current_utterance is None:
      raise xmlbase.UnexpectedElement(self.current_element, self.element_stack)

  def _check_media(self, media_id):
    if not self.db.has_media(media_id):
      raise UnknownMediaId(media_id)
    
  def _check_token(self):
    if self.current_token is None:
      raise xmlbase.UnexpectedElement(self.current_element, self.element_stack)

  def get_database(self):
    """Returns the SignStream database generated from the XML file."""
    return self.db
  
  def start_SIGNSTREAM_DATABASE(self, attrs):
    self.db = self.model_class()
  
  def start_PARTICIPANT(self, attrs):
    self._check_db()
    attrs = _strip_attrs(attrs)
    self.db._add_participant(age=attrs['AGE'], gender=attrs['GENDER'],
                             pid=int(attrs['ID']), label=attrs['LABEL'],
                             name=attrs['NAME'], language=attrs['LANGUAGE'])
  
  def start_FIELD(self, attrs):
    self._check_db()
    attrs = _strip_attrs(attrs)
    self.current_field = int(attrs['ID'])
    name = attrs['NAME']
    label = attrs.get('LABEL', name)
    self.db._add_field(fid=self.current_field, label=label,
                       name=name, constraint=attrs.get('CONSTRAINT', ""))
  
  def end_FIELD(self, text):
    self._check_field()
    self.current_field = None

  def start_VALUE(self, attrs):
    if self.element_stack[-1] not in self.ignored_value_groups:
      self._check_field()
      attrs = _strip_attrs(attrs)
      self.db._add_value(fid=self.current_field, vid=int(attrs['ID']),
                         label=attrs.get('LABEL', None), name=attrs['NAME'])

  def start_MEDIA_FILE(self, attrs):
    self._check_db()
    attrs = _strip_attrs(attrs)
    self.db._add_media(mid=int(attrs['ID']), path=attrs['LEGACY-PATH'])

  def start_UTTERANCE(self, attrs):
    self._check_db()
    attrs = _strip_attrs(attrs)
    self.current_utterance = dict(id=int(attrs['ID']), s=int(attrs['S']),
                                  e=int(attrs['E']), media=[], person=None)
  
  def end_UTTERANCE(self, text):
    self._check_utterance()
    self.current_utterance = None 
  
  def start_MEDIA_REF(self, attrs):
    self._check_utterance()
    self._check_media(int(attrs['ID']))
    attrs = _strip_attrs(attrs)
    self.current_utterance['media'].append(int(attrs['ID']))
  
  def start_SEGMENT(self, attrs):
    self._check_utterance()
    attrs = _strip_attrs(attrs)
    self.current_utterance['person'] = int(attrs['PARTICIPANT-ID'])
    u = self.current_utterance
    self.db._add_utterance(uid=u['id'], pid=u['person'], start=u['s'],
                           end=u['e'], media=u['media'])

  def start_TRACK(self, attrs):
    self._check_utterance()
    attrs = _strip_attrs(attrs)
    self.current_field = int(attrs['FID']) 

  def end_TRACK(self, text):
    self._check_utterance()
    self._check_field()
    self.current_field = None

  def start_A(self, attrs):
    self._check_utterance()
    self._check_field()
    attrs = _strip_attrs(attrs)
    vid = attrs.get('VID', None)
    if vid is not None:
      vid = int(vid)
    self.current_token = dict(s=int(attrs['S']), e=int(attrs['E']),
                              vid=vid)
    
  def end_A(self, text):
    self._check_token()
    u = self.current_utterance
    t = self.current_token
    self.db._add_token(uid=u['id'], pid=u['person'], fid=self.current_field,
                       start=t['s'], end=t['e'], vid=t['vid'],
                       text=text.strip())
    self.current_token = None

  
def _strip_attrs(attrs):
  return dict((k, v.strip()) for (k, v) in attrs.items())

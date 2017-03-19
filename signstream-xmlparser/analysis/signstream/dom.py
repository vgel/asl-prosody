# -*- coding: utf-8 -*-
# $Id$

# DOM-specific classes and functionality, to make the __init__.py file less cluttered.

from __future__ import absolute_import

import analysis.xmlbase as xmlbase

class SignstreamError(xmlbase.XMLException):
  def __init__(self, message):
    super(SignstreamError, self).__init__(message)

class DuplicateParticipant(SignstreamError):
  def __init__(self, pid):
    message = "Participant with id %d already exists" % pid
    super(DuplicateParticipant, self).__init__(message)

class DuplicateField(SignstreamError):
  def __init__(self, fid):
    message = "Field with id %d already exists" % fid
    super(DuplicateField, self).__init__(message)

class DuplicateFieldValue(SignstreamError):
  def __init__(self, fid, vid):
    message = "Field with id %d already has value with id %d" % (fid, vid)
    super(DuplicateFieldValue, self).__init__(message)

class DuplicateMediaFile(SignstreamError):
  def __init__(self, mid):
    message = "Media with id %d already exists" % mid
    super(DuplicateMediaFile, self).__init__(message)

class UnknownMediaId(SignstreamError):
  def __init__(self, mid):
    message = "Unknown media id %d" % mid
    super(UnknownMediaId, self).__init__(message)

class DuplicateUtterance(SignstreamError):
  def __init__(self, uid, pid):
    message = "Utterance with id %d for person %d already exists" % (uid, pid)
    super(DuplicateUtterance, self).__init__(message)

class NonStandardToken(SignstreamError):
  def __init__(self, token):
    message = u"Not a standard token: %s" % unicode(token)
    super(NonStandardToken, self).__init__(message)

class InvalidField(SignstreamError):
  def __init__(self, fieldname):
    message = u'Field "%s" does not exist' % fieldname
    super(InvalidField, self).__init__(message)


class Participant(object):
  """Represents a participant in the annotated resources"""
  
  def __init__(self, db, pid, name, label, age, gender, language):
    """Creates a participant.
         db is the referring database.
         pid is the participant's unique ID number.
         name is the participant's name.
         label is the participant's shorthand label.
         age is the participant's age.
         gender is the participant's gender (male/female).
         language is the participant's language.
    """
    super(Participant, self).__init__()
    self.db = db
    self.pid = pid
    self.name = name
    self.label = label
    self.age = age
    self.gender = gender
    self.language = language
    self.utterances = dict()
    self.uorder = None
    
  def _get_utterance_order(self):
    if self.uorder is None:
      self.uorder = self.utterances.keys()
      self.uorder.sort()
    return self.uorder
  
  def __unicode__(self):
    return u"%s: %s, %s user, age %s, id %d" % (self.name, self.gender, self.language,
                                                self.age, self.pid)

  def _add_utterance(self, uid, start, end, media):
    """Adds an utterance created by this participant"""
    if self.utterances.has_key(uid):
      raise DuplicateUtterance(uid, self.pid)
    self.utterances[uid] = Utterance(uid=uid, participant=self,
                                     start=start, end=end, media=media)
    self.uorder = None

  def _add_token(self, uid, field, start, end, vid, text):
    """Adds a token for a specific field (fid) uttered by this participant"""
    self.utterances[uid]._add_token(field=field, start=start,
                                    end=end, vid=vid, text=text)

  def get_utterances(self):
    """Enumerates the utterances by this person, in ID order.
       Returns an iterable.
    """
    order = self._get_utterance_order()
    return (self.utterances[uid] for uid in order)
  
  def get_tokens(self, field, ignore_missing = False):
    """Enumerates the tokens for a specific field, in timestamp order, as
       an iterable.
       Field can be either an ID or a label.
    """
    field_id = self.db.get_field(field).get_id()
    for utterance in self.get_utterances():
      try:
        for token in utterance.get_tokens_for_field(field_id):
          yield token
      except KeyError, e:
        # if a field does not exist for this utterance
        if not ignore_missing:
          raise e
  
  def get_name(self):
    """Returns this participant's name"""
    return self.name
  
  def get_label(self):
    """Returns this participant's label"""
    return self.label
  
  def get_gender(self):
    """Returns this participant's gender"""
    return self.gender
  
  def get_age(self):
    """Returns this participant's age"""
    return self.age
  
  def get_language(self):
    """Returns this participant's language"""
    return self.language
  
  def get_db(self):
    """Returns the database associated with this participant"""
    return self.db

  def get_id(self):
    """Returns the ID of the participant"""
    return self.pid
  
  def get_utterance(self, uid):
    """Returns utterance by ID"""
    return self.utterances[uid]
  
  def __eq__(self, other):
    """test for self == other"""
    return self.pid == other.pid and \
           self.name == other.name and \
           self.label == other.label and \
           self.age == other.age and \
           self.gender == other.gender and \
           self.language == other.language and \
           self.utterances == other.utterances

  def __ne__(self, other):
    """test for self != other"""
    return not (self == other)


class Field(object):
  """Represents a field (tier) in the annotated resources"""
  
  def __init__(self, fid, name, label, constraint):
    """Creates a field.
         fid is the field's unique ID number.
         name is the field's name.
         label is the field's shorthand label.
         constraint specifies the field's constraint type (seems to be unused).
    """
    super(Field, self).__init__()
    self.fid = fid
    self.name = name
    self.label = label
    self.constraint = constraint
    self.values = dict()
    self.vorder = None
  
  def _add_value(self, vid, name, label=None):
    if self.values.has_key(vid):
      raise DuplicateFieldValue(self.fid, vid)
    self.values[vid] = FieldValue(self, vid=vid, label=label, name=name)
    self.vorder = None
    
  def __unicode__(self):
    return u"Field %s: id %d" % (self.name, self.fid)

  def __getitem__(self, key):
    """Returns a field value by id"""
    return self.values[key]
  
  def get_name(self):
    """Returns the name of the field"""
    return self.name

  def get_label(self):
    """Returns the label of the field"""
    return self.label

  def get_id(self):
    """Returns the id of the field"""
    return self.fid
  
  def get_values(self):
    """Enumerates the standard values of the field ordered
       by ID. Returns an iterable.
    """
    return (self.values[vid] for vid in self._get_value_order())

  def __eq__(self, other):
    """test for self == other"""
    return self.fid == other.fid and \
           self.name == other.name and \
           self.label == other.label and \
           self.constraint == other.constraint and \
           self.values == other.values
  
  def __ne__(self, other):
    """test for self != other"""
    return not (self == other)

  def _get_value_order(self):
    if self.vorder is None:
      self.vorder = self.values.keys()
      self.vorder.sort()
    return self.vorder
  
  
class FieldValue(object):
  """Represents a field value in the annotated resources"""
  
  def __init__(self, field, vid, name, label=None):
    """Creates a field.
         field is the parent field
         vid is the field values's unique ID number (within a containing field)
         name is the values's name.
         label is the value's shorthand label (optional for holds).
    """
    super(FieldValue, self).__init__()
    self.field = field
    self.vid = vid
    self.name = name
    self.label = label
    
  def __unicode__(self):
    return u"Value %s: id %d, belonging to %s" % (self.name, self.vid, unicode(self.field))

  def get_name(self):
    """Returns the name of this field"""
    return self.name
  
  def get_label(self):
    """Returns the label of this field, or None if no label was specified"""
    return self.label
  
  def get_id(self):
    """Returns the id of this field"""
    return self.vid

  def __eq__(self, other):
    """Test for self == other"""
    return self.field.get_id() == other.field.get_id() and \
           self.vid == other.vid and \
           self.name == other.name and \
           self.label == other.label
  
  def __ne_(self, other):
    """Test for self != other"""
    return not (self == other)


class MediaFile(object):
  """Represents a video in the annotated resources"""
  
  def __init__(self, mid, path):
    """Creates a media file.
         mid is the media's unique ID number
         path is the media's path, in legacy sign stream format, with ':' as
         the path separator.
    """
    import macpath
    super(MediaFile, self).__init__()
    self.mid = mid
    self.path = path
    (dir, self.filename) = macpath.split(path)
    
  def __unicode__(self):
    return u"Video %s: id %d" % (self.filename, self.mid)

  def get_id(self):
    """Returns the id of the media"""
    return self.mid
  
  def get_filename(self):
    """Returns the file name of the video, w/o leading path"""
    return self.filename

  def __eq__(self, other):
    """test for self == other"""
    return self.mid == other.mid and \
           self.path == other.path
  
  def __ne__(self, other):
    """test for self != other"""
    return not (self == other)


class Utterance(object):
  """Represents an utterance in the annotated resources.
     NOTE: One utterance per participant only.
     If it contains multiple participants, it must be split into one
     utterance for each respective participant.
  """
  
  def __init__(self, uid, participant, start, end, media):
    """Creates a new utterance.
         uid is the utterance id
         participant is the associated participant
         start is the start of the utterance in ms
         end is the end of the utterance in ms
         media is a list of associated media files
    """
    super(Utterance, self).__init__()
    self.uid = uid
    self.participant = participant
    self.start = start
    self.end = end
    self.media = media
    self.tokens = dict()
    self.torder = None
    
  def __unicode__(self):
    return u"Utterance id %d, with %s" % (self.uid, unicode(self.participant))

  def _add_token(self, field, start, end, vid, text):
    fid = field.get_id()
    if not self.tokens.has_key(fid):
      self.tokens[fid] = []
    self.tokens[fid].append(Token(utterance=self, field=field, start=start,
                                  end=end, vid=vid, text=text))
    self.torder = None
    
  def get_id(self):
    """Returns the id of the utterance"""
    return self.uid
  
  def get_tokens(self):
    """Returns a list of all tokens, ordered by field id"""
    return (self.tokens[fid] for fid in self._get_token_field_order())

  def get_tokens_for_field(self, field):
    """Returns an iterable over all tokens for the given field.
      field can be a field label or numeric id.
    """
    if isinstance(field, basestring):
      # field label
      return self.tokens[self.get_participant().get_db().get_field(field).get_id()]
    else:
      # numeric id
      return self.tokens[field]

  def get_timecodes(self):
    """Returns (start, end) of the utterance in milliseconds"""
    return (self.start, self.end)
  
  def slice(self, fps):
    """Returns an appropriate array slice corresponding to the
       frames that overlap this utterance, based on given
       frame rate.
       Can be used to extract the data frames for this utterance from
       data array.
    """
    return _make_slice(self, fps)
     
  def get_participant(self):
    """Returns the participant of this utterance"""
    return self.participant
  
  def get_media(self):
    """Returns the list of videos belonging to this utterance"""
    return self.media

  def __eq__(self, other):
    """test for self == other"""
    return self.uid == other.uid and \
           self.participant.get_id() == other.participant.get_id() and \
           self.start == other.start and \
           self.end == other.end and \
           self.media == other.media and \
           self.tokens == other.tokens
  
  def __ne__(self, other):
    """test for self != other"""
    return not (self == other)

  def _get_token_field_order(self):
    if self.torder is None:
      self.torder = self.tokens.keys()
      self.torder.sort()
    return self.torder
  

class Token(object):
  """Represents a token uttered by a participant. Can be either
     a standard token, or free-form text.
  """
  
  def __init__(self, utterance, field, start, end, vid, text):
    """Creates a new token.
         utterance is the associated utterance
         field is the field to which the token applies
         start is the start of the token in ms
         end is the end of the token in ms
         vid is the ID of the standard token, or None if free-form
         text is the free-form text of the token
    """
    super(Token, self).__init__()
    (ustart, uend) = utterance.get_timecodes()
    self.utterance = utterance
    self.field = field
    self.start = ustart + start
    self.end = ustart + end
    if vid is not None:
      self.standard_token = field[vid]
      self.text = self.standard_token.get_name()
    else:
      self.standard_token = None
      self.text = text

  def __unicode__(self):
    standard = ""
    if self.standard_token is not None:
      standard = u" (*FID=%d, VID=%d)" % (self.field.get_id(), self.standard_token.get_id())
    return u"%d-%d %s%s in %s" % (self.start, self.end, self.text, standard,
                                  self.field.get_name())
  
  def get_timecodes(self):
    """Returns (start, end) of the token in milliseconds. Note:
       This is an absolute timecode, not relative to the utterance,
       as in the XML file.
    """
    return (self.start, self.end)

  def slice(self, fps):
    """Returns an appropriate array slice corresponding to the
       frames that overlap this token, based on given
       frame rate.
       Can be used to extract the data frames for this token from
       data array.
    """
    return _make_slice(self, fps)
    
  def get_field(self):
    """Returns the field (tier) that the token belongs to."""
    return self.field
    
  def get_text(self):
    """Returns the text of the token. In case of a standard field value,
       returns the text of that field value.
    """
    return self.text
  
  def is_standard(self):
    """Returns true if the token is a standard one, with a listed field
       value (an instance of signstream.dom.FieldValue).
    """
    return self.standard_token is not None
  
  def get_field_value(self):
    """Returns the field value for a standard token, i.e. an instance
       of signstream.dom.FieldValue, raises NonStandardToken
       otherwise.
    """
    if self.is_standard():
      return self.standard_token
    else:
      raise NonStandardToken(self)
  
  def get_utterance(self):
    """Returns the utterance to which the token belongs, e.g. for retrieving
       the media files.
    """
    return self.utterance
  
  def get_coinciding_tokens(self, field):
    """Returns a list of tokens that occur in parallel with this one, for
       a given field. The field can be specified as a numerical id, or
       as a label.
    """
    (start, end) = self.get_timecodes()
    ptokens = []
    try:
      for ptoken in self.get_utterance().get_tokens_for_field(field):
        (pstart, pend) = ptoken.get_timecodes()
        if pstart > end:
          break
        if _overlaps((start, end), (pstart, pend)):
          ptokens.append(ptoken)
    except KeyError:
      # ignore key errors - these occur if a field is valid, but not
      # present in the annotations for this particular utterance
      # that belongs to the token.
      pass
    return ptokens

  def __eq__(self, other):
    """test for self == other"""
    return self.utterance.get_id() == other.utterance.get_id() and \
           self.field.get_id() == other.field.get_id() and \
           self.start == other.start and \
           self.end == other.end and \
           self.standard_token == other.standard_token and \
           self.text == other.text
    
  def __ne__(self, other):
    """test for self != other"""
    return not (self == other)


def _overlaps((s1, e1), (s2, e2)):
  return (s1 >= s2 and s1 < e2) or (e1 > s2 and e1 <= e2)

def _make_slice(obj, fps):
    (start, end) = obj.get_timecodes()
    start = int(round(start / 1000.0 * fps))
    # the end frame is included, whereas python slices exclude it
    end = int(round(end / 1000.0 * fps)) + 1
    return slice(start, end)

# -*- coding: utf-8 -*-
# $Id$

# Functionality for managing, as well as loading and saving a dataset

from __future__ import absolute_import

import xml.sax as sax
import logging

class XMLException(Exception):
  """The base class for all XML parser exceptions. These are caught by some
     content handlers and augmented with line/column information.
  """
  def __init__(self, message):
    super(XMLException, self).__init__(message)
  
class UnexpectedElement(XMLException):
  """Exception that is thrown upon encountering an unexpected element"""
  def __init__(self, tag, stack):
    super(UnexpectedElement, self).__init__("'%s' after '%s'" % (tag, ", ".join(stack)))

class ContentHandlerError(XMLException):
  """Wraps another exception with line/column info"""
  def __init__(self, tag, line, column, exception):
    if line is not None and column is not None:
      if tag is not None:
        message = u"At tag %s, near line %d, column %d: %s: %s" % \
          (tag, line, column, exception.__class__.__name__ , unicode(exception))
      else:
        message = u"Near line %d, column %d: %s: %s" % \
          (line, column, exception.__class__.__name__ , unicode(exception))
    else:
      message = u"%s: %s" % \
        (exception.__class__.__name__ , unicode(exception))
    super(ContentHandlerError, self).__init__(message)
    self.exception = exception
    self.line = line
    self.column = column
    self.tag = tag


class ContentHandlerBase(sax.ContentHandler):
  """Convenience base class for an XML SAX content handler.
     Provides automatic dispatching to methods that handle individual
     elements, of the form "start_<name>" and "end_<name>", and maintains an
     element nesting stack.
     Special characters in elements are converted to "_".
     
     The tag handling functions have the following signature:
       start_<name>(self, attributes)
       end_<name>(self, text) where text is any text that has accumulated since
                              the start of the tag. Note that this messes up
                              mixed content, but we don't need it anyway.
  """
  import re
  _special_chars = re.compile(r"[^A-Za-z0-9_]")
  
  def __init__(self, warn_on_exception=False):
    """If warn_on_exception is true, try to resume parsing, instead of bailing
       out when an error is encountered.
    """
    sax.ContentHandler.__init__(self)
    self.text_stack = None
    self.element_stack = None
    self.locator = None
    self.current_element = None
    self.element_methods = dict() # caches the transformed element names
    self.warn_on_exception = warn_on_exception

  def _method_name(self, name):
    method_name = self.element_methods.get(name, None)
    if method_name is None:
      method_name = self._special_chars.sub("_", name)
      self.element_methods[name] = method_name
    return method_name
  
  def _exception_wrap(self, tag, call_obj, *args, **kw):
    try:
      ret = call_obj(*args, **kw)
    except Exception, e:
      line = None
      column = None
      if self.locator is not None:
        (line, column) = (self.locator.getLineNumber(), self.locator.getColumnNumber())
      e = ContentHandlerError(tag, line, column, e)
      if self.warn_on_exception:
        ret = None
        logging.getLogger("xmlbase").error(unicode(e).encode("utf-8"))
      else:
        raise e
    return ret

  def _call_element(self, is_start, name, *args, **kw):
    if is_start:
      element_type = "start_"
    else:
      element_type = "end_"
    method = getattr(self, element_type + self._method_name(name), None)
    if method is not None:
      method(*args, **kw)
    else:
      if not is_start:
        name = "/" + name
      raise UnexpectedElement(name, self.element_stack)

  def setDocumentLocator(self, locator):
    self.locator = locator
    
  def startDocument(self):
    self.text_stack = [""]
    self.element_stack = []

  def endDocument(self):
    self.text_stack = None
    self.element_stack = None
    
  def startElement(self, name, attrs):
    self.current_element = name
    self._exception_wrap(name, self._call_element, True, name, attrs)
    self.text_stack.append("")
    self.element_stack.append(name)
  
  def endElement(self, name):
    self._exception_wrap(name, self._call_element, False, name,
                         self.text_stack[-1])
    self.text_stack.pop()
    self.element_stack.pop()
    if len(self.element_stack) > 0:
      self.current_element = self.element_stack[-1]
    else:
      self.current_element = None

  def characters(self, text):
    self.text_stack[-1] += text


class ContentHandlerWithDefaults(ContentHandlerBase):
  """Content handler that falls back to a default function if no specialized
     handler function for an element exists.
     If the start_<name> function is missing for some element,
     default_start(self, name, attrs) is called instead; likewise
     default_end(self, name, text) is called for missing end handler
     functions.
     In this class, these two functions are no-ops.
     Of course, subclasses may override these default functions
     as they see fit. 
  """
  def __init__(self, allowed_elements, warn_on_error=False):
    """Constructor. allowed_elements contains the set of allowed tags."""
    ContentHandlerBase.__init__(self, warn_on_error)
    self.allowed_elements = allowed_elements

  # Overrides base class method
  def _call_element(self, is_start, name, *args, **kw):
    if is_start:
      element_type = "start_"
    else:
      element_type = "end_"
    method = getattr(self, element_type + self._method_name(name), None)
    if method is not None:
      method(*args, **kw)
    else:
      if name in self.allowed_elements:
        if is_start:
          self.default_start(name, args[0])
        else:
          self.default_end(name, args[0])
      else:
        if not is_start:
          name = "/" + name
        raise UnexpectedElement(name, self.element_stack)
  
  def default_start(self, name, attrs):
    """Called when an allowed start element has no specialized handler"""
    pass
  
  def default_end(self, name, text):
    """Called when an allowed closing element has no specialized handler"""
    pass
  
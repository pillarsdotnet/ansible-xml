#!/usr/bin/python

import dateutil

class FilterModule(object):

  def filters(self):
    return {
      'assert': self.assert_filter,
      'is_format': self.format_filter,
      'is_datetime': self.datetime_filter,
      'raise': self.raise_filter
    }

  def assert_filter(self, value, logical, message):
    """Provides a Jinja2 function for asserting logical expressions."""
    if not logical:
      self.raise_filter(message, 'Assertion Error')
    return value

  def datetime_filter(self, value, fmt, message):
    """Asserts that a value can be formatted as datetime."""
    try:
      retval=dateutil.parser.parse(value).strftime(fmt)
    except:
      self.raise_filter(message, 'Datetime Error')
    return retval

  def format_filter(self, value, fmt, message):
    """Asserts that a value fits a given format."""
    try:
      retval = value.format(fmt)
    except:
      self.raise_filter(message, 'Format Error')
    return retval

  def raise_filter(self, message, error_type='Error'):
    """Provides a Jinja2 function for raising exceptions."""
    raise Exception('Jinja2 %s: %s' % (error_type, message))

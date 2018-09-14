#!/usr/bin/python

class FilterModule(object):

  def filters(self):
    return {
      'assert': self.assert_filter,
      'raise': self.raise_filter
    }

  def assert_filter(self, value, logical, message):
    """Provides a Jinja2 function for asserting logical expressions."""
    if not logical:
      self.raise_filter(message, 'Assertion Error')
    return value

  def raise_filter(self, message, error_type='Error'):
    """Provides a Jinja2 function for raising exceptions."""
    raise Exception('Jinja2 %s: %s' % (error_type, message))

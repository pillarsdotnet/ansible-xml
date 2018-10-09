#!/usr/bin/python

import dateutil, re, six
from ansible.plugins.filter import core,ipaddr,mathstuff,network,urlsplit

class XmlSchemaError(Exception):
  pass

class XmlValueError(Exception):
  pass

class FilterModule(object):

  def filters(self):
    return {
      'to_xml': self.to_xml,
    }

  def escape_value(self, value):
    return value.replace('&','&amp;')\
                .replace('<','&lt;')\
                .replace('"','&quot;') \
           if isinstance(value, six.string_types) else value

  def is_dict(self, val):
    """Test whether a variable is a dictionary type."""
    return hasattr(val, '__getitem__') \
       and hasattr(val, '__setitem__') \
       and hasattr(val, '__delitem__') \
       and hasattr(val, 'keys')

  def is_empty(self, key, value):
    if key == '_' and not self.is_dict(value):
      value = { key: value }
    return True if not self.is_dict(value) \
      or key not in value \
      or value[key] in (None,'',[]) else False

  def is_required(self, schema):
    """Test whether schema has .required = True."""
    return self.is_dict(schema) \
       and '.required' in schema \
       and schema['.required']

  def is_sequence(self, val):
    """Test whether a variable is an array type."""
    return hasattr(val, '__getitem__') \
       and hasattr(val, '__setitem__') \
       and hasattr(val, '__delitem__') \
       and not hasattr(val, 'keys')

  def get_default(self, schema):
    """Get a default value from schema."""
    return schema[key]['.default'] if hasattr(schema, '.default') else None

  def get_value(self, key, value, schema):
    if key == '_' and not self.is_dict(value):
      value = { key: value }
    return self.get_default(schema) if self.is_empty(key, value) else value[key]

  def to_xml(self, path, key, value, schema, level, spaces):
    """Combines data and schema to produce formatted XML."""
    output = []
    if value is None and not self.is_required(schema):
      return output
    elif self.is_sequence(value):
      for subtag in value:
        output.extend(self.to_xml(path, key, subtag, schema, level, spaces))
      return output
    if isinstance(key, six.string_types):
      key = [key]
    empty = True
    if self.is_dict(schema):
      for optkey in sorted({ k: schema[k] \
          for k in schema if not k.startswith('.')}):
        optval = self.get_value(optkey, value, schema[optkey])
        if ( self.is_empty(optkey, value) or \
             self.get_default(schema[optkey]) == str(optval) \
           ) and not self.is_required(schema[optkey]):
          continue
        if optkey.startswith('+'):
          optval = self.validate(path+'/'+key[0]+optkey, optval, schema[optkey])
          key.append(optkey[1:]+'="'+self.escape_value(optval)+'"')
        elif optkey == '_':
          value = optval
          schema = schema[optkey]
          if not self.is_sequence(value):
            value = [value]
          for subtag in value:
            output.extend(self.to_xml(path, key, subtag, schema, level, spaces))
          return output
        else:
          if empty:
            output.append(' '*level*spaces + '<{}>'.format(' '.join(key)))
            empty = False
          output.extend(self.to_xml(path+'/'+key[0], optkey, optval, \
                                    schema[optkey],level+1, spaces))
      if not empty:
        output.append(' '*level*spaces + '</{}>'.format(key[0]))
      return output
    else:
      if self.is_dict(value):
        value = value['_'] if '_' in value else None
      startkey = ' '*level*spaces + '<{}'.format(' '.join(key))
      if schema is None or value is None:
        output.append(startkey + '/>')
      else:
        value = self.validate(path+'/'+key[0], value, schema)
        value = self.escape_value(value)
        output.append(startkey + '>{}</{}>'.format(value, key[0]))
      return output

  def validate(self, path, value, schema):
    """Raise an error if value is not allowed by schema."""
    if self.is_dict(schema) and '_' in schema:
      schema = schema['_']
    try:
      if isinstance(schema, six.string_types):
        if schema.startswith('%'):
          value = schema.format(value)
        elif schema.startswith('^') and schema.endswith('$'):
          if re.match(schema,str(value)) is None:
            raise XmlValueError
        elif schema[:4] == 'bool':
          match = re.match('^bool(\(([^,]*)(,(.*))?\))?$', schema)
          trueval = 'True' if match.group(2) is None else match.group(2)
          falseval = 'False' if match.group(4) is None else match.group(4)
          value = trueval if core.to_bool(value) else falseval
        elif schema == 'ipaddr':
          value = ipaddr.ipaddr(value)
          if value in (None, False):
            raise XmlValueError
        elif schema == 'ipv4':
          value = ipaddr.ipv4(value)
          if value in (None, False):
            raise XmlValueError
        elif schema == 'ipv6':
          value = ipaddr.ipv6(value)
          if value in (None, False):
            raise XmlValueError
        elif schema[:5] == 'range':
          m = re.match('^range(\(([^,]*)(,([^,]*)(,(.*))?)?\))?$', schema)
          if len(m.group(2)) > 0:
            if float(value) < float(m.group(2)):
              raise XmlValueError
          if len(m.group(4)) > 0:
            if float(value) > float(m.group(4)):
              raise XmlValueError
          if len(m.group(6)) > 0:
            value = m.group(6).format(float(value))
        elif schema[:8] == 'strftime':
          m = re.match('^strftime(\((.*)\))?$', schema)
          datefmt = '%x' if m.group(2) is None else m.group(2)
          value = dateutil.parser.parse(value).strftime(datefmt)
        else:
          raise XmlSchemaError
      elif self.is_sequence(schema):
        if value not in schema:
          raise XmlValueError
      elif schema is None:
        value = None
      else:
        raise XmlSchemaError
    except XmlSchemaError:
      print path + ' has invalid schema: ' + repr(schema)
      raise
    except XmlValueError:
      print path + '=' + repr(value) + ' does not match schema: ' + repr(schema)
      raise
    return value

#!/usr/bin/python

import dateutil, re, six
from ansible.plugins.filter import core,ipaddr,mathstuff,network,urlsplit

class SchemaError(Exception):
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
    """Test whether a variable is a mapping type."""
    return hasattr(val, '__getitem__') \
       and hasattr(val, '__setitem__') \
       and hasattr(val, '__delitem__') \
       and hasattr(val, 'iteritems')

  def is_empty(self, key, value):
    return True if not self.is_dict(value) \
      or key not in value else False

  def is_required(self, schema):
    """Test whether a key is required by schema."""
    return self.is_dict(schema) \
       and '.required' in schema \
       and schema['.required']

  def is_sequence(self, val):
    """Test whether a variable is an array type."""
    return hasattr(val, '__iter__') \
       and hasattr(val, '__next__') \
       and hasattr(val, '__setslice__')

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
    if self.is_sequence(value):
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
        if self.get_default(schema[optkey]) == optval \
           and not self.is_required(schema[optkey]):
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
            output.append(' '*level*spaces + '<%s>'.format(' '.join(key)))
            empty = False
          output.extend(self.to_xml(path+'/'+key[0], optkey, optval, \
                                    schema[optkey],level+1, spaces))
      if not empty:
        output.append(' '*level*spaces + '</%s>'.format(key[0]))
      return output
    else:
      if self.is_dict(value):
        value = value['_'] if '_' in value else None
      startkey = ' '*level*spaces + '<%s'.format(' '.join(key))
      if schema is None or value is None:
        output.append(startkey + '/>')
      else:
        value = self.validate(path+'/'+key[0], value, schema)
        value = self.escape_value(value)
        output.append(startkey + '>%s</%s>'.format(value, key[0]))
      return output

  def validate(self, path, value, schema):
    """Raise an error if value is not allowed by schema."""
    try:
      if isinstance(schema, six.string_types):
        if schema.startswith('%'):
          value = schema.format(value)
        elif schema.startswith('^') and schema.endswith('$'):
          if re.match(schema,value) is None:
            raise
        elif schema[:4] == 'bool':
          match = re.match('^bool(\(([^,]*)(,(.*))?\))?$', schema)
          trueval = 'True' if match.groups(2) is None else match.groups(2)
          falseval = 'False' if match.groups(4) is None else match.groups(4)
          value = trueval if core.to_bool(value) else falseval
        elif schema == 'ipaddr':
          value = ipaddr.ipaddr(value)
          if value is None:
            raise
        elif schema == 'ipv4':
          value = ipaddr.ipv4(value)
          if value is None:
            raise
        elif schema == 'ipv6':
          value = ipaddr.ipv6(value)
          if value is None:
            raise
        elif schema[:5] == 'range':
          m = re.match('^range(\(([^,]*)(,([^,]*)(,(%.*))?)?\))?$', schema)
          if m.group(2) is not None and float(value) < float(m.group(2)) or \
             m.group(4) is not None and float(value) > float(m.group(4)):
             raise
          value = m.group(6).format(float(value)) if m.group(6) is not None else value
        elif schema[:8] == 'strftime':
          m = re.match('^strftime(\((.*)\))?$', schema)
          datefmt = '%x' if m.group(2) is None else m.group(2)
          value = dateutil.parser.parse(value).strftime(datefmt)
        else:
          raise SchemaError
      elif self.is_sequence(schema):
        if value not in schema:
          raise
      elif schema is None:
        value = None
      else:
        raise SchemaError
    except SchemaError:
      print path + ' has invalid schema: ' + repr(schema)
      raise
    except:
      print path + '=' + repr(value) + ' does not match schema: ' + repr(schema)
      raise
    return value

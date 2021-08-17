'''
  Created on Dec 25 2017
  @author: Umesh Chaudhary
'''

import pytz, re, copy, traceback
import json

from datetime import datetime
from bson.objectid import ObjectId
from bson import json_util

import messages
import utils


class Field(object):
  
  _name = None
  _null = False
  _value = None
  _choices = []
  _default = None
  _initial = None
  _required = False
  _parent_class = None

  def __init__(self, **kwargs):
    if 'required' in kwargs:
      assert isinstance(kwargs['required'], bool)
      self._required = kwargs['required']
    if 'default' in kwargs:
      assert 'required' not in kwargs, 'required and default can\'t be set together'
      try:
        self._default = self.get_object(kwargs['default'])
      except Exception as ex:
        raise Exception(
            'invalid default value for the field \'{}\''.format(
                self._name
        ))
    if 'null' in kwargs:
      assert 'required' not in kwargs, 'required and null can\'t be set together'
      assert 'default' not in kwargs, 'default and null can\'t be set together'
      assert isinstance(kwargs['null'], bool)
      self._null = kwargs['null']
    if 'choices' in kwargs:
      assert isinstance(kwargs['choices'], (list, tuple))
      self._choices = kwargs['choices']


  def set_value(self, value=None):
    self._initial = value
    if not value:
      if self._required:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.REQUIRED_FIELD
        )
      self.clear()
      return
    self._value = self.get_object(value)
  
  def get_object(self, value):
    return value

  @property
  def value(self):
    return self._value

  def clear(self):
    if self._null:
      self._value = None
    else:
      self._value = self._default
  
  def serialize(self):
    return self.serialize_object(self.value)
  
  def serialize_object(self, value):
    return value

  def db_repr(self):
    return self.db_object(self.value)
  
  def db_object(self, value):
    return value


class Boolean(Field):
  _default = False

  def get_object(self, value):
    if not isinstance(value, bool):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_BOOLEAN.format(value)
      )
    return value


class DateTime(Field):
  
  _default = utils.now

  def get_object(self, value):
    if not isinstance(value, datetime):
      try:
        value = utils.millis_since_epoch_to_datetime(value)
      except:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.INVALID_DATETIME.format(value)
        )
    return value

  def serialize_object(self, value):
    return utils.datetime_to_millis(value) if value else None

  def clear(self):
    if self._null:
      self._value = None
    else:
      self._value = utils.now()


class String(Field):
  
  _default = ''

  def get_object(self, value):
    if not isinstance(value, (str, unicode)):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_STRING.format(value)
      )
    if self._choices and value not in self._choices:
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_STRING_CHOICE.format(value)
      )
    return value


class Email(String):

  _default = None

  email_regex = re.compile(
      '^[A-Za-z0-9._]{1}[A-Za-z0-9._-]*@[A-Za-z0-9._-]*[A-Za-z0-9._]{1}$')

  def get_object(self, value):
    value = super(Email, self).get_object(value)
    if value is not None and not self.email_regex.match(value):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_EMAIL.format(value)
      )
    return value


class Number(Field):

  _default = 0

  def get_object(self, value):
    if not isinstance(value, (int, float)):
      raise Exception(
        400, messages.VALIDATION_ERROR,
        messages.INVALID_NUMBER.format(value))
    return value


class ObjectID(Field):

  def get_object(self, value):
    if not isinstance(value, ObjectId):
      try:
        value = ObjectId(utils.decode(str(value)))
      except:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.INVALID_OBJECT_ID.format(value)
        )
    return value

  def serialize_object(self, value):
    return utils.encode(str(value)) if value else None


class RelatedField(Field):
  
  _child = None
  _many = False

  def __init__(self, **kwargs):
    assert 'child' in kwargs, "child must be supplied as the first argument"
    self._child = kwargs['child']
    if 'many' in kwargs:
      assert isinstance(kwargs['many'], bool)
      self._many = kwargs['many']
    super(RelatedField, self).__init__(**kwargs)
  
  def set_value(self, value=None):
    self._initial = value
    if not value:
      if self._required:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.REQUIRED_FIELD
        )
      self.clear()
      if self._null:
        return
      value = self._value
    if self._many:
      if not isinstance(value, (list, tuple)):
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.INVALID_STRING_WITH_MANY_TRUE.format(type(value))
        )
      value_list = []
      errors = dict()
      for index, obj in enumerate(value):
        try:
          value_list.append(self.get_object(obj))
        except Exception as ex:
          errors[index] = ex.args[2]
          continue
      if errors:
        raise Exception(400, messages.VALIDATION_ERROR, errors)    
      self._value = value_list
      return
    self._value = self.get_object(value)

  def get_object(self, value):
    obj = copy.copy(self._child)
    obj.set_value(value)
    if obj.__module__ == self.__module__:
      obj = obj.value
    return obj
  
  def clear(self):
    if self._null:
      self._value = None
    elif self._many and not self._default:
      self._value = []
    else:
      self._value = self._default

  def serialize(self):
    if not self._many:
      return self.serialize_object(self.value)
    
    json_dict_list = []
    errors = dict()
    for index, obj in enumerate(self.value):
      try:
        json_dict_list.append(self.serialize_object(obj))
      except Exception as ex:
        print traceback.format_exc()
        errors[index] = ex.args[2]      
      if errors:
        raise Exception(400, messages.VALIDATION_ERROR, errors)

    return json_dict_list

  def serialize_object(self, obj):
    if isinstance(obj, (int, float, str, unicode, bool)):
      return obj
    if isinstance(obj, datetime):
      obj = DateTime()
      obj.set_value(obj)
    if isinstance(obj, ObjectId):
      obj = ObjectID()
      obj.set_value(obj)
    return obj.serialize()

  def db_repr(self):
    if not self._many:
      return self.db_object(self.value)

    db_dict_list = []
    errors = dict()
    for index, obj in enumerate(self.value):
      try:
        db_dict_list.append(self.db_object(obj))
      except Exception as ex:
        print traceback.format_exc()
        errors[index] = ex.args[2]
      if errors:
        raise Exception(400, messages.VALIDATION_ERROR, errors)

    return db_dict_list

  def db_object(self, obj):
    if isinstance(obj, (int, float, str, unicode, bool, datetime, ObjectId)):
      return obj
    return obj.db_repr()


class Dict(dict):

  _name = None
  _null = False
  _value = None
  _initial = None
  _required = False

  def __init__(self, **kwargs):
    if 'required' in kwargs:
      assert isinstance(kwargs['required'], bool)
      self._required = kwargs['required']
    if 'null' in kwargs:
      assert isinstance(kwargs['null'], bool)
      self._null = kwargs['null']
    super(Dict, self).__init__()
  
  def set_value(self, value=dict()):
    self._initial = value
    if not value:
      if self._required:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.REQUIRED_FIELD
        )
      if self._null:
        return
      value = dict()
    if not isinstance(value, dict):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_DATA_FORMAT.format('dict', type(value))
      )
    super(Dict, self).__init__(**value)

  def serialize(self):
    return self

  def db_repr(self):
    return json_util.loads(json.dumps(self))

  @property
  def value(self):
    return self


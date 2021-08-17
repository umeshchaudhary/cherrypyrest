'''
  Created on Dec 25 2017
  @author: Umesh Chaudhary
'''
import copy, traceback
from datetime import datetime
from bson.objectid import ObjectId

import utils
import messages
import managers
import fields


class Model(object):

  exclude_fields = []
  public_fields = []

  # obj fields
  fields = []
  initial_data = dict()

  _null= False
  _value = None
  _required = False

  manager = managers.BaseManager

  def __init__(self, **kwargs):

    for field in self.fields:
      if field is '_id':
        field = 'pk'
      try:
        field_class = getattr(self, field)
        field_class._name = field
      except:
        raise Exception(
            500, messages.SERVER_ERROR,
            messages.INVALID_FIELD_MAPPING.format(
                field, self.__class__.__name__,
                traceback.format_exc()
            )
        )
      field_class._parent_class = self
      setattr(self, '_{}'.format(field), field_class)
    if 'required' in kwargs:
      assert isinstance(kwargs['required'], bool)
      self._required = kwargs['required']
    if 'null' in kwargs:
      assert isinstance(kwargs['null'], bool)
      self._null = kwargs['null']

    self.manager.model = self.__class__

  def _populate_data(self, value):
    if value:
      if not isinstance(value, dict):
        db_id = fields.ObjectID().get_object(value)
        value = self.manager._get_obj(db_id)
    self._populate_fields(value)

  def _populate_fields(self, data):
    if not data:
      data = dict()

    errors = dict()
    if not isinstance(data, dict):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_DATA_FORMAT.format('dict', type(data))
      )
    for field in self.fields:
      if field is '_id':
        field_class = getattr(self, '_pk')
      else:
        field_class = getattr(self, '_{}'.format(field))
      field_class.clear()

      setter = getattr(self, 'set_{}'.format(field), self.set)

      try:
        setter(field, field_class, data.get(field))
      except Exception as ex:
        print ex.args
        import traceback
        print traceback.format_exc()
        # raise
        errors[field] = ex.args[2]
    if errors:
      raise Exception(400, messages.VALIDATION_ERROR, errors)

  def set_value(self, value=None):
    if value and not isinstance(value, dict):
      self.initial_data = {'_id': value}
    else:
      self.initial_data = value or dict()
    if not value:
      if self._required:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.REQUIRED_FIELD
        )
    self._populate_data(value)

  def clear(self):
    for field in self.fields:
      if field is '_id':
        field = 'pk'
      getattr(self, '_{}'.format(field)).clear()

  def set(self, field, field_class, value):
    field_class.set_value(value)
    setattr(self, field, field_class.value)

  def db_repr(self):
    dict_obj = dict()
    for field in self.fields:
      if field is '_id':
        field = 'pk'
      if hasattr(self, 'get_{}'.format(field)):
        dict_obj[field] = getattr(self, 'get_{}'.format(field))()
        continue
      value = getattr(self, field)
      if hasattr(value, 'db_repr'):
        value = value.db_repr()
      elif isinstance(value, (list, tuple)):
        field_class = getattr(self, '_{}'.format(field))
        field_class._value = value
        value = field_class.db_repr()
      dict_obj[field] = value
    if 'pk' in dict_obj:
      dict_obj['_id'] = dict_obj.pop('pk')
    return dict_obj

  def serialize(self):
    dict_obj = dict()
    for field in self.public_fields or self.fields:
      if field is '_id':
        field = 'pk'
      if hasattr(self, 'serialize_{}'.format(field)):
        dict_obj[field] = getattr(self, 'serialize_{}'.format(field))()
        continue
      
      value = getattr(self, field)
      if hasattr(value, 'serialize'):
        value = value.serialize()
      elif isinstance(value, (list, tuple)):
        field_class = getattr(self, '_{}'.format(field))
        field_class._value = value
        value = field_class.serialize()
      dict_obj[field] = value
    if 'pk' in dict_obj:
      dict_obj['_id'] = dict_obj.pop('pk')
    return dict_obj

  @staticmethod
  def check_data_type(attr, data, typ):
    if not isinstance(data, typ):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          {attr: messages.INVALID_DATA_FORMAT.format(
              str(typ), str(type(data)))}
      )

  @staticmethod
  def validate_value(attr, value):
    if value is None or value == '':
      raise Exception(400, messages.VALIDATION_ERROR, {
          attr: messages.REQUIRED_FIELD
      })

  @staticmethod
  def is_valid_value(value):
    if value is None or value == '':
      return False
    return True

  @staticmethod
  def validate_email(attr, email):
    if not utils.EMAIL_REGEX.match(email):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          {attr: messages.INVALID_EMAIL.format(email)}
      )

  def create(self):
    return self.manager.create(self)

  def update(self):
    return self.manager.update(self)





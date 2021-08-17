"""
  Created on Dec 25 2017
  @author: Umesh Chaudhary
"""
from __future__ import absolute_import
from builtins import str
from builtins import object
import traceback

# noinspection Pylint
from . import fields
from . import managers
from . import messages
from . import utils


class Model(object):
  public_fields = []
  read_only_fields = []
  alias = dict()

  # obj fields
  fields = []
  initial_data = dict()
  db_fields = []

  _null = False
  _value = None
  _required = False

  manager = managers.BaseManager()

  def __init__(self, **kwargs):

    self._fields = dict()
    self.db_fields = self.fields
    for field in self.fields:
      if field is '_id':
        field = 'pk'
      try:
        field_class = getattr(self, field)
      except:
        # print traceback.format_exc()
        raise Exception(
            500, messages.SERVER_ERROR,
            messages.INVALID_FIELD_MAPPING.format(
                field, self.__class__.__name__,
                traceback.format_exc()
            )
        )
      field_class.name = field
      field_class.model = self
      self._fields[field] = field_class
      # setattr(self, field, field_class.default)
      setattr(self, '_{}'.format(field), field_class)
    if 'required' in kwargs:
      assert isinstance(kwargs['required'], bool)
      self._required = kwargs['required']
    if 'null' in kwargs:
      assert isinstance(kwargs['null'], bool)
      self._null = kwargs['null']

    self.manager.model = self.__class__

  def _populate_data(self, value, validate=False):
    self.initial_data = value
    self._populate_fields(value, validate=validate)

  def _populate_fields(self, data, validate=False):
    # print 'populating fields', data
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
      setter = getattr(self, 'set_{}'.format(field), self.set)
      value = data.get(field)
      if not value and value != 0:
        value = data.get(self.alias.get(field))

      if isinstance(value, fields.Empty):
        # print 'valie us empty'
        if not validate:
          # print 'validate is false, settings attr to empty'
          setattr(self, field, value)
          # print 'done'
          continue
        value = None

      try:
        if field == '_id':
          field = 'pk'
        setter(field, field_class, value)
      except Exception as ex:
        # print traceback.format_exc()
        errors[self.alias.get(field, field)] = ex.args[2] if len(ex.args) >= 2 else ex.args[0]
    if errors:
      raise Exception(400, messages.VALIDATION_ERROR, errors)

    # Post validation after populating all fields
    self.validate_object()

  def validate_object(self):
    """
      Override this method for post validation of the object
    """
    pass

  def validate(self, value, validate=False):
    _obj = self.__class__()
    _obj.set_value(value, validate=validate)
    return _obj

  def set_value(self, value=None, validate=False):
    if not value:
      if self._required:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.REQUIRED_FIELD
        )
    self._populate_data(value, validate=validate)

  def set(self, field, field_class, value):
    setattr(self, field, field_class.validate(value))

  @property
  def _id(self):
    return self.pk

  def db_repr(self):
    dict_obj = dict()
    for field in self.fields:
      if hasattr(self, 'get_{}'.format(field)):
        dict_obj[field] = getattr(self, 'get_{}'.format(field))()
        continue
      value = getattr(self, field)
      if hasattr(value, 'db_repr'):
        if '_id' in getattr(value, 'fields', []):
          dict_obj[field] = value.pk
          continue
        value = value.db_repr()
      else:
        if field is '_id':
          field_class = getattr(self, '_pk')
        else:
          field_class = getattr(self, '_{}'.format(field))
        if field_class.__module__ == self.__module__:
          value = field_class.db_repr()
        else:
          value = field_class.db_repr(value)
      dict_obj[field] = value
    return dict_obj

  def serialize(self):
    dict_obj = dict()
    for field in self.public_fields or self.fields:
      if hasattr(self, 'serialize_{}'.format(field)):
        dict_obj[self.alias.get(field, field)] = getattr(self, 'serialize_{}'.format(field))()
        continue
      value = getattr(self, field)
      if hasattr(value, 'serialize'):
        if '_id' in getattr(value, 'fields', []):
          dict_obj[field] = value._pk.serialize(value.pk)
          continue
        value = value.serialize()
      else:
        if field is '_id':
          field_class = getattr(self, '_pk')
        else:
          field_class = getattr(self, '_{}'.format(field))
        if field_class.__module__ == self.__module__:
          value = field_class.serialize()
        else:
          value = field_class.serialize(value)
      dict_obj[self.alias.get(field, field)] = value
    return dict_obj

  def validate_db_fields(self):
    self.set_value(self.db_repr(), validate=True)

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
    self.validate_db_fields()
    return self.manager.create(self)

  def update(self):
    self.validate_db_fields()
    return self.manager.update(self)

  def __getattribute__(self, attr):
    value = object.__getattribute__(self, attr)
    if attr not in object.__getattribute__(self, 'db_fields'):
      return value
    if not isinstance(value, fields.Empty):
      return value
    obj_id = object.__getattribute__(self, 'pk')
    obj = object.__getattribute__(self, 'manager')._get_obj(obj_id)
    if not obj:
      field_class = object.__getattribute__(self, '_pk')
      raise Exception(
          400, messages.VALIDATION_ERROR,
          {'_id': messages.INVALID_OBJECT_ID.format(
              field_class.serialize(obj_id)
          )}
      )
    object.__getattribute__(self, 'set_value')(obj)
    return object.__getattribute__(self, attr)

  def __getitem__(self, attr):
    if attr == '_id':
      attr = 'pk'
    return getattr(self, attr)

  def __setitem__(self, key, item):
    self.__dict__[key] = item
    setattr(self, key, item)

  def get(self, attr, default=None):
    return getattr(self, attr, default)

"""
  Created on Dec 25 2017
  @author: Umesh Chaudhary
"""

from builtins import str
from builtins import object
import datetime as datetime_lib
import re

from bson.objectid import ObjectId
from dateutil import parser as dt_parser

from . import messages
from . import utils


class Empty(object):
  _instance = None

  def __new__(cls):
    if cls._instance:
      return cls._instance
    cls._instance = super(Empty, cls).__new__(cls)
    return cls._instance


class Field(object):
  _null_types = (Empty(), None)
  required = False
  null = False
  default = None
  choices = []
  model = None
  name = None

  def _initialize_obj_with_default_values(self):
    self.required = self.__class__.required
    self.null = self.__class__.null
    self.default = self.__class__.default
    self.choices = self.__class__.choices
    self.model = self.__class__.model
    self.name = self.__class__.name

  def __init__(self, required=Empty(), null=Empty(), default=Empty(), choices=Empty(), **kwargs):
    self._initialize_obj_with_default_values()
    if not isinstance(required, Empty):
      assert isinstance(required, bool), 'must be of boolean type'
      self.required = required
    if not isinstance(null, Empty):
      assert isinstance(null, bool), 'must be of boolean type'
      self.null = null
    if not isinstance(choices, Empty):
      assert isinstance(choices, (list, tuple)), 'must be of type list or tuple'
      self.choices = choices
    if not isinstance(default, Empty):
      assert default not in self._null_types, 'can not set null value as a default for the field explicitly'
      self.default = self.validate(default)
    if self.required:
      assert not self.null
      assert not self.default
    if self.null:
      assert not self.required
      assert not self.default
    if self.default:
      assert not self.null
      assert not self.required
    if self.choices and self.default:
      assert self.default in self.choices
    self.__dict__.update(kwargs)

  def get_default_value(self):
    if self.null:
      return None
    return self.default

  def _validate_object(self, value):
    return value

  def validate(self, value=Empty()):
    if value in self._null_types:
      if self.required:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.REQUIRED_FIELD
        )
      return self.get_default_value()
    return self._validate_object(value)

  def set_value(self, value=Empty()):
    return self.validate(value)

  def serialize(self, value):
    if value in self._null_types:
      return self.get_default_value()
    return self._serialize_object(value)

  def _serialize_object(self, value):
    return value

  def db_repr(self, value):
    if value in self._null_types:
      return self.get_default_value()
    return self._db_repr_object(value)

  def _db_repr_object(self, value):
    return value


class Boolean(Field):
  default = False

  def _validate_object(self, value):
    if not isinstance(value, bool):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_BOOLEAN
      )
    return value


class DateTime(Field):
  auto_add = False

  def __init__(self, auto_add=Empty(), required=Empty(), default=Empty(), null=Empty(), **kwargs):
    assert isinstance(default, Empty), 'Default attribute not applicable on datetime field'
    super(DateTime, self).__init__(required=required, default=default, null=null, **kwargs)
    if not isinstance(auto_add, Empty):
      assert isinstance(auto_add, bool)
      assert not self.null
      assert not self.required
      self.auto_add = auto_add

  def _initialize_obj_with_default_values(self):
    super(DateTime, self)._initialize_obj_with_default_values()
    self.auto_add = self.__class__.auto_add

  def _validate_object(self, value):
    if isinstance(value, (str, bytes)):
      try:
        value = dt_parser.parse(value)
      except:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.INVALID_DATETIME
        )
    if isinstance(value, (int, float)):
      try:
        value = utils.millis_since_epoch_to_datetime(value)
      except:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.INVALID_DATETIME
        )
    if not isinstance(value, datetime_lib.datetime):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_DATETIME
      )
    if not value.tzinfo and getattr(self, 'localize', True):
      value = utils.localize(value)
    return value

  def get_default_value(self):
    value = super(DateTime, self).get_default_value()
    if self.auto_add:
      value = utils.now()
    return value

  def _serialize_object(self, value):
    return int(utils.datetime_to_millis(value))


class DateField(Field):

  def _validate_object(self, value):
    if isinstance(value, (str, bytes)):
      try:
        value = dt_parser.parse(value).date()
      except:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.INVALID_DATE
        )
    if isinstance(value, datetime_lib.datetime):
      value = value.date()
    if not isinstance(value, datetime_lib.date):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_DATE
      )
    return value

  def _serialize_object(self, value):
    return value.isoformat()

  def _db_repr_object(self, value):
    return dt_parser.parse(value.isoformat())


class TimeField(Field):

  def _validate_object(self, value):
    if isinstance(value, (str, bytes)):
      try:
        value = dt_parser.parse(value).time()
      except:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.INVALID_TIME
        )
    if isinstance(value, datetime_lib.datetime):
      value = value.time()
    if not isinstance(value, datetime_lib.time):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_TIME
      )
    return value

  def _db_repr_object(self, value):
    return value.isoformat()

  def _serialize_object(self, value):
    return {
        'hours': value.hour,
        'minutes': value.minute,
        'seconds': value.second
    }


class String(Field):
  _null_types = (Empty(), None, '')
  default = ''

  def _initialize_obj_with_default_values(self):
    super(String, self)._initialize_obj_with_default_values()
    self.default = self.__class__.default

  def _validate_object(self, value):
    if not isinstance(value, (str, bytes)):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_STRING
      )
    if isinstance(value, bytes):
      value = value.decode('utf-8')

    value = value.strip()

    if not value:
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.REQUIRED_FIELD
      )
    if self.choices and value not in self.choices:
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_STRING_CHOICE
      )
    return value

  def _serialize_object(self, value):
    if isinstance(value, bytes):
      return value.decode('utf-8')
    return value.strip()

  def _db_repr_object(self, value):
    if isinstance(value, bytes):
      return value.decode('utf-8')
    return value.strip()


class Email(String):

  user_regex = re.compile(
      r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
      r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # quoted-string
      re.IGNORECASE)

  domain_regex = re.compile(
      # max length for domain name labels is 63 characters per RFC 1034
      r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z',
      re.IGNORECASE)

  def _validate_object(self, value):
    if not isinstance(value, (str, bytes)):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_STRING
      )
    if isinstance(value, bytes):
      try:
        value = value.decode('utf-8')
      except Exception as ex:
        raise Exception(
            400,
            messages.VALIDATION_ERROR,
            messages.INVALID_STRING
        )

    value = value.strip()

    if not value:
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.REQUIRED_FIELD
      )
    user_part, domain_part = value.split('@')
    if not self.user_regex.match(user_part) or not self.domain_regex.match(domain_part):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_EMAIL
      )
    return value


class Number(Field):

  def _validate_object(self, value):
    if not isinstance(value, (int, float)):
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_NUMBER)
    if self.choices and value not in self.choices:
      raise Exception(
          400, messages.VALIDATION_ERROR,
          messages.INVALID_STRING_CHOICE
      )
    return value


class ObjectID(Field):
  _null_types = (Empty(), None, '')

  def _validate_object(self, value):
    if not isinstance(value, ObjectId):
      try:
        value = ObjectId(utils.decode(str(value)))
      except:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.INVALID_OBJECT_ID
        )
    return value

  def _serialize_object(self, value):
    return utils.encode(str(value))


class RelatedField(Field):
  _null_types = (Empty(), None, {}, [])

  def __init__(self, child=Empty(), many=Empty(), default=Empty(), choices=Empty(), **kwargs):
    assert isinstance(default, Empty), '`default` attribute not applicable on Related field'
    assert isinstance(choices, Empty), '`choices` attribute not applicable on Related field'
    self.many = False
    assert not isinstance(child, Empty), "`child` must be supplied as a first argument"
    try:
      self.child = utils.import_module(child)
    except Exception as ex:
      raise Exception('Invalid Module suplied as a value for child argument in RelatedField')
    if not isinstance(many, Empty):
      assert isinstance(many, bool)
      self.many = many
    super(RelatedField, self).__init__(**kwargs)

  def get_default_value(self):
    if self.many:
      return []
    return None

  def _validate_object(self, value):
    return self._opr_on_related_object(value, '_validate_related_object')

  def _db_repr_object(self, value):
    return self._opr_on_related_object(value, '_db_repr_related_object')

  def _serialize_object(self, value):
    return self._opr_on_related_object(value, '_serialize_related_object')

  def _validate_related_object(self, value):
    if not isinstance(value, dict) and '_id' in getattr(self.child, 'fields', []):
        obj = self.fake_db_object(getattr(self.child, 'db_fields', []))
        obj['_id'] = ObjectID(required=True).validate(value)
        value = obj
    return self.child.validate(value)

  @staticmethod
  def fake_db_object(db_fields):
    value = dict()
    for field in db_fields:
      value[field] = Empty()
    return value

  def _serialize_related_object(self, obj):
    if self.child.__module__ == self.__module__:
      return self.child.serialize(obj)
    return obj.serialize()

  def _db_repr_related_object(self, obj):
    if self.child.__module__ == self.__module__:
      return self.child.db_repr(obj)
    return obj.db_repr()

  def _opr_on_related_object(self, value, method):
    if not self.many:
      return getattr(self, method)(value)

    objects = list()
    errors = dict()
    for index, obj in enumerate(value):
      try:
        objects.append(getattr(self, method)(obj))
      except Exception as ex:
        errors[index] = ex.args[2] if len(ex.args) >= 2 else ex.args[0]
        continue
    if errors:
      raise Exception(400, messages.VALIDATION_ERROR, errors)
    return objects


class Dict(Field):

  default = dict()

  def __init__(self, **kwargs):
    super(Dict, self).__init__(**kwargs)
    self.default = dict()

  def validate(self, value=Empty()):
    if value in self._null_types:
      if self.required:
        raise Exception(
            400, messages.VALIDATION_ERROR,
            messages.REQUIRED_FIELD
        )
      return dict()
    return self._validate_object(value)

  def _validate_object(self, obj):
    if not isinstance(obj, dict):
      raise Exception(
          400,
          messages.VALIDATION_ERROR,
          messages.INVALID_DATA_FORMAT.format('dict', type(obj))
      )
    return utils.unicode_to_python_obj(obj)

  def _serialize_object(self, value):
    db_dict = value.copy()
    for k, v in list(db_dict.items()):
      if isinstance(v, datetime_lib.datetime):
        db_dict[k] = utils.datetime_to_millis(v)
    return db_dict

"""
  Created on Dec 25 2017
  @author: Umesh Chaudhary
"""
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.utils import old_div
import urllib.request, urllib.parse, urllib.error
import base64
import datetime as datetime_lib
import re
from os import getenv
from threading import Lock
import binascii

import pytz
from Crypto.Cipher import AES
from bson.objectid import ObjectId


# SECRET = None
SECRET = "1234567890123455"
LOCK = Lock()

utc = pytz.UTC


def _init():
  global SECRET

  # idempotent!
  if SECRET is not None:
    return

  f = open("encrypted_pw.txt")
  SECRET = f.readline().strip()
  f.close()


def get_cipher_instance():
  if not SECRET:
    _init()
  return AES.new(SECRET, AES.MODE_ECB)


# def encode(value):
#   cipher = get_cipher_instance()
#   return base64.b64encode(cipher.encrypt(value.rjust(32))).encode('hex')
#
#
# def decode(enc_value):
#   cipher = get_cipher_instance()
#   return cipher.decrypt(base64.b64decode(enc_value.decode('hex'))).strip()

def encode(value):
  cipher = get_cipher_instance()
  return str(binascii.hexlify(base64.b64encode(cipher.encrypt(value.rjust(32)))), 'utf-8')


def decode(enc_value):
  cipher = get_cipher_instance()
  return str(cipher.decrypt(base64.b64decode(binascii.unhexlify(enc_value.encode('utf-8')))).strip(), 'utf-8')


def url(regex, api):
  return re.compile(regex), api


def get_month(dt):
  return str(dt.year) + "-" + str(dt.month)


def localize(dt):
  return utc.localize(dt)


def new_york_alize(dt):
  return get_tzinfo(-4).localize(dt)


epoch = localize(datetime_lib.datetime.utcfromtimestamp(0))
min = localize(datetime_lib.datetime.min)
max = localize(datetime_lib.datetime.max)


def fromtimestamp(timestamp):
  return localize(datetime_lib.datetime.utcfromtimestamp(float(timestamp)))


def millis_since_epoch_to_datetime(millis):
  secs = old_div(millis, 1000)
  return localize(datetime_lib.datetime.utcfromtimestamp(secs))


def now():
  return localize(datetime_lib.datetime.utcnow())


def today():
  return datetime_lib.date.today()


def time(hour, minute):
  return datetime_lib.time(hour, minute)


def date(year, month, day):
  return datetime_lib.date(year, month, day)


def datetime(year, month, day, hour, minute):
  return localize(datetime_lib.datetime(year, month, day, hour, minute))


def datetime_to_unix_timestamp(dt):
  delta = dt - epoch
  return delta.total_seconds()


def date_to_millis(d):
  return datetime_to_millis(localize(datetime_lib.datetime.combine(d, datetime_lib.time())))


def datetime_to_millis(dt):
  return datetime_to_unix_timestamp(dt) * 1000


def datetime_to_mins(dt):
  delta = dt - epoch
  return int(old_div(delta.total_seconds(), 60))


def time_to_mins(t):
  return t.hour * 60 + t.minute


def parse_datetime(string, fmt):
  return localize(datetime_lib.datetime.strptime(string, fmt))


def parse_datetime_without_tz(string, fmt):
  return datetime_lib.datetime.strptime(string, fmt)


def parse_time_zone(tz_string):
  return pytz.timezone(tz_string)


def datetime_to_month_str(dt):
  return datetime_lib.datetime.strftime(dt, "%Y-%m")


def datetime_to_week_str(dt):
  day_of_week = dt.weekday()
  to_beginning_of_week = datetime_lib.timedelta(days=day_of_week)
  beginning_of_week = dt - to_beginning_of_week
  return datetime_lib.datetime.strftime(beginning_of_week, "%Y-%m-%d")


def overlaps(tuple1, tuple2):
  if tuple1[1] <= tuple2[0]:
    return False
  if tuple2[1] <= tuple1[0]:
    return False
  return True


def url(regex, api, kwargs=dict()):
  return re.compile(regex), api, kwargs


def change_timezone(dt_object, time_zone):
  assert dt_object, 'a datetime object is required'
  assert isinstance(dt_object, datetime_lib.datetime), 'invalid datetime object'
  assert time_zone is not None, 'a time_zone object or a string is required'

  if not dt_object.tzinfo:
    dt_object = localize(dt_object)

  if not isinstance(time_zone, datetime_lib.tzinfo):
    time_zone = get_tzinfo(time_zone)

  # convert it into given timezone
  dt_object = dt_object.astimezone(time_zone)
  return dt_object


def get_tzinfo(offset):
  """
    Offset must be in hours
  """
  try:
    return pytz.FixedOffset(float(offset) * 60)
  except:
    return pytz.timezone(offset)


def time(hour, minute):
  return datetime_to_unix_timestamp()


def get_value_from_environment(key):
  value = getenv(key)
  if not value:
    value = None
    # raise Exception('value must be supplied for the key "{}".'.format(key))
  return value


def get_readable_class_name(klass):
  if klass.__class__.__name__ != 'type':
    klass = klass.__class__
  return str(klass).split("'")[1]


def import_module(pkg):
  if not isinstance(pkg, (str, bytes)):
    return pkg
  components = pkg.split('.')
  module = __import__(components[0])
  for comp in components[1:]:
    module = getattr(module, comp)
  return module()


def unicode_to_python_obj(obj):
  """
    Formats the gievn data into valid python objects.
  """
  if isinstance(obj, (list, tuple)):
    temp = []
    for obj in obj:
      temp.append(unicode_to_python_obj(obj))
    return temp
  if not isinstance(obj, dict):
    return decode_obj(obj)
  temp_dict = dict()
  for key, value in list(obj.items()):
    # if isinstance(key, str):
    #   key = key.encode('utf-8')
    if isinstance(value, (list, tuple)):
      temp = []
      for item in value:
        temp.append(unicode_to_python_obj(item))
      temp_dict[key] = temp
      continue
    if isinstance(value, dict):
      temp_dict[key] = unicode_to_python_obj(value)
      continue
    temp_dict[key] = decode_obj(value)
  return temp_dict


def decode_obj(obj):
  # if isinstance(obj, str):
  #   obj = obj.encode('utf-8')
  # if isinstance(obj, str):
  #   obj = urllib.parse.unquote(obj.strip())

  # try to decode as bson object id if possible
  try:
    return ObjectId(decode(obj))
  except Exception as ex:
    pass

  # # try to parse as json if possible
  # try:
  #   obj = json.loads(obj)
  #   return unicode_to_python_obj(obj)
  # except:
  #   pass

  return obj


def format_response(resp):
  """
    Formats the end result into serializable objects.
  """

  if isinstance(resp, (list, tuple)):
    temp = []
    for obj in resp:
      temp.append(format_response(obj))
    return temp
  if not isinstance(resp, dict):
    return encode_obj(resp)

  for key, value in list(resp.items()):
    # if isinstance(key, str):
    #   key = key.encode('utf-8')
    if isinstance(value, (list, tuple)):
      temp = []
      for item in value:
        temp.append(format_response(item))
      resp[key] = temp
    if not isinstance(value, dict):
      resp[key] = encode_obj(value)
    resp[key] = format_response(value)
  return resp


def encode_obj(obj):
  if isinstance(obj, ObjectId):
    return encode(str(obj))
  if isinstance(obj, datetime_lib.datetime):
    return datetime_to_millis(obj)
  if hasattr(obj, 'serialize'):
    return obj.serialize()
  return obj


def unicode_to_str_wrapper(func):
  def wrapper(*args, **kwargs):
    resp = func(*args, **kwargs)
    if not isinstance(resp, (dict, list, tuple)):
      return resp
    return unicode_to_python_obj(resp)
  return wrapper


def is_true(truthy_value):
  if truthy_value in ['true', 'True', True, 1, '1', 'yes', 'Yes', 'Y', 'y']:
    return True
  return False


def is_false(truthy_value):
  if truthy_value in ['false', 'False', False, 0, '0', 'no', 'No', 'N', 'n']:
    return True
  return False


def parse_as_boolean(truthy_value):
  if is_true(truthy_value):
    return True

  if is_false(truthy_value):
    return False
  raise Exception('invalid boolean input')


escape_dict = {'\a': r'\\a',
               '\b': r'\\b',
               '\f': r'\\f',
               '\n': r'\\n',
               '\r': r'\\r',
               '\t': r'\\t',
               '\v': r'\\v',
               '\'': r'\'',
               '\"': r'\"',
               '\0': r'\\0',
               '\1': r'\\1',
               '\2': r'\\2',
               '\3': r'\\3',
               '\4': r'\\4',
               '\5': r'\\5',
               '\6': r'\\6',
               '\7': r'\\7',
               }


def raw(text):
  """Returns a raw string representation of text"""

  new_string = ''
  try:
    text = text.decode('utf-8')
  except:
    pass
  for char in text:
    try:
      new_string += escape_dict[char]
    except KeyError:
      new_string += char
  try:
    new_string = new_string.encode('utf-8')
  except:
    pass
  return new_string.decode('utf-8')

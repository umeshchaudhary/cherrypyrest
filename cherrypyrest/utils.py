"""
  Created on Dec 25 2017
  @author: Umesh Chaudhary
"""
import re
import pytz
import base64
import pymongo
import cherrypy
import simplejson
import datetime as datetime_lib

from Crypto.Cipher import AES
from bson.objectid import ObjectId

# SECRET = None
SECRET = "1234567890123455"

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


def encode(value):
  cipher = get_cipher_instance()
  return base64.b64encode(cipher.encrypt(value.rjust(32))).encode('hex')


def decode(enc_value):
  cipher = get_cipher_instance()
  return cipher.decrypt(base64.b64decode(enc_value.decode('hex'))).strip()


def url(regex, api):
  return re.compile(regex), api


def get_month(dt):
  return str(dt.year) + "-" + str(dt.month)


def localize(dt):
  return utc.localize(dt)


def new_york_alize(dt):
  return pytz.timezone('America/New_York').localize(dt)


epoch = localize(datetime_lib.datetime.utcfromtimestamp(0))
min = localize(datetime_lib.datetime.min)
max = localize(datetime_lib.datetime.max)


def fromtimestamp(timestamp):
  return localize(datetime_lib.datetime.utcfromtimestamp(float(timestamp)))


def millis_since_epoch_to_datetime(millis):
  secs = millis / 1000
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
  return int(delta.total_seconds() / 60)


def time_to_mins(t):
  return t.hour * 60 + t.minute


def parse_datetime(string, fmt):
  return localize(datetime_lib.datetime.strptime(string, fmt))


def parse_time_zone(tz_string):
  return pytz.timezone(tz_string)


def datetime_to_month_str(dt):
  return datetime_lib.datetime.strftime(dt, "%Y-%m")


def datetime_to_week_str(dt):
  day_of_week = dt.weekday()
  to_beginning_of_week = datetime_lib.timedelta(days=day_of_week)
  beginning_of_week = dt - to_beginning_of_week
  return datetime_lib.datetime.strftime(beginning_of_week, "%Y-%m-%d")


def change_timezone(dt, tz_string):
  tz = pytz.timezone(tz_string)
  return dt.astimezone(tz)


def overlaps(tuple1, tuple2):
  if tuple1[1] <= tuple2[0]:
    return False
  if tuple2[1] <= tuple1[0]:
    return False
  return True

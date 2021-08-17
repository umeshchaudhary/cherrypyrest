"""
  Created on Dec 25 2017
  @author: Umesh Chaudhary
"""
from builtins import object
import os
import threading
import mongomock

from collections import defaultdict
# from reschedge_modules.Utils import TEST_DB
# from reschedge_modules.Utils import new_mongo_client
# from settings import DATABASE as DATABASE_NAME

from .utils import unicode_to_str_wrapper


THREAD_POOL = dict()


class BaseManager(object):
  """
    Base class for all managers. Every manager class must be derived from this one.
  """
  _excluded_attrs_from_wrapper = ['db', 'collection', 'client']
  _manager_methods = []

  def __init__(self):
    self._manager_methods = self.__class__._manager_methods
    for key in list(self.__class__.__dict__.keys()):
      if key.startswith('_'):
        continue
      if key in self._excluded_attrs_from_wrapper:
        continue
      if not callable(object.__getattribute__(self, key)):
        continue
      self._manager_methods.append(key)

  @property
  def client(self):
    """
      We need a separate mongo client for every thread otherwise there can be a deadlock issue
      For more information check the link below
      LINK: https://api.mongodb.com/python/current/faq.html#multiprocessing
    """

    _current_thread = threading.currentThread().name
    # Try to find the current active thread in thread pool. If a mongo client object for this
    # thread exists then return that object for thread, or create a new mongo client object
    # for the active thread and push it in the thread pool.
    if _current_thread in THREAD_POOL:
      return THREAD_POOL[_current_thread]

    THREAD_POOL[_current_thread] = {} # new_mongo_client() # you need to create a mongo client EX: MongoClient() in your settings file and import it here
    return THREAD_POOL[_current_thread]

  @property
  def db(self):
    if os.environ.get('APP_ENVIRONMENT', 'DEVELOPMENT') == 'TESTING':
      return mongomock.MongoClient()
    return {} # self.client[DATABASE_NAME]  # you need to create a mongo_lient

  # def new_mongo_client():
  #   return MongoClient(host=EnvironmentVariables.MONGO_CLIENTS, tz_aware=True)

  @property
  def collection(self):
    if not hasattr(self, 'collection_name') or not self.collection_name:
      return None
    return self.db.get_collection(self.collection_name)

  class __metaclass__(type):
    __subclasses__ = defaultdict(dict)

    def __new__(meta, name, bases, dct):
      klass = type.__new__(meta, name, bases, dct)
      for base in klass.mro()[1:-1]:
        meta.__subclasses__[base].update({klass.__name__: klass})
      return klass

  def __getattribute__(self, attr_name):
    attribute = object.__getattribute__(self, attr_name)
    if attr_name not in object.__getattribute__(self, '_manager_methods'):
      return attribute
    try:
      return unicode_to_str_wrapper(attribute)
    except Exception as ex:
      pass
    return attribute

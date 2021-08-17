'''
  Created on Dec 25 2017
  @author: Umesh Chaudhary
'''
from bson.objectid import ObjectId

import messages
import mongo_utils


class BaseManager(object):
  '''
    Base class for all managers. Every manager class must be derived from this one.
  '''

  def __init__(self, *args, **kwargs):
    '''
      Get the db and assign a collection for particular manager class
      A manager class should deal with only one collection that is assigned here.
    '''
    self.db = mongo_utils.get_db(kwargs.get('db'))
    if 'collection' in kwargs:
      self.collection = getattr(self.db, kwargs['collection'])



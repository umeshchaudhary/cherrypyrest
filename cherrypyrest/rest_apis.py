"""
  Created on Dec 25, 2017
  @author: Umesh Chaudhary
"""
from __future__ import print_function
from builtins import str
from builtins import object
import datetime as datetime_lib
import traceback

import cherrypy
import simplejson
from bson.objectid import ObjectId

from . import messages
from .exceptions import APIException
from .utils import decode
from .utils import format_response
from .utils import unicode_to_python_obj


class GenericAPI(object):
  """
    Contains all basic attributes and performs all basic operations required by an api
  """

  service = None
  manager = None
  permissions = []
  serializer = None

  def __init__(self, *args, **kwargs):
    """
      Initialze all api related classes.
    """
    # self.db = kwargs['db']
    if not self.service:
      raise APIException(500, messages.NO_SERVICE_DEFINED)
    self.service = self.service()
    # self.serializer = self.service.serializer
    # self.manager = self.service.manager
    # self.serializer.manager = self.manager

  def default(self, *args, **kwargs):
    """
     Default method executes for every request.
     This is the very first endpoint of request.
     Here all the basic information from  request is extracted.
    """
    method = getattr(self, cherrypy.request.method.upper(), None)
    if not method:
      raise APIException(400, messages.METHOD_NOT_AVAILABLE.format(
          cherrypy.request.method.upper()))
    self.request = cherrypy.request
    self.request.user = cherrypy.request.cookie.get('user')
    self.request.account = cherrypy.request.cookie.get('account')
    self.args = args
    self.kwargs = kwargs
    try:
      kwargs = self.pre_request_validation(*args, **kwargs)
      resp = method(*args, **kwargs)
    except UnicodeEncodeError:
      print('unicode encode error')
      print(traceback.format_exc())
      raise APIException(400, messages.INVALID_INPUT_DATA, data={
          "traceback": traceback.format_exc()
      })
    except UnicodeDecodeError:
      print('unicode decode error')
      print(traceback.format_exc())
      raise APIException(400, messages.INVALID_INPUT_DATA, data={
          "traceback": traceback.format_exc()
      })
    except ValueError as ex:
      print('value error')
      print(traceback.format_exc())
      raise APIException(400, messages.INVALID_DATA.format(str(ex)), {
          "traceback": traceback.format_exc()
      })
    except KeyError as ex:
      print('key error')
      print(traceback.format_exc())
      raise APIException(500, messages.KEY_ERROR.format(str(ex)), {
          "traceback": traceback.format_exc()
      })
    except Exception as ex:
      status_code = 500
      message = 'Internal Server Error. Actual exception was: {}'.format(str(ex))
      data = {'traceback': traceback.format_exc()}
      if len(ex.args) > 0 and isinstance(ex.args[0], int):
        status_code = ex.args[0]
      if len(ex.args) > 1 and isinstance(ex.args[1], (str, str)):
        message = str(ex.args[1])
      if len(ex.args) > 2 and isinstance(ex.args[2], dict):
        data = ex.args[2]
      # else:
      #   data = 
      raise APIException(status_code, message, data=data)
    self.finalize_response(resp)
    format_response(resp)
    return {
        'success': resp.get('success', True) if isinstance(resp, dict) else True,
        'message': resp.get('message', True) if isinstance(resp, dict) else "success",
        'data': resp
    }

  @staticmethod
  def parse_request_data():
    """
      Cherry doesn't provide support for handling content-type application/json' in post
      or put requests. So this method extract data from cherrypy request and  converts it into json.
    """
    try:
      cl = cherrypy.request.headers['Content-Length']
      rawbody = cherrypy.request.body.read(int(cl))
      return simplejson.loads(rawbody)
    except APIException as ex:
      raise APIException(400, messages.INVALID_DATA.format(str(ex)))
    # return cherrypy.request.json

  def get_object_id_from_url(self):
    for obj in self.args:
      try:
        return ObjectId(decode(obj))
      except:
        pass
    return None

  def pre_request_validation(self, *args, **kwargs):
    """
      Performs data validation and permission check before handling request to actual api endpoint.
    """
    self.pk = self.get_object_id_from_url()

    # Excetue all permissions in the controller
    for permission in self.permissions:
      permission(self, *args, **kwargs).has_permission()

    data = dict()
    if cherrypy.request.method.upper() == 'GET':
      return unicode_to_python_obj(kwargs)
      # params = self.serializer.validate_params(kwargs)
    if 'apis/files/' in cherrypy.request.path_info:
      return unicode_to_python_obj(kwargs)
    if cherrypy.request.method.upper() in ['POST', 'PUT']:
      return unicode_to_python_obj(self.parse_request_data())
    return data

  @staticmethod
  def finalize_response(resp):
    """
      Any last minute changes in the response needs to be done here.
    """
    return resp


class ListAPI(GenericAPI):
  """
    Provides functionality for listing of obejcts.
  """
  search_params = []
  sorting = []

  def get_queryset(self, params):
    """
      This method must be implemented in every list API
    """
    raise APIException(
        500, messages.METHOD_NOT_IMPLEMENTED.format('get_queryset'))

  def GET(self, *args, **kwargs):
    """
      performs operations used in getting list of objects
    """
    self.args = args
    return self.get_queryset(kwargs)


class CreateAPI(GenericAPI):
  """
    Object Creation API.
    It contains all the basic attributes and methods required to create a new object.
  """

  def perform_create(self, data):
    """
      This method must be implemented in order to create a new object
    """
    raise APIException(
        500, messages.METHOD_NOT_IMPLEMENTED.format('perform_create'))

  def POST(self, *args, **kwargs):
    """
      Simple POST method handles required steps to be taken while cerating a new object
    """
    return self.perform_create(kwargs)


class RetrieveAPI(GenericAPI):
  """
    This API retrieves an object from the database based on the user permissions
  """

  def get_object(self):
    """
      Need to be implemented in the successor api.
      This simply returns an object that is requested.
      Hint:
        -> Create a subclass of this API and defaine this method.
        -> Create an object permission class in permissions module and validate object id.
        -> If object id is correct then find an object using manager and assign it to the controller.
        -> Return the assigned object from this method.
    """
    if not self.permissions:
      raise APIException(500, 'No Object permission class is defind')
    return self.object

  def GET(self, *args, **kwargs):
    return self.get_object()


class UpdateAPI(GenericAPI):

  def perform_update(self, data):
    """
      This method must be implemented in order to create a new object
    """
    raise APIException(
        500, messages.METHOD_NOT_IMPLEMENTED.format('perform_update'))

  def PUT(self, *args, **kwargs):
    return self.perform_update(kwargs)


class DestroyAPI(GenericAPI):
  """
    Defines methods and attributes rewuired for deleteing an object
  """

  def perform_delete(self, **kwargs):
    """
      This method must be implemented in order to delete an existing object
    """
    raise APIException(
        500, messages.METHOD_NOT_IMPLEMENTED.format('perform_delete'))

  def DELETE(self, *args, **kwargs):
    """
      Checks object level permission classes and deletes an object.
    """
    # if not self.permissions:
    #   raise APIException(500, 'No Object permission class is defind')
    return self.perform_delete(**kwargs)


class RetrieveUpdateAPI(RetrieveAPI, UpdateAPI):
  pass


class RetrieveUpdateDestroyAPI(RetrieveUpdateAPI, DestroyAPI):
  pass


class ListCreateAPI(ListAPI, CreateAPI):
  pass

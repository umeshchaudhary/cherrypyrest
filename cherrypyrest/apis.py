'''
  Created on Dec 25, 2017
  @author: Umesh Chaudhary
'''
import cherrypy
import traceback
import simplejson

from bson.objectid import ObjectId

from . import constants
from .utils import encode
from .rest_exceptions import APIException


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
    self.db = kwargs['db']
    if not self.service:
      raise APIException(500, constants.NO_SERVICE_DEFINED)
    self.service = self.service(self.db)
    # self.serializer = self.service.serializer
    self.manager = self.service.manager
    # self.serializer.manager = self.manager

  @cherrypy.expose
  @cherrypy.tools.json_out()
  def default(self, *args, **kwargs):
    """
     Default method executes for every request.
     This is the very first endpoint of request.
     Here all the basic information from  request is extracted.
    """
    method = getattr(self, cherrypy.request.method.upper(), None)
    if not method:
      raise APIException(400, constants.METHOD_NOT_AVAILABLE.format(
          cherrypy.request.method.upper()))
    self.request = cherrypy.request
    try:
      kwargs = self.pre_request_validation(*args, **kwargs)
      resp = method(*args, **kwargs)
    except UnicodeEncodeError, UnicodeDecodeError:
      raise APIException(400, constants.INVALID_INPUT_DATA)
    except ValueError as ex:
      raise APIException(400, constants.INVALID_DATA.format(ex.message))
    except KeyError as ex:
      print traceback.format_exc()
      raise APIException(500, constants.KEY_ERROR.format(ex.message))
    except Exception as ex:
      status_code = 500
      message = 'Internal Server Error. Actual exception was: {}'.format(
          ex.message)
      data = {}
      if len(ex.args) > 0 and isinstance(ex.args[0], int):
        status_code = ex.args[0]
      if len(ex.args) > 1 and isinstance(ex.args[1], (str, unicode)):
        message = str(ex.args[1])
      if len(ex.args) > 2 and isinstance(ex.args[2], dict):
        data = ex.args[2]
      raise APIException(status_code, message, data=data)
    self.finalize_response(resp)
    self.format_response(resp)
    return {
        'success': True,
        'message': 'success',
        'data': resp
    }

  def parse_request_data(self):
    """
      Cherry doesn't provide support for handling content-type application/json' in post
      or put requests. So this method extract data from cherrypy request and  converts it into json.
    """
    try:
      cl = cherrypy.request.headers['Content-Length']
      rawbody = cherrypy.request.body.read(int(cl))
      return simplejson.loads(rawbody)
    except APIException as ex:
      raise APIException(400, constants.INVALID_DATA.format(ex.message))

  def pre_request_validation(self, *args, **kwargs):
    """
      Performs data validation and permission check before handling request to actual api endpoint.
    """

    # Excetue all permissions in the controller
    for permission in self.permissions:
      permission(self, *args, **kwargs).has_permission()
    if cherrypy.request.method.upper() == 'GET':
      self.format_request(kwargs)
      params = self.serializer.validate_params(kwargs)
    else:
      data = self.parse_request_data()
      self.format_request(data)
      params = self.serializer.validate_data(data)
    return params

  def format_request(self, data):
    """
      Formats the gievn data into valid python objects.
    """
    if isinstance(data, (list, tuple)):
      for obj in data:
        self.format_request(obj)
    if isinstance(data, dict):
      for key, value in data.items():
        if isinstance(value, (list, tuple)):
          for item in value:
            self.format_request(item)
        if isinstance(value, dict):
          self.format_request(value)
        str(value)

  def format_response(self, resp):
    """
      Formats the end result into serializable objects.
    """
    if isinstance(resp, (list, tuple)):
      for obj in resp:
        self.format_response(obj)
    if isinstance(resp, dict):
      for key, value in resp.items():
        if isinstance(value, (list, tuple)):
          for item in value:
            self.format_response(item)
        if isinstance(value, dict):
          self.format_response(value)
        if isinstance(value, ObjectId):
          resp[key] = encode(str(value))

  def finalize_response(self, resp):
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
        500, constants.METHOD_NOT_IMPLEMENTED.format('get_queryset'))

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
        500, constants.METHOD_NOT_IMPLEMENTED.format('perform_create'))

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

  def perfom_update(self, data):
    """
      This method must be implemented in order to create a new object
    """
    raise APIException(
        500, constants.METHOD_NOT_IMPLEMENTED.format('perform_update'))

  def PUT(self, *args, **kwargs):
    return self.perfom_update(kwargs)


class DestroyAPI(GenericAPI):
  """
    Defines methods and attributes rewuired for deleteing an object
  """

  def perform_delete(self, object):
    """
      This method must be implemented in order to delete an existing object
    """
    raise APIException(
        500, constants.METHOD_NOT_IMPLEMENTED.format('perform_delete'))

  def DELETE(self, *args, **kwargs):
    """
      Checks object level permission classes and deletes an object.
    """
    if not self.permissions:
      raise APIException(500, 'No Object permission class is defind')
    return self.perform_delete(self, self.object)


class RetrieveUpdateAPI(RetrieveAPI, UpdateAPI):
  pass


class RetrieveUpdateDestroyAPI(RetrieveUpdateAPI, DestroyAPI):
  pass


class ListCreateAPI(ListAPI, CreateAPI):
  pass

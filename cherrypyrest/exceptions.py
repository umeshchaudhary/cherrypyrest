"""
  Created on Dec 25, 2017
  @author: Umesh Chaudhary
"""
from __future__ import print_function
from builtins import str
import json

import cherrypy


# the below variable will be used to store the error response and will be used to send in so lgger response
ERROR_RESP = dict()


class CustomEncoder(json.JSONEncoder):
  def default(self, obj):
    try:
      return json.JSONEncoder.default(self, obj)
    except:
      pass
    try:
      return str(obj)
    except:
      pass
    return 'NA'


class APIException(cherrypy.HTTPError):

  def __init__(self, status, message, *args, **kwargs):
    super(APIException, self).__init__(status)
    resp = {
        'success': False,
        'message': message,
        'data': kwargs.get('data', {})
    }
    self._api_err_resp = resp

  def set_response(self):
    super(APIException, self).set_response()
    resp = json.dumps(self._api_err_resp, cls=CustomEncoder).encode('utf-8')
    if self.status >= 500:
      ERROR_RESP[id(cherrypy.request)] = resp
      self._api_err_resp = {'success': False, 'message': 'Internal server error'}
    cherrypy.serving.response.body = resp
    cherrypy.response.headers['Content-Type'] = 'application/json'
    cherrypy.response.headers['Content-Length'] = len(json.dumps(self._api_err_resp, cls=CustomEncoder))

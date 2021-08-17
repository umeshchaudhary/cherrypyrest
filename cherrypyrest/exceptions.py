'''
  Created on Dec 25, 2017
  @author: Umesh Chaudhary
'''
import json
import cherrypy

from bson.json_util import default


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
    response = cherrypy.serving.response
    # cherrypy.response.headers['Content-Type'] = 'application/json'
    response.body = json.dumps(self._api_err_resp, default=default)

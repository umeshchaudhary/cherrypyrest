"""
Created on 13 oct 2017
@author:  Umesh Chaudhary
"""

from builtins import object
import json


class BaseSerializer(object):
  """
    BaseSerializer validates request data and performs other basic validations.
  """

  def validate_params(self, params):
    """
      Simply returns the request params without validation.
      Recommands overriding in subclass.
    """
    return params

  def validate_data(self, data):
    """
      Mainly for parsing request body and formating request data. Then pass it to the endpoint
    """
    body = self.parse_data()
    body = json.loads(json.dumps(body), object_hook=self.format_request)
    return body if body else data

  @staticmethod
  def finalize_response(resp):
    """
      Override this method into the subclass of this serializer to perfom
      last time changes in the response before returning to the client.
      Such as format date time object or make a nested object json serializable.
    """
    return resp

"""
  Created on Jan 27 2019
  @author: Umesh Chaudhary
"""

import time
import cherrypy


class TimingTool(cherrypy.Tool):
  def __init__(self):
    cherrypy.Tool.__init__(self, 'before_handler',
                           self.start_timer,
                           priority=1)

  def _setup(self):
    cherrypy.Tool._setup(self)
    cherrypy.request.hooks.attach('before_finalize',
                                  self.end_timer,
                                  priority=5)

  @staticmethod
  def start_timer():
    cherrypy.request._time = time.time()

  @staticmethod
  def end_timer():
    duration = time.time() - cherrypy.request._time
    cherrypy.log("Page handler took %.4f" % duration)


# cherrypy.tools.timeit = TimingTool()

from url import url
import tornado.web
import os
from ui_method.RefreshPlayer import *

class MyApplication(tornado.web.Application):

    PlayerList = {}
    RegisterUser = {}
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'statics'),
        )
        settings['ui_modules']={'ReturnPlayers':ReturnPlayers}

        tornado.web.Application.__init__(self,url,**settings)


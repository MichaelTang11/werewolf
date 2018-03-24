import tornado.web
# from methods.ConnectDb import cursor
import tornado.websocket
from methods.models.Player import Player
import application
from methods.models.GameRoom import GameRoom
import requests

class GetOpenID(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        js_code = self.get_argument('data')
        appid = "wx8d4d470811ec1fa2"
        secret = "44dc0b33fca8f61991a87da71fb37275"
        r = requests.get('https://api.weixin.qq.com/sns/jscode2session?appid='+appid+'&secret='+secret+'&js_code='+js_code+'&grant_type=authorization_code')
        self.write(r.text)

# class DoLogin(tornado.web.RequestHandler):
#     def get(self):
#         self.render('Login.html')
#
#     def post(self):
#         username = self.get_argument('username')
#         password = self.get_argument('password')
#         try:
#             cursor.execute('SELECT * FROM users WHERE `Username`="'+username+'" AND `Password`="'+password+'" ')
#             result=cursor.fetchone()
#             if result is not None:
#                 # if not self.get_cookie('ID') or self.get_cookie('ID')!= str(result[0]):
#                 #      self.set_cookie('ID',str(result[0]))
#                 # else:
#                 #     print(self.get_cookie('ID'))
#                 if result[0] in application.MyApplication.PlayerList.keys():
#                     pass
#                 else:
#                     application.MyApplication.PlayerList[result[0]] = Player(result[0],username)
#                 self.redirect('/Home.html?ID='+str(result[0])+'&UserName='+username)
#                 # self.render('Home.html',ID=result[0],UserName=username)
#             else:
#                 self.render('LoginFail.html')
#         except Exception as e:
#             print(e)
#
# class DoRegister(tornado.web.RequestHandler):
#     def get(self, *args, **kwargs):
#         RegisterUsername=self.get_cookie('RegisterUsername')
#         RegisterPassword=self.get_cookie('RegisterPassword')
#         ConfPassword=self.get_cookie('ConfPassword')
#         self.render('Register.html',RegisterUsername=RegisterUsername,RegisterPassword=RegisterPassword,ConfPassword=ConfPassword)
#
#     def post(self, *args, **kwargs):
#         RegisterUsername = self.get_argument('username')
#         RegisterPassword = self.get_argument('password')
#         ConfPassword = self.get_argument('confPassword')
#         self.set_cookie('RegisterUsername', '')
#         self.set_cookie('RegisterPassword', '')
#         self.set_cookie('ConfPassword', '')
#         if RegisterPassword != ConfPassword:
#             self.set_cookie('RegisterUsername',RegisterUsername)
#             self.render('RegisterFail1.html')
#         else:
#             try:
#                 cursor.execute('select * from Users where Username=' + RegisterUsername)
#                 result = cursor.fetchone()
#                 if result is None:
#                     cursor.execute("insert into users(Username,Password) values('"+RegisterUsername+"','"+RegisterPassword+"')")
#                     self.set_cookie('RegisterUsername', '')
#                     self.set_cookie('RegisterPassword', '')
#                     self.set_cookie('ConfPassword', '')
#                     self.render('RegisterSuccess.html')
#                 else:
#                     self.set_cookie('RegisterPassword', RegisterPassword)
#                     self.set_cookie('ConfPassword', ConfPassword)
#                     self.render('RegisterFail2.html')
#             except Exception as e:
#                 print(e)

class CreateRoom(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        UserID = self.get_argument('ID')
        HostName = self.get_argument('UserName')
        PlayerNumber = self.get_argument('PlayerNumber')
        room=application.MyApplication.PlayerList[int(UserID)].CreateRoom(PlayerNumber)
        PlayerList=room.Players
        self.render('Room.html',UserID=UserID,HostID=UserID,RoomID=room.RoomID,PlayerNumber=PlayerNumber,PlayerList=PlayerList)

class JoinRoom(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        UserID = int(self.get_argument('ID'))
        RoomID = int(self.get_argument('RoomID'))
        print(RoomID)
        application.MyApplication.PlayerList[UserID].JoinRoom(RoomID)
        room=GameRoom.Rooms[RoomID]
        for key in room.Players:
            if key != UserID:
                ws=application.MyApplication.RegisterUser[key]
                ws.write_message('update')
        PlayerList = room.Players
        self.render('Room.html',UserID=UserID,HostID=room.HostID,RoomID=room.RoomID,PlayerNumber=room.PlayerNumber,PlayerList=PlayerList)

class Home(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        ID=self.get_argument('ID')
        UserName=self.get_argument('UserName')
        self.render('Home.html', ID=ID, UserName=UserName)

class CreateConnection(tornado.websocket.WebSocketHandler):
    """创建新的websocket连接"""

    def open(self, *args, **kwargs):
        ID = self.get_argument('ID')
        application.MyApplication.RegisterUser[ID]=self
        print('User %s connected'%ID)


    def on_close(self):
        ID = self.get_argument('ID')
        print('%s disconnected'%ID)
        del application.MyApplication.RegisterUser[ID]
    def on_message(self, message):
        pass

    def check_origin(self, origin):
        return True

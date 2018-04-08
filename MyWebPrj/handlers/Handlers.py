import logging
import uuid
import tornado.web
from methods.ConnectDb import cursor, conn
import tornado.websocket
from methods.models.Player import Player, Player2
import application
from methods.models.GameRoom import GameRoom, GameRoom2
import requests

class GetOpenID(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        js_code = self.get_argument('data')
        appid = "wx8d4d470811ec1fa2"
        secret = "44dc0b33fca8f61991a87da71fb37275"
        r = requests.get('https://api.weixin.qq.com/sns/jscode2session?appid='+appid+'&secret='+secret+'&js_code='+js_code+'&grant_type=authorization_code')
        self.write(r.text)


class CreateRoom(tornado.web.RequestHandler):  # Not Use
    def get(self, *args, **kwargs):
        UserID = self.get_argument('ID')
        HostName = self.get_argument('UserName')
        PlayerNumber = self.get_argument('PlayerNumber')
        room=application.MyApplication.PlayerList[int(UserID)].CreateRoom(PlayerNumber)
        PlayerList=room.Players
        self.render('Room.html',UserID=UserID,HostID=UserID,RoomID=room.RoomID,PlayerNumber=PlayerNumber,PlayerList=PlayerList)


class CreateRoom2(tornado.web.RequestHandler):
    def get(self):
        player_num = self.get_argument("playerNum")
        host_name = self.get_argument("hostName")  # TODO
        logging.warn(player_num)
        cursor.execute("""
          SELECT MAX(id) FROM room
          """)
        max_id = cursor.fetchone()[0] or 0
        next_id = max_id + 1
        cursor.execute("""
          INSERT INTO room(id, player_num) VALUES (?, ?)""",
          (next_id, int(player_num))
        )
        conn.commit()
        # TODO 删hostinstance
        self.write(dict(room_id=next_id))


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


class WaitReady(object):
    def __init__(self, room_id):
        self.room_id = room_id
        self.player_num = -1

    def get_player_num(self):
        cursor.execute("""
          SELECT * FROM room
          WHERE id = ?
          """, (self.room_id, )
        )
        q = cursor.fetchone()
        if q:
            self.player_num = q[1]
        return self.player_num


class CreateConnection(tornado.websocket.WebSocketHandler):
    """
      ret = 0: 房间未满 
      ret = 1: 房间不存在或满了
      ret = 2: 全部的人都进来了
    """
    rooms = {}
    rooms = {}
    current_num = 0

    def current_room(self, room_id, player_num):
        room = self.rooms.get(room_id, None)
        if not room:
            room = GameRoom2(room_id, player_num)
            self.rooms[room_id] = room
        return self.rooms[room_id]

    def open(self):
        logging.warn("Socket is connected")
        room_id = self.get_argument("no")
        player_name = self.get_argument("name")
        player_id = uuid.uuid4()
        self.player_instance = Player2(player_id, player_name)
        #wr = WaitReady(room_id)
        #player_num = wr.get_player_num()
        player_num = 9
        if player_num == -1:
            logging.warn("No player")
            self.write_message(dict(ret=1, msg=u"房间不存在"))
            return
        room = self.current_room(room_id, player_num)
        current_num = room.add_player(self)
        if current_num == -1:
            self.write_message(dict(ret=1, msg=u"房间已满"))
            return
        if current_num < room.player_num:
            for player in room.players:
                player.write_message(dict(ret=0, current_num=current_num))
        if current_num == room.player_num:
            room.give_character()
            for player in room.players:
                character = player.player_instance.character
                player.write_message(dict(ret=2, character=character.name or 'error'))

    def check_origin(self, origin):
        return True


class CreateConnection2(tornado.websocket.WebSocketHandler):  # Not Use
    """创建新的websocket连接"""

    def open(self, *args, **kwargs):
        logging.warn("Socket is connected")
        player_name = self.get_argument("playerName")
        logging.warn("player_name: ", player_name)
        #ID = self.get_argument('ID')
        #application.MyApplication.RegisterUser[ID]=self
        #print('User %s connected'%ID)


    def on_close(self):
        ID = self.get_argument('ID')
        print('%s disconnected'%ID)
        del application.MyApplication.RegisterUser[ID]
    def on_message(self, message):
        pass

    def check_origin(self, origin):
        return True

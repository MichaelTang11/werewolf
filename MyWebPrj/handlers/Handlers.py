import logging
import json
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


class VotePerson(tornado.web.RequestHandler):
    def get(self):
        room_id = self.get_argument("no")
        logging.warn("room_id: %s", room_id)
        uid = self.get_argument("uid")
        logging.warn("uid: %s", uid)
        room = GameRoom2.get_room(room_id)
        player_to_kill = room.get_player(uid)
        player_to_kill.alive = False
        room.dead.append(player_to_kill)
        logging.warn("Dead: %s", room.dead)



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

    def get_attrs(self, attrs, obj_list):
        return [{attr: getattr(obj, attr) for attr in attrs} for obj in obj_list]

    def open(self):
        logging.warn("Socket connected")
        room_id = self.get_argument("no", 1)  # TODO erase 1
        player_name = self.get_argument("name")
        player_id = str(uuid.uuid4())  # TODO usr's id of wechat
        player_instance = Player2(player_id, player_name)
        self.you = player_instance
        #wr = WaitReady(room_id)
        #player_num = wr.get_player_num()
        player_num = 9
        if player_num == -1:
            logging.warn("No player")
            self.write_message(dict(ret=1, msg=u"房间不存在"))
            return
        self.room = self.current_room(room_id, player_num)
        current_num = self.room.add_player(self, player_instance)
        if current_num == -1:
            self.write_message(dict(ret=1, msg=u"房间已满"))
            return
        if current_num < self.room.player_num:
            for player in self.room.players:
                player["sender"].write_message(dict(ret=0, current_num=current_num))
        if current_num == self.room.player_num:
            self.room.give_character()
            wolves = list(self.room.wolves)
            attrs = ["character", "username", "uid"]
            for m in self.room.players:
                m_sender = m["sender"]
                m_player = m["player"]
                your_character = m["player"].character
                your_uid = m["player"].uid
                alive_players = self.room.get_alive_players(self, m_player.if_wolf)
                alive = self.get_attrs(attrs, alive_players)
                send_dict = dict(ret=2, your_character=your_character, your_uid=your_uid, alive=alive)
                if m_player.if_wolf:
                    counterpart = self.get_attrs(attrs, wolves)
                    send_dict["wolves"] = counterpart
                m_sender.write_message(send_dict)

    def change_status(self, msg, character, uid):
        # status = self.room.get_player(uid).alive
        status = self.you.alive
        logging.warn("Alive?: %s", status)
        if status:
            if character == "wolf":
                uid_to_kill = msg["kill"]
                self.room.kill_player(uid_to_kill)
            if character == "witch":
                uid_to_kill = msg["kill"]
                ret_kill = self.room.kill_player(uid_to_kill)
                self.you.char.Poison_Number = 0 if ret_kill else 1
                uid_to_save = msg["save"]
                ret_save = self.room.save_player(uid_to_save)
                self.you.char.Antidote_Number = 0 if ret_save else 1
            if character == "hunter":
                uid_to_kill = msg["kill"]
                if uid_to_kill == 0:
                    pass
                else:
                    ret_kill = self.room.kill_player(uid_to_kill)
                    self.you.char.Hunt = 0 if ret_save else 1
            if character == "all":
                uid_to_vote = msg["vote"]
                self.room.vote_player(uid_to_vote)
                self.you.voted = True
            
    def on_message(self, msg):
        if_wolf = False
        msg = json.loads(msg)
        character = msg["current_character"]
        next_player = msg["ret"]
        uid = msg["uid"]
        self.change_status(msg, character, uid)
        if character == "wolf":
            if_wolf = True
        dead_players = self.room.dead
        all_alive = self.room.get_all_alive()
        all_players = self.room.get_all_players()
        attrs = ["character", "username", "uid", "alive"]
        all_players = self.get_attrs(attrs, all_players)
        dead = self.get_attrs(attrs, dead_players)

        if next_player == "vote":
            alive_num = len(all_alive)
            vote_finish = self.room.vote_finish()
            vote_num = len(vote_finish)
            if vote_num < alive_num:
                for m in self.room.players:
                    m_sender = m["sender"]
                    current_status = m["player"].alive
                    voted = m["player"].voted
                    if voted:
                        m_sender.write_message(dict(ret=5, current_status=current_status, vote_num=vote_num, voted=voted))
            else:
                vote_result =  self.room.vote_caculate()
                for m in self.room.players:
                    m_sender = m["sender"]
                    current_status = m["player"].alive
                    m_sender.write_message(dict(ret=6, vote_result=vote_result))
        elif next_player == "all":
            all_alive_attr = self.get_attrs(attrs, all_alive)
            win = self.room.judge_win()
            for m in self.room.players:
                m_sender = m["sender"]
                current_status = m["player"].alive
                m_sender.write_message(dict(ret=4, all_alive=all_alive_attr, dead=dead, win=win, current_status=current_status))
            self.room.dead = []
        else:
            alive_players = self.room.get_alive_players(self, if_wolf)
            alive = self.get_attrs(attrs, alive_players)
            for m in self.room.players:
                m_sender = m["sender"]
                current_status = m["player"].alive
                player_skill = m["player"].char.__dict__
                m_sender.write_message(dict(ret=3, current_status=current_status, current_character=next_player, alive=alive, dead=dead, all_players=all_players, player_skill=player_skill))

    def on_close(self):


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

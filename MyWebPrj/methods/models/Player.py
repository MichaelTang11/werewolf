from methods.models.GameRoom import GameRoom, GameRoom2
from methods.models.Characters import *


class Player2(object):
    __room_id = 0
    __character = None

    def __init__(self, _id, username):
        self.__id = _id
        self.__username = username

    def create_and_join(self, room_id, player_num):
        room = GameRoom2.get_room(room_id)
        if not room:  # create room
            room = GameRoom2(room_id, player_num)
            self.__room_id = room.room_id
        # join the room
        current_players = room.room_players[room_id]


class Player(object):
    """玩家类"""
    __RoomID = ''
    __Character = None
    def __init__(self,ID,Username):
        self.__ID=ID
        self.__Username=Username

    def CreateRoom(self,PlayerNumber):
        Room=GameRoom(self,PlayerNumber)
        self.__RoomID=Room.RoomID
        return Room

    def JoinRoom(self,RoomID):
        try:
            Room=GameRoom.Rooms[RoomID]
        except Exception:
            return '无该房间号！'
        if len(Room.Players) == Room.PlayerNumber:
            return '房间已满，无法加入！'
        else:
            Room.Players[self.__ID]=self
            self.__RoomID=RoomID
            return '加入成功'

    def GetCharacter(self,character):
        self.__Character=character

    @property
    def ID(self):
        return self.__ID

    @property
    def RoomID(self):
        return self.__RoomID

    @property
    def Character(self):
        return self.__Character

    @property
    def Username(self):
        return self.__Username

    @Character.setter
    def Character(self,Character):
        self.__Character=Character

if __name__ == '__main__':
    player=Player(1,'a')
    room = player.CreateRoom(1)
    character=Witch()
    player.Character=character
    print(character.ReturnMedicineStatus())
    print(room.CheckMedicine())




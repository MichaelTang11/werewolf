import logging
from methods.models.Characters import *
import random


class GameRoom2(object):
    rooms = {}
    room_setting = {9: {'wolf': 3, 'god': 3, 'villager': 3}}

    def __init__(self, room_id, player_num):
        self.room_id = room_id
        self.player_num = player_num
        self.rooms[self.room_id] = self
        self.players = []
        self.wolves = set()
        self.dead = []

    @classmethod
    def get_room(cls, room_id):
        room = cls.rooms.get(room_id, None)
        return room

    def add_player(self, sender, player):
        if len(self.players) < self.player_num:
            self.players.append(dict(sender=sender, player=player))
            return len(self.players)
        else:
            return -1

    def give_character(self):
        characters = []
        characters.append(Witch())
        characters.append(Hunter())
        characters.append(Seer())
        setting = self.room_setting[self.player_num]
        characters.extend([Werewolf() for i in range(setting["wolf"])])
        characters.extend([Villager() for i in range(setting["villager"])])

        for i in range(self.player_num):
            j = random.randint(0, self.player_num-1)
            characters[i], characters[j] = characters[j], characters[i]

        for i in range(self.player_num):
            name = characters[i].name
            self.players[i]["player"].character = name
            self.players[i]["player"].char = characters[i]
            if name == "wolf":
                self.players[i]["player"].if_wolf = True
                self.wolves.add(self.players[i]["player"])

    def get_alive_players(self, sender, if_wolf=False):
        alive_players = set()
        for m in self.players:
            m_sender = m["sender"]
            m_player = m["player"]
            if m_player.alive and sender != m_sender:
                alive_players.add(m_player)
            if if_wolf and sender == m_sender:
                alive_players.add(m_player)
        if if_wolf:
            alive_players -= self.wolves
        return list(alive_players)

    def get_all_alive(self):
        alive_players = []
        for m in self.players:
            m_player = m["player"]
            if m_player.alive:
                alive_players.append(m_player)
        return alive_players

    def kill_player(self, player_id, killer):
        killed = self.get_player(player_id)
        if killed:
            killed.alive = False
            killed.killed_by = killer
            self.dead.append(killed)
            return 1
        else:
            return 0

    def save_player(self, player_id):
        saved = self.get_player(player_id)
        if saved:
            saved.alive = True
            self.dead.remove(saved)
            return 1
        else:
            return 0

    def vote_player(self, player_id):
        player = self.get_player(player_id)
        if player:
            player.vote += 1

    def get_all_players(self):
        all_players = []
        for m in self.players:
            m_player = m["player"]
            all_players.append(m_player)
        return all_players

    def get_player(self, player_id):
        for m in self.players:
            m_player = m["player"]
            if m_player.uid == player_id:
                return m_player
        else:
            return None

    def get_player_by_sender(self, sender):
        for m in self.players:
            if m["sender"] == sender:
                return m["player"]

    def vote_finish(self):
        voted = []
        for m in self.players:
            m_player = m["player"]
            if m_player.voted == True:
                voted.append(m_player)
        return voted

    def get_attrs(self, attrs, obj_list):
        return [{attr: getattr(obj, attr) for attr in attrs} for obj in obj_list]

    def vote_caculate(self):
        target = []
        _max = 0
        players = []
        for m in self.players:
            m_player = m["player"]
            players.append(m_player)
        _max = sorted(players, key=lambda p: p.vote, reverse=True)[0]
        _max = _max.vote
        for m in self.players:
            m_player = m["player"]
            if m_player.vote == _max:
                m_player.alive = False
                m_player.killed_by = "all"
                target.append(m_player)
            m_player.vote = 0
            m_player.voted = False
        attrs = ["character", "username", "uid"]
        target = self.get_attrs(attrs, target)
        return {'get_vote': _max, "target": target}

    def judge_win(self):
        good_dead = 0
        bad_dead = 0
        for m in self.players:
            m_player = m["player"]
            if not m_player.alive:
                if m_player.character == "wolf":
                    bad_dead += 1
                else:
                    good_dead += 1
        if good_dead == 6:
            return 0
        elif bad_dead == 3:
            return 1
        else:
            return 2


class GameRoom(object):  # Not use
    Rooms = {}
    __Players = {}
    __DeadPlayerID = []

    def __init__(self,HostInstance,PlayerNumber):
        RandomNumber=random.randint(1000,9999)
        self.__RoomID=RandomNumber
        self.__HostID=HostInstance.ID
        self.__PlayerNumber=PlayerNumber
        GameRoom.Rooms[RandomNumber]=self
        self.__Players[HostInstance.ID]=HostInstance

    def __str__(self):
        return 'RoomID:' + str(self.__RoomID) + '\n' + 'HostID:' + str(self.__HostID) + '\n' + 'PlayerNumber:' + str(self.__PlayerNumber)

    def CalVote(self):
        """计算投票结果"""
        max = -1
        for player in self.__Players.values():
            if player.Character.Vote_Number >= max:
                max = player.Character.Vote_Number
        SameNumber = 0
        for player in self.__Players.values():
            if player.Character.Vote_Number == max:
                SameNumber += 1
        if SameNumber == 1:
            for player in self.__Players.values():
                if player.Character.Vote_Number == max:
                    return player
        else:
            SameNumberPlayer = []
            for player in self.__Players.values():
                if player.Character.Vote_Number == max:
                    SameNumberPlayer.append(player)
            Length = len(SameNumberPlayer)
            return SameNumberPlayer[random.randint(0, Length - 1)]

    def ClearVoteNumber(self):
        for key in self.__Players:
            self.__Players[key].Character.Vote_Number=0

    def AddPlayer(self,PlayerInstance):
        self.__Players[PlayerInstance.ID]=PlayerInstance

    def GiveCharacter(self):
        if self.PlayerNumber == 9:
            CharacterIndex = []
            for i in range(1,4):
                CharacterIndex.append(Villager())
            for i in range(1,4):
                CharacterIndex.append(Werewolf())
            CharacterIndex.append(Seer())
            CharacterIndex.append(Hunter())
            CharacterIndex.append(Witch())
            players=[]
            for key in self.__Players:
                players.append(self.__Players[key])
            for i in range(0,9):
                RandomNumber=random.randint(0,8-i)
                players[i].Character = CharacterIndex[RandomNumber]
                del CharacterIndex[RandomNumber]

    def GetAllDeath(self):
        AllDeath=[]
        for key in self.__Players:
            if self.__Players.Character.Life == 0:
                AllDeath.append(key)
        return AllDeath

    def GetAllLive(self):
        AllLive = []
        for key in self.__Players:
            if self.__Players[key].Character.Life == 1:
                AllLive.append(key)
        return AllLive

    def JudgeCharacterStatus(self,character):
        for player in self.Players.values():
            if type(player.Character) == character:
                return player.Character.Life

    def CheckMedicine(self):
        for player in self.Players.values():
            if type(player.Character) == Witch:
                return  player.Character.ReturnMedicineStatus()

    def FindCharacter(self,character):
        for player in self.Players.values():
            if type(player.Character) == character:
                return player.Character

    def JudgeWin(self):
        BadDeath = 0
        GoodDeath = 0
        for key in self.Players:
            if self.Players[key].Character.Life == 0:
                for character in Good:
                    if type(self.Players[key].Character) == character:
                        GoodDeath+=1
                        break
                for character in Bad:
                    if type(self.Players[key].Character) == character:
                        BadDeath+=1
                        break
        print(BadDeath)
        print(GoodDeath)
        if BadDeath == 3:
            return '好人获胜'
        if GoodDeath == 6:
            return '狼人获胜'
        return None

    @property
    def RoomID(self):
        return self.__RoomID

    @property
    def Players(self):
        return self.__Players

    @property
    def PlayerNumber(self):
        return self.__PlayerNumber

    @property
    def HostID(self):
        return self.__HostID

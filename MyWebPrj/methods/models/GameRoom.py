from methods.models.Characters import *
import random


class GameRoom(object):
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
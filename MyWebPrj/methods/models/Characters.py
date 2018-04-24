
class Character(object):

    __Vote_Number=0

    @staticmethod
    def FindCharacterByPlayerID(PlayerID,room):
        return room.Players[PlayerID].Character

    @staticmethod
    def Vote(PlayerID,room):
        character=room.Players[PlayerID].Character
        character.Vote_Number += 1

    def __init__(self):
        self.__Life=1

    def FindPlayerID(self,room):
        players=room.Players
        for key in players:
            if players[key].Character == self:
                return key

    @property
    def Vote_Number(self):
        return self.__Vote_Number

    @Vote_Number.setter
    def Vote_Number(self,NewNumber):
        self.__Vote_Number=NewNumber

    @property
    def Life(self):
        return self.__Life

    @Life.setter
    def Life(self,Status):
        self.__Life=Status

class Villager(Character):
    name = "villager"
    pass

class Werewolf(Character):
    name = "wolf"

    @staticmethod
    def KillPerson(PlayerID,room):
        if PlayerID =='':
            pass
        else:
            Character.FindCharacterByPlayerID(PlayerID,room).Life=0

    def FindFriends(self,room):
        FriendID=[]
        players=room.Players
        for key in players:
            if type(players[key].Character) == 'Werewolf':
                if key != self.FindPlayerID(room):
                    FriendID.append(key)
        return FriendID

class Witch(Character):
    name = "witch"

    def __init__(self):
        self.antidote_number = 1
        self.poison_number = 1

    def Save(self,PlayerID, room):
        players = room.Players
        players[PlayerID].Life=1
        self.__Antidote_Number=0

    def Poison(self,PlayerID, room):
        players = room.Players
        players[PlayerID].Character.Life = 0
        self.__Poison_Number=0
        print('毒人成功')

    def ReturnMedicineStatus(self):
        return self.__Antidote_Number,self.__Poison_Number


class Hunter(Character):
    name = "hunter"

    def __init__(self):
        self.hunt = 1

    @staticmethod
    def Shoot(PlayerID, room):
        players = room.Players
        players[PlayerID].Life = 0


class Seer(Character):
    name = "seer"

    @staticmethod
    def Check(PlayerID, room):
        players = room.Players
        Type = type(players[PlayerID].Character)
        for temp in Good:
            if temp == Type:
                return 'Good'
        for temp in Bad:
            if temp == Type:
                return 'Bad'

Good=[
    Villager,
    Seer,
    Witch,
    Hunter
]
Bad = [
    Werewolf
]

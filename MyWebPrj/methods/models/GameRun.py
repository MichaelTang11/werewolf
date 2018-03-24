from methods.models.Player import Player
from methods.models.Characters import *

def main():
    PlayerList = []
    for i in range(0, 9):
        username = input('请输入第%d个玩家的姓名' % (i + 1))
        PlayerList.append(Player(i, username))
    room = PlayerList[0].CreateRoom(9)
    for i in range(1, 9):
        print(PlayerList[i].JoinRoom(room.RoomID))
    room.GiveCharacter()
    for player in room.Players.values():
        print('%d号玩家角色是：%s' % (player.ID, type(player.Character)))
    while True:
        Result = room.JudgeWin()
        if Result is not None:
            print(Result)
            break
        # 晚上
        NightDeath = []
        print('天黑请闭眼')
        input('回车键下一步')
        print('狼人请睁眼')
        input('回车键下一步')
        ID = input('狼人请选择击杀对象')
        if ID != '':
            ID = int(ID)
            NightDeath.append(ID)
        Werewolf.KillPerson(ID, room)
        print('狼人请闭眼')
        input('回车键下一步')
        print('女巫请睁眼')
        input('回车键下一步')
        print('你有一瓶解药是否要使用（若要使用请输入ID）,你有一瓶毒药是否要使用（若要使用请输入ID）')
        if room.JudgeCharacterStatus(Witch) != 0:
            if len(NightDeath) != 0:
                for ID in NightDeath:
                    print('%d死了' % ID)
            Antidote_Number, Poison_Number = room.CheckMedicine()
            choose = ''
            if Antidote_Number != 0:
                choose = input('输入是否要使用解药')
                if choose != '':
                    choose = int(choose)
                    room.FindCharacter(Witch).Save(choose, room)
                    NightDeath.remove(choose)
            if Poison_Number != 0 and choose == '':
                choose = input('输入是否要使用毒药')
                if choose != '':
                    choose = int(choose)
                    room.FindCharacter(Witch).Poison(choose, room)
                    NightDeath.append(choose)
        else:
            input('女巫已死亡请按任意键跳过')
        print('预言家请睁眼')
        input('回车键下一步')
        print('请选择你需要查验的人')
        if room.JudgeCharacterStatus(Seer) != 0:
            choose = int(input('输入ID'))
            print(Seer.Check(choose, room))
        else:
            input('预言家已死亡请按任意键跳过')
        input('回车键下一步')
        # 白天
        DayDeath = []
        if len(NightDeath) == 0:
            print('昨晚是平安夜')
        else:
            print('昨晚死的人是')
            for ID in NightDeath:
                print(ID)
        print('现在开始发言')
        input('回车键下一步')
        players = room.GetAllLive()
        for key in players:
            print('玩家%d请发言' % key)
            input('输入回车结束发言')
        print('请开始投票')
        input('回车键下一步')
        for key in players:
            print('玩家%d请投票' % key)
            ID = input('输入ID选择要投票的玩家')
            if ID != '':
                ID = int(ID)
                Character.Vote(ID, room)
        VotedPlayer = room.CalVote()
        VotedPlayer.Character.Life = 0
        DayDeath.append(VotedPlayer.ID)
        room.ClearVoteNumber()
        for id in NightDeath:
            if type(Character.FindCharacterByPlayerID(id, room)) == Hunter:
                print('猎人玩家%s请选择是否发动技能,如要发动请输入射杀的玩家ID' % room.Players[id].Username)
                id = input('玩家id')
                if id != '':
                    id = int(id)
                    DayDeath.append(id)
                Hunter.Shoot(id, room)
                print('ID:%d玩家死亡' % id)

        for id in DayDeath:
            if type(Character.FindCharacterByPlayerID(id, room)) == Hunter:
                print('猎人玩家%s请选择是否发动技能,如要发动请输入射杀的玩家ID' % room.Players[id].Username)
                id = input('玩家id')
                if id != '':
                    id = int(id)
                    DayDeath.append(id)
                Hunter.Shoot(id, room)
                print('ID:%d玩家死亡' % id)
        input('玩家%s请留遗言,按回车建结束' % VotedPlayer.Username)

if __name__ == '__main__':
    main()
from methods.models.GameRoom import GameRoom

def ReturnPlayers(RoomID):
    return GameRoom.Rooms[RoomID].Players
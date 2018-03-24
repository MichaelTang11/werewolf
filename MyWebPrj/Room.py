Rooms=[]

class ClassRoom(object):
    __number=0
    def Set(self,number):
        self.__number=number

    def Add(self):
        Rooms.append(self)
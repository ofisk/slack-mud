import rooms.trainingroom

globalMap = {}

def build() :
    addRoom(rooms.trainingroom.createTrainingRoom())

def addRoom(room) :
    globalMap[room["id"]] = room

def getRoom(roomId) :
    return globalMap[roomId]
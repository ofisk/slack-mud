import trainingroom

globalMap = {}

def build(sc, mbus, users) :
    addRoom(trainingroom.createTrainingRoom(sc, mbus, users))

def addRoom(room) :
    globalMap[room["id"]] = room

def getRoom(roomId) :
    return globalMap[roomId]
import trainingroom

globalMap = {}

def build(sc) :
    addRoom(trainingroom.createTrainingRoom(sc))

def addRoom(room) :
    globalMap[room["id"]] = room

def getRoom(roomId) :
    return globalMap[roomId]
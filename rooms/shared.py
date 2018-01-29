def createNewRoom(roomId, onEnterFuction, commandMap, roomConnections):
    return {
        "id": roomId,
        "onEnter": onEnterFuction,
        "commandMap": commandMap,
        "roomConnections": roomConnections
    }
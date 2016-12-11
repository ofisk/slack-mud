import os
import time
import re
from slackclient import SlackClient

ADMIN_USER = 'U10F84U2J'
TARGET_CHANNEL = 'C3D4EAVGS'

slack_token = os.environ["SLACK_BOT_TOKEN"]
sc = SlackClient(slack_token)
users = {}
globalMap = {}

TRAINING_ROOM_ID = "trainingroom"
TRAINING_COMPLETE_ROOM_ID = "trainingcompleteroom"
RACES = {
    "dragonborn": {
        "title": "Dragonborn",
        "description": ""
    },
    "dwarf": {
        "title": "Dwarf",
        "description": ""
    },
    "eladrin": {
        "title": "Eladrin",
        "description": ""
    },
    "elf": {
        "title": "Elf",
        "description": ""
    },
    "gnome": {
        "title": "Gnome",
        "description": ""
    },
    "half-elf": {
        "title": "Half-Elf",
        "description": ""
    },
    "half-orc": {
        "title": "Half-Orc",
        "description": ""
    },
    "halfling": {
        "title": "Halfling",
        "description": ""
    },
    "human": {
        "title": "Human",
        "description": ""
    },
    "tiefling": {
        "title": "Tiefling",
        "description": ""
    }
}

def handleReset() :
    users = {}

def createNewRoom(roomId, onEnterFuction, commandMap, roomConnections) :
    globalMap[roomId] = {
        "id": roomId,
        "onEnter": onEnterFuction,
        "commandMap": commandMap,
        "roomConnections": roomConnections
    }
    return globalMap[roomId]

def tryCommandInRoom(roomId, command, user) :
    room = globalMap[roomId]
    print room
    if command in room["commandMap"].keys() :
        room["commandMap"][command](user)
    else :
        sc.api_call(
            "chat.postMessage",
            channel="#slackmud",
            text="""
                %s was unable to perform action '%s' in this room.
            """ % (user['name'], command)
        )

def tryMovementFromRoom(roomId, command, user) :
    room = globalMap[roomId]
    goPattern = re.compile("go *")
    print room
    if goPattern.match(command) :
        command = command.split("go ")[1]
    if command in room["roomConnections"].keys() :
        globalMap[room["roomConnections"][command]]["onEnter"](user)
    else :
        sc.api_call(
            "chat.postMessage",
            channel="#slackmud",
            text="""
                %s tried to go %s but ran into a wall like a dipshit.
            """ % (user['name'], command)
        )

def createTrainingRoom() :
    def trainingRoomOnEnter(user) :
        user["currentRoomId"] = TRAINING_ROOM_ID
        sc.api_call(
            "chat.postMessage",
            channel="#slackmud",
            text="""
                You enter a circular room, almost completely empty except for a fountain in the center of the room.
                A door to the north is visible but seems to be sealed shut, currently.  A voice from nowhere and 
                everywhere beckons you forward, "%s, peer into the Fountain to begin your journey."
            """ % (user["name"])
        )
    def trainingCompleteRoomOnEnter(user) :
        user["currentRoomId"] = TRAINING_COMPLETE_ROOM_ID
        sc.api_call(
            "chat.postMessage",
            channel="#slackmud",
            text="""
                The voice returns again to congratulate you for completing your training:
                "Congratulations, %s.  You have now completed your introduction to this world.
                Ahead of you lies adventure, glory, and gold.  Oh wait, nevermind.  Oren hasn't
                built this part yet.  I guess you just have to stand here now.  Alright... well...
                Bye, I guess.
                ...
                Also, fuck York.
            """ % (user["name"])
        )
    def beginTrainingQuiz(user) :
        sc.api_call(
            "chat.postMessage",
            channel="#slackmud",
            text="""
                Training Quiz:  Are you a fuckboy?
            """
        )
        sc.api_call(
            "chat.postMessage",
            channel="#slackmud",
            text="""
                Just kidding, I don't care at all.
                Alright, now type 'go north', 'north' or 'n' to move to the next room (it's north of this one, in case you're a dipshit).
            """
        )

    trainingCompleteRoomConnections = {"s": TRAINING_ROOM_ID, "south": TRAINING_ROOM_ID}
    trainingCompleteRoom = createNewRoom(TRAINING_COMPLETE_ROOM_ID, trainingCompleteRoomOnEnter, None, trainingCompleteRoomConnections)
    commandMap = {
        "look at fountain": beginTrainingQuiz, 
        "look at the fountain": beginTrainingQuiz, 
        "look into fountain": beginTrainingQuiz, 
        "look into the fountain": beginTrainingQuiz, 
        "peer into fountain": beginTrainingQuiz, 
        "peer into the fountain": beginTrainingQuiz
    }

    return createNewRoom(TRAINING_ROOM_ID, trainingRoomOnEnter, commandMap, {"n": TRAINING_COMPLETE_ROOM_ID, "north": TRAINING_COMPLETE_ROOM_ID})

def buildGlobalMap() :
    globalMap[TRAINING_ROOM_ID] = createTrainingRoom()

def handleJoin(userId) :
    users[userId] = {"reset": True}
    sc.api_call(
        "chat.postMessage",
        channel="#slackmud",
        text="""
            Welcome to Slack MUD.  An interactive Multi User Dungeon, built in Slack.  
            To play, just communicate with the game by commands like '@slackmud <action>'. 
            Before we start though, let's get some basic information on your character.  
            First off, what is your name?
            """
    )

def handleNameResetForUser(userId) :
    handleJoin(userId)

def handleWelcomeOfNewUser(userId, name) :
    users[userId] = {"id": userId, "name": name, "currentRoomId": TRAINING_ROOM_ID, "reset": False}
    sc.api_call(
        "chat.postMessage",
        channel="#slackmud",
        text="Welcome " + users[userId]["name"] + "! If you don't like your character, type '@slackmud reset character' to reset (your whole character will get reset)."
    )
    globalMap[TRAINING_ROOM_ID]["onEnter"](users[userId])

if sc.rtm_connect():
    buildGlobalMap()
    while True:
        messageRaw = sc.rtm_read()
        print messageRaw
        message = None
        userId = None
        channel = None
        messageType = None
        if (len(messageRaw) > 0) :
            channel = messageRaw[0].get('channel', None)
            message = messageRaw[0].get('text', None)
            userId = messageRaw[0].get('user', None)
            messageType = messageRaw[0].get('type', None)
        if (TARGET_CHANNEL != channel or messageType != "message") :
            continue
        if (message == '@slackmud join') :
            handleJoin(userId)
        elif (users.get(userId, None) == None) :
            continue
        elif (message == '@slackmud reset world' and userId == ADMIN_USER) :
            handleReset()
        elif (message == '@slackmud reset character') :
            handleNameResetForUser(userId)
        elif (message == 'n' or message == 'north' or message == 'go north' or
            message == 'e' or message == 'east' or message == 'go east' or
            message == 's' or message == 'south' or message == 'go south' or
            message == 'w' or message == 'west' or message == 'go west') :
            tryMovementFromRoom(user["currentRoomId"], message, user)
        elif (userId != None and users[userId]["reset"]) :
            handleWelcomeOfNewUser(userId, message)
        elif (message != None and userId != None) :
            user = users[userId]
            tryCommandInRoom(user["currentRoomId"], message, user)
        time.sleep(1)
else:
    print "Connection Failed, invalid token?"
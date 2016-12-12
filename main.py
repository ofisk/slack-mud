import os
import time
import re
import rooms.globalmap
import character.races
from slackclient import SlackClient

ADMIN_USER = 'U10F84U2J'
TARGET_CHANNEL = 'C3D4EAVGS'

slack_token = os.environ["SLACK_BOT_TOKEN"]
sc = SlackClient(slack_token)
users = {}

def handleReset() :
    users = {}
    sc.api_call(
        "chat.postMessage",
        channel="#slackmud",
        text="Resetting the world."
    )

def tryCommandInRoom(roomId, command, user) :
    room = rooms.globalmap.getRoom(roomId)
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
    room = rooms.globalmap.getRoom(roomId)
    goPattern = re.compile("go *")
    print room
    if goPattern.match(command) :
        command = command.split("go ")[1]
    if command in room["roomConnections"].keys() :
        rooms.globalmap.getRoom(room["roomConnections"][command])["onEnter"](user)
    else :
        sc.api_call(
            "chat.postMessage",
            channel="#slackmud",
            text="""
                %s tried to go %s but ran into a wall like a dipshit.
            """ % (user['name'], command)
        )

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
    users[userId] = {"id": userId, "name": name, "currentRoomId": rooms.roomids.TRAINING_ROOM_ID, "reset": False}
    sc.api_call(
        "chat.postMessage",
        channel="#slackmud",
        text="Welcome " + users[userId]["name"] + "! If you don't like your character, type '@slackmud reset character' to reset (your whole character will get reset)."
    )
    rooms.globalmap.getRoom(rooms.roomids.TRAINING_ROOM_ID)["onEnter"](users[userId])

if sc.rtm_connect():
    rooms.globalmap.build(sc)
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
        elif (message == '@slackmud reset world' and userId == ADMIN_USER) :
            handleReset()
        if (message == '@slackmud join') :
            handleJoin(userId)
        elif (users.get(userId, None) == None) :
            continue
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
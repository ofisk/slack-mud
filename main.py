import os
import time
import re
import rooms.globalmap
import character.races
from slackclient import SlackClient
from messaging.messagebus import MessageBus

TARGET_CHANNEL = 'C3D4EAVGS'

slack_token = os.environ["SLACK_BOT_TOKEN"]
sc = SlackClient(slack_token)
users = {}
mbus = MessageBus()

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
    newUser = {"id": userId, "reset": True}
    users[userId] = newUser
    mbus.registerUser(newUser)
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
    mbus.registerCommandForUser(newUser, handleWelcomeOfNewUser)

def handleNameResetForUser(userId) :
    handleJoin(userId)

def handleWelcomeOfNewUser(user, name) :
    users[user["id"]] = {"id": user["id"], "name": name, "currentRoomId": rooms.roomids.TRAINING_ROOM_ID, "reset": False}
    mbus.registerUser(users[user["id"]])
    sc.api_call(
        "chat.postMessage",
        channel="#slackmud",
        text="Welcome " + users[user["id"]]["name"] + "! If you don't like your character, type '@slackmud reset character' to reset (your whole character will get reset)."
    )
    rooms.globalmap.getRoom(rooms.roomids.TRAINING_ROOM_ID)["onEnter"](users[user["id"]])

def handleDescribeRace(userId) :
    user = users[userId]
    def handleDescribeSpecificRace(user, race) :
        if (character.races.PLAYABLE_RACES.get(race, None) == None) :
            sc.api_call(
                "chat.postMessage",
                channel="#slackmud",
                text="I'm sorry, I don't recognize that race."
            )
        sc.api_call(
            "chat.postMessage",
            channel="#slackmud",
            text="{0}: {1}".format(race, character.races.PLAYABLE_RACES[race]["description"])
        ) 
    sc.api_call(
        "chat.postMessage",
        channel="#slackmud",
        text="Which race would you like me to describe?"
    )
    mbus.registerCommandForUser(user, handleDescribeSpecificRace)

mbus.registerAdminCommand('@slackmud reset world', handleReset)
mbus.registerGlobalCommand('@slackmud join', handleJoin)
mbus.registerGlobalCommand('@slackmud describe race', handleDescribeRace)
if sc.rtm_connect():
    rooms.globalmap.build(sc, mbus, users)
    while True:
        message = None
        userId = None
        channel = None
        messageType = None

        rawMessages = sc.rtm_read()
        
        if (len(rawMessages) > 0) :
            for rawMessage in rawMessages :
                print "Processing message: ", rawMessage
                channel = rawMessage.get('channel', None)
                message = rawMessage.get('text', None)
                userId = rawMessage.get('user', None)
                messageType = rawMessage.get('type', None)

                if (TARGET_CHANNEL != channel or messageType != "message") :
                    continue
                if (message == '@slackmud reset character') :
                    handleNameResetForUser(userId)
                elif (message == 'n' or message == 'north' or message == 'go north' or
                    message == 'e' or message == 'east' or message == 'go east' or
                    message == 's' or message == 'south' or message == 'go south' or
                    message == 'w' or message == 'west' or message == 'go west') :
                    tryMovementFromRoom(user["currentRoomId"], message, user)
                result = mbus.handleMessage(rawMessage)
                if (result == "COMMAND_NOT_FOUND") :
                    user = users[userId]
                    tryCommandInRoom(user["currentRoomId"], message, user)
        time.sleep(1)
else:
    print "Connection Failed, invalid token?"
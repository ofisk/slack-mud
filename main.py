import os
import time
import re
import rooms.globalmap
import character.races
import character.classes
from slackclient import SlackClient
from messaging.messagebus import MessageBus

TARGET_CHANNEL = 'C3D4EAVGS'
DIRECT_CHANNEL = 'foo'

slack_token = os.environ["SLACK_BOT_TOKEN"]
sc = SlackClient(slack_token)
users = {}
mbus = MessageBus(sc)

def handleReset():
    users = {}
    mbus.postMessageToParty("Resetting the world.")
    if len(users.keys()) == 0:
        mbus.postMessageToParty("No users detected.  Type '@slackmud join' to create a new user via direct message.")

def tryCommandInRoom(roomId, command, user):
    room = rooms.globalmap.getRoom(roomId)
    if command in room["commandMap"].keys():
        room["commandMap"][command](user)
    else:
        mbus.postMessageToParty("""%s tried to '%s' but was unsuccessful.""" % (user['name'], command))

def tryMovementFromRoom(roomId, command, user):
    room = rooms.globalmap.getRoom(roomId)
    goPattern = re.compile("go *")
    if goPattern.match(command):
        command = command.split("go ")[1]
    if command in room["roomConnections"].keys():
        rooms.globalmap.getRoom(room["roomConnections"][command])["onEnter"](user)
    else:
        mbus.postMessageToParty("""%s tried to go %s but was unable to go that direction.""" % (user['name'], command))

def handleJoin(userId):
    newUser = {"id": userId, "reset": True}
    users[userId] = newUser
    mbus.registerUser(newUser)
    mbus.postMessageToParty("""
            Welcome to Slack MUD.  An interactive Multi User Dungeon, built in Slack.  
            To play, just communicate with the game by commands like '@slackmud <action>'. 
            Before we start though, let's get some basic information on your character.  
            First off, what is your name?
            """
    )
    mbus.registerCommandForUser(newUser, handleWelcomeOfNewUser)

def handleCharacterResetForUser(userId):
    handleJoin(userId)

def handleWelcomeOfNewUser(user, name):
    userId = user["id"]
    users[userId] = {"id": userId, "name": name, "currentRoomId": rooms.roomids.TRAINING_ROOM_ID, "reset": False}
    user = users[userId]
    mbus.registerUser(user)
    mbus.postMessageToParty("Welcome %s! If you don't like your character, type '@slackmud reset character' to reset (your whole character will get reset)." % (user["name"]))
    rooms.globalmap.getRoom(rooms.roomids.TRAINING_ROOM_ID)["onEnter"](user)

def handleDescribeRace(userId):
    user = users[userId]
    def handleDescribeSpecificRace(user, race):
        if (character.races.PLAYABLE_RACES.get(race, None) == None):
            mbus.postMessageToUser(user, "I'm sorry, I don't recognize that race.")
        mbus.postMessageToUser(user, "{0}: {1}".format(race, character.races.PLAYABLE_RACES[race]["description"])) 
    mbus.postMessageToUser(user, "Which race would you like me to describe?")
    mbus.registerCommandForUser(user, handleDescribeSpecificRace)

def handleDescribeClass(userId):
    user = users[userId]
    def handleDescribeSpecificClass(user, playableclass):
        if (character.classes.PLAYABLE_CLASSES.get(playableclass, None) == None):
            mbus.postMessageToUser(user, "I'm sorry, I don't recognize that class.")
        mbus.postMessageToUser(user, "{0}: {1}".format(playableclass, character.classes.PLAYABLE_CLASSES[playableclass]["description"])) 
    mbus.postMessageToUser(user, "Which class would you like me to describe?")
    mbus.registerCommandForUser(user, handleDescribeSpecificClass)

mbus.registerAdminCommand('@slackmud reset world', handleReset)
mbus.registerGlobalCommand('@slackmud join', handleJoin)
mbus.registerGlobalCommand('@slackmud describe race', handleDescribeRace)
mbus.registerGlobalCommand('@slackmud describe class', handleDescribeClass)

if sc.rtm_connect():
    rooms.globalmap.build(sc, mbus, users)
    while True:
        message = None
        userId = None
        channel = None
        messageType = None

        rawMessages = sc.rtm_read()
        
        if (len(rawMessages) > 0):
            for rawMessage in rawMessages:
                print "Processing message: ", rawMessage
                channel = rawMessage.get('channel', None)
                message = rawMessage.get('text', None)
                if message != None:
                    message = message.lower()
                userId = rawMessage.get('user', None)
                messageType = rawMessage.get('type', None)
                print channel, TARGET_CHANNEL, DIRECT_CHANNEL, not(TARGET_CHANNEL == channel or DIRECT_CHANNEL == channel)
                if (not(TARGET_CHANNEL == channel or DIRECT_CHANNEL == channel) or messageType != "message"):
                    continue
                if (message == '@slackmud reset character'):
                    handleCharacterResetForUser(userId)
                elif (message == 'n' or message == 'north' or message == 'go north' or
                    message == 'e' or message == 'east' or message == 'go east' or
                    message == 's' or message == 'south' or message == 'go south' or
                    message == 'w' or message == 'west' or message == 'go west'):
                    tryMovementFromRoom(user["currentRoomId"], message, user)
                result = mbus.handleMessage(rawMessage)
                if (result == "COMMAND_NOT_FOUND"):
                    user = users[userId]
                    tryCommandInRoom(user["currentRoomId"], message, user)
        time.sleep(1)
else:
    print "Connection Failed, invalid token?"
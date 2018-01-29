ADMIN_USER = 'U10F84U2J'
DEFAULT_CHAT_CHANNEL = "#slakmud" #TODO: make this configurable

class MessageBus:
    adminCommands = None
    pendingCommandsByUser = None
    registeredUsers = None
    globalCommands = None
    sc = None

    def __init__(self, slackClient):
        self.globalCommands = {}
        self.adminCommands = {}
        self.pendingCommandsByUser = {}
        self.registeredUsers = {}
        self.sc = slackClient

    def handleMessage(self, rawMessage):
        message = None
        userId = None
        channel = None
        messageType = None

        if (len(rawMessage) > 0):
            channel = rawMessage.get('channel', None)
            message = rawMessage.get('text', None)
            userId = rawMessage.get('user', None)
            messageType = rawMessage.get('type', None)
        if (userId == None):
            return

        targetUser = self.registeredUsers.get(userId, None)
        if (self.adminCommands.get(message, None) != None and userId == ADMIN_USER):
            self.adminCommands[message]()
            return
        elif (self.registeredUsers.get(userId, None) == None or message.startswith("@slackmud")):
            if (self.globalCommands.get(message, None) != None):
                self.globalCommands[message](userId)
                return
        pendingCommands = self.pendingCommandsByUser.get(userId, None)
        if (pendingCommands == None or len(pendingCommands) == 0):
            return "COMMAND_NOT_FOUND"
        pendingCommand = pendingCommands.pop() #TODO: Maybe add a message print callback for the message that's now on the top of the stack?
        self.pendingCommandsByUser[userId] = pendingCommands
        pendingCommand(targetUser, message)

    def registerAdminCommand(self, message, command):
        self.adminCommands[message] = command

    def registerGlobalCommand(self, message, command):
        self.globalCommands[message] = command

    def registerUser(self, user):
        self.registeredUsers[user["id"]] = user

    def registerCommandForUser(self, user, command):
        if (self.pendingCommandsByUser.get(user["id"], None) == None):
            self.pendingCommandsByUser[user["id"]] = []
        self.pendingCommandsByUser[user["id"]].append(command)

    def postMessageToChannel(self, channel, message):
        self.sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=message
        )

    def postMessageToParty(self, message):
        self.postMessageToChannel(DEFAULT_CHAT_CHANNEL, message)

    def postMessageToUser(self, user, message):
        channel = self.findIMChannelByUserId(user["id"])
        self.postMessageToChannel(channel, message)

    def findIMChannelByUserId(self, userId):
        response = self.sc.api_call(
            "im.list"
        )
        print response
        for im in response["ims"]:
            if im["user"] == userId and im["is_im"] == True:
                return im["id"]
        return None
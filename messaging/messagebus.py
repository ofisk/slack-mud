ADMIN_USER = 'U10F84U2J'

class MessageBus:
    adminCommands = {}
    pendingCommandsByUser = {}
    registeredUsers = {}
    globalCommands = {}

    def __init__(self):
        globalCommands = {}
        adminCommands = {}
        pendingCommandsByUser = {}
        registeredUsers = {}

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
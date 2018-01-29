import shared
import roomids
import globalmap
import character.races
import character.classes

def createTrainingRoom(mbus, users):
    def trainingRoomOnEnter(user):
        user["currentRoomId"] = roomids.TRAINING_ROOM_ID
        mbus.postMessageToParty("""
                You enter a circular room, almost completely empty except for a fountain in the center of the room.
                A door to the north is visible but seems to be sealed shut, currently.  A voice from nowhere and 
                everywhere beckons you forward, "%s, peer into the Fountain to begin your journey."
            """ % (user["name"])
        )

    def trainingCompleteRoomOnEnter(user):
        user["currentRoomId"] = roomids.TRAINING_COMPLETE_ROOM_ID
        mbus.postMessageToParty("""
                The voice returns again to congratulate you for completing your training:
                "Congratulations, %s.  You have now completed your introduction to this world.
                Ahead of you lies adventure, glory, and gold.  Oh wait, nevermind.  Oren hasn't
                built this part yet.  I guess you just have to stand here now.  Alright... well...
                Bye, I guess.
                ...
                Also, fuck York.
            """ % (user["name"])
        )

    def gl_handleClassReset(userId):
        def setClassForUser(user, command):
            requestedClass = "UNKNOWN"
            PLAYABLE_CLASSES = character.classes.PLAYABLE_CLASSES
            for playableClass in PLAYABLE_CLASSES:
                if (playableClass.lower() == command.lower()):
                    requestedClass = playableClass.lower()
                    break
            if (requestedClass != "UNKNOWN"):
                mbus.postMessageToUser(user, 
                    """You chose *{0}*. If you'd like to change your class, you'll have to reset your character with '@slackmud reset character'""".format(requestedClass)
                )
                #TODO: continue the training quiz?
            else:
                mbus.postMessageToUser(user, 
                    """Sorry, I don't recognize that class, please try again."""
                )
                mbus.registerCommandForUser(user, gl_handleClassReset)

        def listClasses():
            PLAYABLE_CLASSES = character.classes.PLAYABLE_CLASSES
            for playableClass in PLAYABLE_CLASSES:
                mbus.postMessageToUser(users[userId], 
                    "{0}".format(playableClass)
                )

        mbus.postMessageToUser(users[userId], 
            """What profession do you follow?
            """
        )
        listClasses()
        mbus.postMessageToUser(users[userId], 
            """To see descriptions of each class, type '@slackmud describe class' and then tell me which class you'd like me to describe.
            """
        )
        mbus.registerCommandForUser(users[userId], setClassForUser)

    def gl_handleRaceReset(userId):
        def setRaceForUser(user, command):
            requestedRace = "UNKNOWN"
            PLAYABLE_RACES = character.races.PLAYABLE_RACES
            for race in PLAYABLE_RACES:
                if (race.lower() == command.lower()):
                    requestedRace = race.lower()
                    break
            if (requestedRace != "UNKNOWN"):
                mbus.postMessageToUser(user, """You chose *{0}*. If you'd like to change your race, you'll have to reset your character with '@slackmud reset character'.""".format(requestedRace))
                if (user["training"]):
                    gl_handleClassReset(userId)
            else:
                mbus.postMessageToUser(user, """Sorry, I don't recognize that race, please try again.""")
                mbus.registerCommandForUser(user, gl_handleRaceReset)

        def listRaces():
            PLAYABLE_RACES = character.races.PLAYABLE_RACES
            for race in PLAYABLE_RACES:
                mbus.postMessageToUser(user, "{0}".format(race))

        mbus.postMessageToUser(users[userId], "What people do you hail from?")
        listRaces()
        mbus.postMessageToUser(users[userId], 
            """To see descriptions of each race, type '@slackmud describe race' and then tell me which race you'd like me to describe.
            """
        )
        mbus.registerCommandForUser(users[userId], setRaceForUser)

    def gl_handleGenderReset(userId):
        def setGenderForUser(user, command):
            gender = "male"
            if (command.lower() != "male"):
                gender = "female"
            user["gender"] = gender
            users[user["id"]] = user
            mbus.postMessageToUser(user, " You chose *{0}*. If you'd like to change your gender type '@slackmud reset gender' at any time.".format(gender))
            if (user["training"]):
                gl_handleRaceReset(userId)

        mbus.postMessageToUser(user, "Are you male or female?")
        mbus.registerCommandForUser(users[userId], setGenderForUser)

    def beginTrainingQuiz(user):
        user["training"] = True
        users[user["id"]] = user
        mbus.postMessageToParty("""
                A strange power seems to overcome {0}.  Unable to move, they stare into the depths of the still pond.
            """.format(user["name"])
        )
        mbus.postMessageToUser(user, """
                As you look into the still waters of the fountain you see your face and form start to twist. The 
                voice returns, "Who are you?" You think the question seems odd but suddenly can't remember yourself.  
                Even the most basic of questions escape you.
            """
        )
        gl_handleGenderReset(user["id"])


    trainingCompleteRoomConnections = {"s": roomids.TRAINING_ROOM_ID, "south": roomids.TRAINING_ROOM_ID}
    trainingCompleteRoom = shared.createNewRoom(roomids.TRAINING_COMPLETE_ROOM_ID, trainingCompleteRoomOnEnter, None, trainingCompleteRoomConnections)
    globalmap.addRoom(trainingCompleteRoom)
    commandMap = {
        "look at fountain": beginTrainingQuiz, 
        "look at the fountain": beginTrainingQuiz, 
        "look into fountain": beginTrainingQuiz, 
        "look into the fountain": beginTrainingQuiz, 
        "peer into fountain": beginTrainingQuiz, 
        "peer into the fountain": beginTrainingQuiz,
        "i look at fountain": beginTrainingQuiz,
        "i look at the fountain": beginTrainingQuiz, 
        "i look into fountain": beginTrainingQuiz, 
        "i look into the fountain": beginTrainingQuiz, 
        "i peer into fountain": beginTrainingQuiz, 
        "i peer into the fountain": beginTrainingQuiz,
    }


    mbus.registerGlobalCommand('@slackmud reset gender', gl_handleGenderReset)

    return shared.createNewRoom(
        roomids.TRAINING_ROOM_ID, 
        trainingRoomOnEnter, 
        commandMap, {
            "n": roomids.TRAINING_COMPLETE_ROOM_ID, 
            "north": roomids.TRAINING_COMPLETE_ROOM_ID
        }
    )
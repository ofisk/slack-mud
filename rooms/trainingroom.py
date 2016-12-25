import shared
import roomids
import globalmap

def createTrainingRoom(sc, mbus, users) :
    def trainingRoomOnEnter(user) :
        user["currentRoomId"] = roomids.TRAINING_ROOM_ID
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
        user["currentRoomId"] = roomids.TRAINING_COMPLETE_ROOM_ID
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

    def gl_handleGenderReset(userId) :
        def setGenderForUser(user, command) :
            adjective = "manly"
            gender = "male"
            if (command.lower() != "male") :
                adjective = "pretty"
                gender = "female"
            user = users[userId]
            user["gender"] = gender
            users[user["id"]] = user
            sc.api_call(
                "chat.postMessage",
                channel="#slackmud",
                text=""" You chose {0}, are you sure? Not to say you don't look very {1}. If you'd like to change your gender type '@slackmud reset gender' at any time.""".format(gender, adjective)
            )

        sc.api_call(
            "chat.postMessage",
            channel="#slackmud",
            text="""
                Are you male or female?
            """
        )
        mbus.registerCommandForUser(users[userId], setGenderForUser)

    def beginTrainingQuiz(user) :
        sc.api_call(
            "chat.postMessage",
            channel="#slackmud",
            text="""
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
        "peer into the fountain": beginTrainingQuiz
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
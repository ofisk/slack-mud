def createCharacter(name, gender, race, mudclass, stats) :
    return {
        "name": name,
        "gender": gender,
        "race": race,
        "class": mudclass,
        "stats": stats
    }

def setName(character, value) :
    setProperty(character, "name", value)

def setGender(character, value) :
    setProperty(character, "gender", value)

def setRace(character, value) :
    setProperty(character, "race", value)

def setClass(character, value) :
    setProperty(character, "class", value)

def setStats(character, value) :
    setProperty(character, "stats", value)

def setProperty(character, property, value) :
    character[property] = value
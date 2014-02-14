# coding: utf8

response.static_version = '1.0.0'

# This model has functions which relate to to games, game participations, and user status in the game.

# Generates a 12 character bitecode in hexidecimal.
def generatebitecode():
    import uuid

    return str(uuid.uuid4().hex)[:12].upper()


# Generates a 14 character curecode in hexidecimal.
def generatecurecode():
    import uuid

    return str(uuid.uuid4().hex)[:14].upper()


# Checks to see if there is an active game. If there is it returns the game ID. If not it returns False. DEPRICATED
def currentgame():
    games = db(db.games).select(orderby=~db.games.created, limitby=(0, 1))
    for game in games:
        if converttotz(game.end_at) > getesttime():
            return game.id
    else:
        return False


# checks if there is an upcoming but not yet started game
def isgameupcoming():
    cgame = db(db.games).select(orderby=~db.games.created, limitby=(0, 1))
    if cgame:
        if getesttime() < converttotz(cgame[0].end_at) and getesttime() < converttotz(cgame[0].start_at):
            return True
        else:
            return False
    else:
        return False


# Looks up and returns the game participation info for the current user.
def returncurrentuserpart():
    if auth.is_logged_in() and gameinfo:
        authid = auth.user.id
        user = db((db.auth_user.id == authid) & (db.auth_user.id == db.game_part.user_id) &
                  (db.games.id == db.game_part.game_id) & (db.games.id == gameinfo.getId()) & (
                  db.game_part.creature_type == db.creature_type.id)).select(
            db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle,
            db.auth_user.registration_id,
            db.game_part.id, db.game_part.bitecode, db.game_part.zombie_expires_at, db.game_part.squad_leader,
            db.game_part.squad_id,
            db.game_part.banned, db.creature_type.name, db.creature_type.zombie, db.creature_type.immortal,
            db.game_part.squad_apps,
        )
        if user:
            return user[0]
        else:
            return False
    else:
        return False


# Returns the game registation app info for the current user. Returns if it exists or not.
def returncurrentuserapp():
    if auth.is_logged_in() and gameinfo:
        authid = auth.user.id
        regreq = db((db.registration_app.user_id == authid) & (db.registration_app.game_id == gameinfo.getId())).select()
        if regreq:
            return True
        else:
            return False
    else:
        return False


# Returns the game registation request info for the current user. Returns if it exists or not. (this is for filtering non-students)
def returncurrentuserreqapp():
    if auth.is_logged_in():
        authid = auth.user.id
        gid = getgamevars()
        regreq = db((db.registration_request.user_id == authid) & (db.registration_app.game_id == gameinfo.getId())).select()
        if regreq:
            return True
        else:
            return False
    else:
        return False


# returns a new starve timer based on the current time per food DEPRICATED
def zombiebitefood(time):
    newtime = getesttime() + timedelta(seconds=gameinfo.foodtime())
    return newtime


# Checks to see if a cure has expired. DEPRICATED
def isexpired(cure):
    if converttotz(cure.expiration) > getesttime():
        return False
    else:
        return True


# Checks to see if a cure has expired. NEW takes a joined row item as args
def isExpiredCure(cure):
    if converttotz(cure.cures.expiration) > getesttime():
        return False
    else:
        return True


# Checks to see if a player has starved. NEW. Must pass user.creature_type.immortal, game_part.zombie_expires_at, and creature_type.zombie joined
def isZombieDead(user):
    if user.creature_type.zombie:
        if converttotz(user.game_part.zombie_expires_at) > getesttime() and user.creature_type.zombie:
            return False
        elif user.creature_type.immortal:
            return False
        else:
            return True
    else:
        return False


# Checks to see if a player has starved. DEPRECATED
def isdead(user):
    if db.creature_type(user.creature_type).zombie:
        if converttotz(user.zombie_expires_at) > getesttime() and db.creature_type(user.creature_type).zombie:
            return False
        elif db.creature_type(user.creature_type).immortal:
            return False
        else:
            return True
    else:
        return False


# checks to see if a player's infection is past the cure_timer. Will return False if there is no bite_event. DEPRICATED
def isinfected(user):
    gd = gameinfo.getId()
    bevent = db((db.bite_event.human_id == user.id) & (db.bite_event.game_id == gd)).select().last()
    if bevent:
        inftimer = getesttime() - converttotz(bevent.created)
        if gameinfo.cureTime() > inftimer.seconds:
            return False
        else:
            return True
    else:
        return False


# Checks to see if a mission has unlocked for non-admins.
def isunlocked(mis):
    if converttotz(mis.mission_reveal) < getesttime():
        return True
    else:
        return False


def isover(mis):
    if converttotz(mis.mission_end) < getesttime():
        return True
    else:
        return False


# takes an auth_user id and returns all the game_parts associated with it. DEPRICATED
def gamesplayed(user):
    if user:
        gamesplayed = db(db.game_part.user_id == user).select(orderby=db.game_part.id)
        return gamesplayed


# function to return bite_events of a zombie, given the game_part ID and game ID. If the total variable is false it will return rows of bites, otherwise just the total.
def totalkills(user, game, total):
    if user and game:
        bites = db((db.bite_event.zombie_id == user) & (db.bite_event.game_id == game)).select(db.bite_event.ALL)
        if total:
            return len(bites)
        else:
            return bites




def missionfeed(gameid):
    if gameid:
        return db(db.missions.game_id == gameid).select(cache=(cache.ram, 15), cacheable=True)
    else:
        return False
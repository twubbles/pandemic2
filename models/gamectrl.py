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


# checks if current game is an upcoming game
def isgameupcoming():
    if gameinfo.getId():
        if getesttime() < converttotz(gameinfo.gameStart()):
            return True
        else:
            return False
    else:
        return False


# Looks up and returns the game participation info for the current user.
def returncurrentuserpart():
    if auth.is_logged_in() and gameinfo.getId():
        authid = auth.user.id
        user = db((db.auth_user.id == authid) & (db.auth_user.id == db.game_part.user_id) &
                  (db.games.id == db.game_part.game_id) & (db.games.id == gameinfo.getId()) & (
                  db.game_part.creature_type == db.creature_type.id)).select(
            db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle,
            db.auth_user.registration_id,
            db.game_part.id, db.game_part.bitecode, db.game_part.zombie_expires_at, db.game_part.squad_leader,
            db.game_part.squad_id, db.creature_type.hidden,
            db.game_part.banned, db.creature_type.name, db.creature_type.zombie, db.creature_type.immortal,
            db.game_part.squad_apps,cache=(cache.ram, 5), cacheable=True
        )
        if user:
            return user[0]
        else:
            return False
    else:
        return False


# Returns the game registation app info for the current user. Returns if it exists or not.
def returncurrentuserapp():
    if auth.is_logged_in() and gameinfo.getId():
        authid = auth.user.id
        regapp = db((db.registration_app.user_id == authid) & (db.registration_app.game_id == gameinfo.getId())).select()
        if regapp:
            return True
        else:
            return False
    else:
        return False


# Returns the game registation request info for the current user. Returns if it exists or not. (this is for filtering non-students)
def returncurrentuserreqapp():
    if auth.is_logged_in():
        authid = auth.user.id
        regreq = db((db.registration_request.user_id == authid) & (db.registration_request.game_id == gameinfo.getId())).select()
        if regreq:
            return True
        else:
            return False
    else:
        return False


# Checks to see if a cure has expired. NEW takes a joined row item as args
def isExpiredCure(cure):
    if converttotz(cure.cures.expiration) > getesttime():
        return False
    else:
        return True


# Checks to see if a player has starved. NEW. Must pass user.creature_type.immortal, game_part.zombie_expires_at, and creature_type.zombie joined
def isZombieDead(user):
    if user.creature_type.zombie:
        if converttotz(user.game_part.zombie_expires_at) > getesttime() and not user.creature_type.immortal:
            return False
        elif user.creature_type.immortal:
            return False
        else:
            return True
    else:
        return False


# Checks if mission details have unlocked.
def isunlocked(mis):
    if converttotz(mis.mission_reveal) < getesttime():
        return True
    else:
        return False

# Checks if a mission is over.
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

# will return all of the missions for a game
def missionfeed(gameid):
    if gameid:
        return db(db.missions.game_id == gameid).select(cache=(cache.ram, 15), cacheable=True)
    else:
        return False


# form validator for the geolocation information on bitecodes. it is hardcoded for the umass amherst campus area
def validategeo(form):
    lat = form.vars.Lat
    lng = form.vars.Long
    north = 42.405967152309120
    south = 42.383401202818526
    east = -72.513628005981450
    west = -72.538347244262700
    if (float(lat) > float(north)) or float(lat) < float(south):
        form.errors.Lat = "invalid latitude"
    elif float(lng) > float(east) or float(lng) < float(west):
        form.errors.Long = "invalid longitude"
    else:
        form.vars.Lat = lat
        form.vars.Long = lng

# form validator for prompts requiring typed confirmation of an action. requires "YES"
def validateconfirm(form):
    if not (form.vars.Confirm == "YES"):
        form.errors.Confirm = 'You did not confirm the action'
    else:
        form.vars.Confirm = form.vars.Confirm

# form validator for registration requests
def validateemail(form):
    defappeal="Reason why you should play. Ex: Alumni, friend of student, visiting from another school, etc. Alums must state year of graduation. Friends of students must state the student they are friends with. Visitors must tell us what school they are from."
    if form.vars.address == 'address@email.com':
        form.errors.address = 'You did not enter your email!'

    elif form.vars.appeal == defappeal:
        form.errors.appeal = 'You need to tell us why you should play!'
    else:
        form.vars.address = form.vars.address
        form.vars.appeal = form.vars.appeal
        form.vars.original = form.vars.original


# Forum access checker
def forumAccess(gpart,forumid):
    foruminfo = db.forum_forums(forumid)
    if gpart and foruminfo:
        if auth.has_membership('admins' or 'mods'):
            return True
        elif foruminfo.zombie and gpart.creature_type.zombie and not isZombieDead(gpart):
            return True
        elif foruminfo.human and not gpart.creature_type.zombie:
            return True
        else:
            return False
    else:
        return False


def getSassyPost():
    phrase = db(db.sassypost).select(db.sassypost.phrase, orderby='<random>').last()
    return phrase.phrase

# form validator for forum posts
def forumCheck(form):
    user = db((db.game_part.user_id == form.vars.author) & (db.game_part.game_id == gameinfo.getId())).select().last()
    timecheck = converttotz(user.lastpost + timedelta(minutes=gameinfo.postTimer()))
    if  timecheck > getesttime():
        form.errors.author = getSassyPost()
        form.errors.body = getSassyPost()
    else:
        user.update_record(lastpost=request.now)
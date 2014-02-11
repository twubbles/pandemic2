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

# Checks to see if there is an active game. If there is it returns the game ID. If not it returns False.       
def currentgame():
    games = db(db.games).select(orderby=~db.games.created, limitby=(0, 1))
    for game in games:  
        if converttotz(game.end_at) > getesttime():
            return game.id
    else:
        return False

# checks if there is an upcoming game            
def isgameupcoming():
    cgame = db.games(currentgame())
    if cgame: 
        if converttotz(cgame.end_at) > getesttime() and converttotz(cgame.start_at) > getesttime():
            return True
        else:
            return False
    else:
        return False

# Looks up and returns the game participation info for the current user.                      
def returncurrentuserpart():
    if auth.is_logged_in():
        gid=currentgame()
        user = db((db.game_part.user_id==auth.user.id) & (db.game_part.game_id==gid)).select()
        if user:
            return user[0]
        else:
            return False
    else:
        return False

# Returns the game registation app info for the current user. Returns if it exists or not.
def returncurrentuserapp():                      
    if auth.is_logged_in():
        gid=currentgame()
        regreq = db((db.registration_app.user_id==auth.user.id) & (db.registration_app.game_id==gid)).select()
        if regreq:
            return True
        else:
            return False
    else:
        return False

# Returns the game registation request info for the current user. Returns if it exists or not. (this is for filtering non-students)
def returncurrentuserreqapp():                      
    if auth.is_logged_in():
        gid=currentgame()
        regreq = db((db.registration_request.user_id==auth.user.id) & (db.registration_app.game_id==gid)).select()
        if regreq:
            return True
        else:
            return False
    else:
        return False
    
# takes a starve time and adds the bite per food to it
def zombiebitefood(stime):
    gid=currentgame()
    gameinfo =  db(db.games.id==gid).select()
    foodtime = gameinfo[0].time_per_food 
    stime = getesttime() + datetime.timedelta(seconds=foodtime)
    return stime



    
# Checks to see if a cure has expired.
def isexpired(cure):
    if converttotz(cure.expiration) > getesttime():
         return False
    else:
        return True

# Checks to see if a player has starved. NEW. Must pass auth_user, game_part, and creature_type joined
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
                
# checks to see if a player's infection is past the cure_timer. Will return False if there is no bite_event.          
def isinfected(user):
    gd = currentgame()
    bevent =  db((db.bite_event.human_id==user.id) & (db.bite_event.game_id==gd)).select().last()
    if bevent:
        gameinf =  db(db.games.id==gd).select()
        inftimer = getesttime() - converttotz(bevent.created)
        if gameinf[0].cure_timer > inftimer.seconds:
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

# takes an auth_user id and returns all the game_parts associated with it.
def gamesplayed(user):
        if user:
            gamesplayed = db(db.game_part.user_id==user).select(orderby=db.game_part.id)
            return gamesplayed

# function to return bite_events of a zombie, given the game_part ID and game ID. If the total variable is false it will return rows of bites, otherwise just the total.             
def totalkills(user,game,total):
        if user and game:
            bites = db((db.bite_event.zombie_id==user) & (db.bite_event.game_id==game)).select(db.bite_event.ALL)
            if total:
                return len(bites)
            else:
                return bites

# function to check if registration for a game is alive.
def checkreg(game_id):
    try:
        if request.now > db.games(game_id).signup_start_at and request.now < db.games(game_id).signup_end_at:
            regalive = True
        else:
            regalive = False
        return regalive
    except:
        regalive = False
        return regalive

def missionfeed(gameid):
    if gameid:
        return db(db.missions.game_id==gameid).select(cache=(cache.ram, 15),cacheable=True)
    else:
        return False
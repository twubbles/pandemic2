
### This Controller holds component controllers for information about the game and players ###



# Returns the current game's global stun/starve timers
def gameticker():
    session.forget(response)
    if gameinfo.isGameActive:
        if isgameupcoming():

            globalvars = 'Game begins @ '
            globalvars += pretty_date(gameinfo.gameStart())
        else:
            stimer = (gameinfo.starveTimer() / 60) / 60
            globalvars = 'Stuns: ' + str(gameinfo.stunTime()) + ' mins - Starve Timer: ' + str(stimer) + ' hrs'
    else:

        globalvars = 'No upcoming game yet'
    return dict(globalvars=globalvars)


# Returns the pending events feed
def pendingevents():
    session.forget(response)
    gameid = gameinfo.getId()
    if gameid:
        return db(db.missions.game_id == gameid).select(cache=(cache.ram, 15), cacheable=True)
    else:
        return False






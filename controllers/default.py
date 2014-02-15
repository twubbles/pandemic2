def fblogin():
    response.view = 'default.html'
    form = auth.profile()
    return dict(form=form)


# Default roster page. Pulls all the game_part info for the current game and also returns player counts.
def roster():
    if not gameinfo.getId() and not request.args(0):
        response.flash = 'No current or upcoming game!'
        redirect(URL('index'))
    elif not request.args(0):
        players = db((db.auth_user.id == db.game_part.user_id) & (db.game_part.game_id == gameinfo.getId()) & (
        db.game_part.creature_type == db.creature_type.id)).select(
            db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle,
            db.creature_type.zombie, db.creature_type.name, db.game_part.zombie_expires_at, db.creature_type.immortal,
            cache=(cache.ram, 5), cacheable=True)
        humanTotal = 0
        zombieTotal = 0
        deadTotal = 0
        for player in players:
            if not player.creature_type.zombie:
                humanTotal += 1
            elif player.creature_type.zombie:
                if isZombieDead(player):
                    deadTotal += 1
                else:
                    zombieTotal += 1
        return dict(players=players, humanTotal=humanTotal, zombieTotal=zombieTotal, deadTotal=deadTotal)
    elif request.args(0):
        players = db((db.auth_user.id == db.game_part.user_id) & (db.game_part.game_id == request.args(0)) & (
        db.game_part.creature_type == db.creature_type.id)).select(
            db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle,
            db.creature_type.zombie, db.creature_type.name, db.game_part.zombie_expires_at, db.creature_type.immortal,
            cache=(cache.ram, 5), cacheable=True)
        humanTotal = 0
        zombieTotal = 0
        deadTotal = 0
        for player in players:
            if not player.creature_type.zombie:
                humanTotal += 1
            elif player.creature_type.zombie:
                if isZombieDead(player):
                    deadTotal += 1
                else:
                    zombieTotal += 1
        return dict(players=players, humanTotal=humanTotal, zombieTotal=zombieTotal, deadTotal=deadTotal)


#paginated posts feed
def postfeed():
    page = 0
    if len(request.args):
        page = int(request.args[0])
    else:
        page = 0
    items_per_page = 3
    limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
    posts = db(db.posts).select(orderby=~db.posts.pub_date, limitby=limitby, cache=(cache.ram, 300), cacheable=True)
    return dict(posts=posts, page=page, items_per_page=items_per_page)


# Landing page index.
def index():
    # This builds the globalvars variable that appears at the top of the landing page
    if gameinfo.isGameActive():
        if not isgameupcoming():
            stimer = (gameinfo.starveTimer() / 60) / 60
            globalvars = 'Stun Timer: ' + str(gameinfo.stunTime()) + ' mins - Starve Timer: ' + str(stimer) + ' hrs'
            #grabs the 4 most recent bite events
            events = db(db.bite_event.game_id == gameinfo.getId()).select(orderby=~db.bite_event.created,
                                                                          limitby=(0, 12), cache=(cache.ram, 5),
                                                                          cacheable=True)
        elif isgameupcoming():
            events = False
            count = abs(getesttime() - converttotz(gameinfo.gameStart()))
            hcount = (count.seconds / 60) / 60
            mcount = (count.seconds / 60) - (hcount * 60)
            scount = (count.seconds - ((hcount * 60) * 60)) - (mcount * 60)
            globalvars = str(hcount) + ' hours ' + str(mcount) + ' mins ' + str(scount) + ' secs '
            if count.days:
                globalvars = str(count.days) + ' days ' + globalvars
    else:
        events = False
        globalvars = 'No upcoming game yet'
    if gameinfo.isGameActive():
        missions = missionfeed(currentgame())
    else:
        missions = False
    return dict(missions=missions, globalvars=globalvars)


# View post page.
def view_post():
    post = db.posts[request.args(0)] or redirect(URL(r=request, f='index'))
    return dict(post=post, comments=False)


# Returns the rules doc for the game. In the future I may make this a page and not a file.
def rules():
    redirect(URL('static', 'hvzrules.pdf'))


# View mission page.
def viewmission():
    mission = db.missions[request.args(0)] or redirect(URL(r=request, f='index'))
    if isunlocked(mission):
        return dict(mission=mission)
    else:
        redirect(URL(r=request, f='index'))


# User profile page
def userinfo():
    if request.args(0):
        count = db.bite_event.zombie_id.count()
        count.readable = True
        cparts = db((db.auth_user.id == db.game_part.user_id) & (db.game_part.game_id == db.games.id) & (
        db.auth_user.id == request.args(0)) & (db.game_part.creature_type == db.creature_type.id)).select(
            db.auth_user.id, db.auth_user.bio, db.auth_user.registration_id, db.auth_user.first_name,
            db.auth_user.last_name,
            db.auth_user.handle, db.creature_type.zombie, db.creature_type.name, db.game_part.zombie_expires_at,
            db.creature_type.immortal, db.squads.id, db.squads.name, count, db.game_part.game_id, db.games.id,
            db.games.game_name, left=[db.squads.on(db.squads.id == db.game_part.squad_id),
                                      db.bite_event.on(db.bite_event.zombie_id == db.game_part.id)],
            groupby=~db.game_part.game_id,
            cache=(cache.ram, 1), cacheable=True)
        return dict(cparts=cparts)
    else:
        redirect(URL(r=request, f='index'))


def userlogin():
    form = auth.login(next=URL(r=request, args=request.args))
    dict(form=form)


def user():
    response.view = 'default.html'
    auth.settings.formstyle = 'bootstrap'
    return dict(form=auth())


def download():
    return response.download(request, db)


@auth.requires_signature()
def data():
    return dict(form=crud())

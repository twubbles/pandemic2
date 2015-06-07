def fblogin():
    response.view = 'default.html'
    form = auth.profile()
    return dict(form=form)

def status():
    redirect(URL(c='forums', f='viewthread', args=56, extension='html'))

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
            cache=(cache.ram, 60), cacheable=True)
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
            cache=(cache.ram, 60), cacheable=True)
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


# Landing page index.
def index():
    # This builds the globalvars variable that appears at the top of the landing page
    if gameinfo.isGameActive:
        missions = missionfeed(gameinfo.getId())
        bites = bitefeed(gameinfo.getId())
    else:
        bites = False
        missions = False
    posts = db((db.auth_user.id == db.posts.author)).select(db.posts.id, db.posts.title,
                                                            db.posts.description,
                                                            db.posts.pub_date, db.auth_user.first_name,
                                                            db.auth_user.last_name, db.auth_user.id,
                                                            orderby=~db.posts.pub_date, limitby=(0, 15),
                                                            cache=(cache.ram, 120),
                                                            cacheable=True)
    return dict(missions=missions, posts=posts, bites=bites)


# View post page.
def viewpost():
    if request.args(0):
        pid = request.args(0)
        posts = db((db.auth_user.id == db.posts.author) & (db.posts.id == pid)).select(
                    db.posts.id,db.posts.title,db.posts.description,db.posts.pub_date,
                    db.auth_user.first_name,db.auth_user.last_name,db.auth_user.id,cache=(cache.ram, 120),cacheable=True)
        return dict(posts=posts)
    else:
        redirect(URL(r=request, f='index'))


# Returns the rules doc for the game.
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
            cache=(cache.ram, 30), cacheable=True)
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


# View post page.
def plot_summary():
    post = db(db.summary).select(cache=(cache.ram, 120),cacheable=True).last()
    if post:
        return dict(post=post)
    else:
        redirect(URL(r=request, f='index'))


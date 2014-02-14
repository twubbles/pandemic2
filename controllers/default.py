

def fblogin():
    response.view='default.html'
    form = auth.profile()
    return dict(form=form)

# Default roster page. Pulls all the game_part info for the current game and also returns player counts.
def roster():
    if not currentgame() and not request.args(0):
        response.flash = 'No current or upcoming game!'
        redirect(URL('index'))
    elif not request.args(0):
        players = db((db.auth_user.id==db.game_part.user_id) & (db.game_part.game_id==currentgame()) & (db.game_part.creature_type==db.creature_type.id)).select(
                  db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.creature_type.zombie, db.creature_type.name, db.game_part.zombie_expires_at, db.creature_type.immortal,
                  cache=(cache.ram, 5),cacheable=True)
        humanTotal=0
        zombieTotal=0
        deadTotal=0
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
        players = db((db.auth_user.id==db.game_part.user_id) & (db.game_part.game_id==request.args(0)) & (db.game_part.creature_type==db.creature_type.id)).select(
                  db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.creature_type.zombie, db.creature_type.name, db.game_part.zombie_expires_at, db.creature_type.immortal,
                  cache=(cache.ram, 5),cacheable=True)
        humanTotal=0
        zombieTotal=0
        deadTotal=0
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
    if len(request.args): page=int(request.args[0])
    else: page=0
    items_per_page=3
    limitby=(page*items_per_page,(page+1)*items_per_page+1)
    posts = db(db.posts).select(orderby=~db.posts.pub_date,limitby=limitby,cache=(cache.ram, 300),cacheable=True)
    return dict(posts=posts,page=page,items_per_page=items_per_page)

# Landing page index.
def index():
    # This builds the globalvars variable that appears at the top of the landing page
    if currentgame():
        if not isgameupcoming():
            stimer = (db.games(currentgame()).time_per_food/60)/60
            globalvars = 'Stun Timer: ' + str(db.games(currentgame()).stun_timer) + ' mins - Starve Timer: ' + str(stimer) + ' hrs'
            #grabs the 4 most recent bite events
            events = db(db.bite_event.game_id==currentgame()).select(orderby=~db.bite_event.created,limitby=(0,12),cache=(cache.ram, 5),cacheable=True)
        elif isgameupcoming():
            events = False
            count = abs(getesttime() - converttotz(db.games(currentgame()).start_at))
            hcount = (count.seconds/60)/60
            mcount = (count.seconds/60) - (hcount*60)
            scount = (count.seconds - ((hcount*60)*60)) - (mcount*60)
            globalvars = str(hcount)  + ' hours ' + str(mcount) + ' mins ' + str(scount) + ' secs '
            if count.days:
                globalvars = str(count.days) + ' days ' + globalvars
    else:
        events = False
        globalvars = 'No upcoming game yet'
    if currentgame():
        missions = missionfeed(currentgame())
    else:
        missions = False
    return dict(missions=missions)

# View post page.
def view_post():
    post = db.posts[request.args(0)] or redirect(URL(r=request,f='index'))

    return dict(post=post, comments=False)

# Returns the rules doc for the game. In the future I may make this a page and not a file.
def rules():
    redirect(URL('static', 'hvzrules.pdf'))

# View mission page.
def viewmission():
    mission = db.missions[request.args(0)] or redirect(URL(r=request,f='index'))
    if isunlocked(mission):
        return dict(mission=mission)
    else:
         redirect(URL(r=request,f='index'))

# User profile page
def userinfo():
     if request.args(0):
         count = db.bite_event.zombie_id.count()
         count.readable = True
         cparts = db((db.auth_user.id==db.game_part.user_id) & (db.game_part.game_id==db.games.id) & (db.auth_user.id==request.args(0)) & (db.game_part.creature_type==db.creature_type.id)).select(
                db.auth_user.id, db.auth_user.bio, db.auth_user.registration_id, db.auth_user.first_name, db.auth_user.last_name,
                db.auth_user.handle, db.creature_type.zombie, db.creature_type.name, db.game_part.zombie_expires_at,
                db.creature_type.immortal, db.squads.id, db.squads.name, count ,db.game_part.game_id, db.games.id,
                db.games.game_name, db.game_part.pinktext, left=[db.squads.on(db.squads.id==db.game_part.squad_id),
                db.bite_event.on(db.bite_event.zombie_id==db.game_part.id)],groupby=~db.game_part.game_id,
                cache=(cache.ram, 1),cacheable=True)
         return dict(cparts=cparts)
     else:
         redirect(URL(r=request,f='index'))

# The public squadlist
def squadlist():
    if not currentgame() and not request.args(0):
        msg = 'No current or upcoming game!'
        return dict(squads=False, gid=False,msg=msg)
    elif request.args(0):
        squads=db(db.squads.game_id==request.args(0)).select(orderby='<random>')
        msg= ''
        return dict(squads=squads, gid=request.args(0),msg=msg)
    else:
        if not gpart.game_part.squad_id and not gpart.game_part.squad_apps:
            msg = A("Create Squad", _class='btn btn-success btn-lg pull-right', _href=URL(c='gamectrl', f='createsquadapp'))

        else:
            msg= ''
        squads=db(db.squads.game_id==currentgame()).select(orderby='<random>')
        return dict(squads=squads, gid=False,msg=msg)

# squad info page
def squadinfo():
     squad = db.squads(request.args(0)) or redirect(URL('squadlist'))
     try:
         cpart=returncurrentuserpart()
     except:
         cpart=False
     players = db((db.auth_user.id==db.game_part.user_id) & (db.creature_type.id==db.game_part.creature_type) & (db.squads.id==db.game_part.squad_id) & (db.squads.id==request.args(0))).select(
             db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.auth_user.registration_id,
             db.creature_type.name, db.game_part.zombie_expires_at, db.game_part.squad_title,
             db.game_part.squad_leader,orderby=db.game_part.created)
     if squad and cpart:
         #checks if the view should display a registration button or not
         if not isdead(cpart) and not cpart.squad_apps and not cpart.squad_id:
             app=True
         else:
             app=False
         return dict(squad=squad,players=players, app=app)
     else:
         return dict(squad=squad,players=players, app=False)


def userlogin():
    form=auth.login(next=URL(r=request,args=request.args))
    dict(form=form)
		 
def user():
    response.view='default.html'
    auth.settings.formstyle = 'bootstrap'
    return dict(form=auth())

def download():
    return response.download(request,db)

@auth.requires_signature()
def data():
    return dict(form=crud())

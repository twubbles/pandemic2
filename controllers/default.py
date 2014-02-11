import re
import datetime
from gluon.tools import prettydate
from time import sleep


def fblogin():
    response.view='default.html'
    form = auth.profile()
    return dict(form=form)

# Starved roster page.
def rosterdead():
    if not currentgame():
        response.flash = 'No current or upcoming game!'
        redirect(URL('index'))
    else:
        count = db.bite_event.zombie_id.count()
        count.readable = True
        players = db((db.auth_user.id==db.game_part.user_id) & (db.game_part.game_id==currentgame()) & (db.game_part.creature_type==db.creature_type.id) & (db.creature_type.zombie==True) ).select(db.auth_user.id, count , db.auth_user.registration_id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.squads.name, db.game_part.squad_id, db.creature_type.name, db.game_part.zombie_expires_at, db.creature_type.immortal,db.creature_type.zombie, left=[db.squads.on(db.squads.id==db.game_part.squad_id),db.bite_event.on(db.bite_event.zombie_id==db.game_part.id)], groupby=db.auth_user.id,cache=(cache.ram, 1),cacheable=True)
        for player in players.exclude(lambda player: isZombieDead(player)==False):
            n=0
        return dict(players=players)

# Zombies roster page.
def rosterzombies():
    if not currentgame():
        response.flash = 'No current or upcoming game!'
        redirect(URL('index'))
    else:
        count = db.bite_event.zombie_id.count()
        count.readable = True
        players = db((db.auth_user.id==db.game_part.user_id) & (db.game_part.game_id==currentgame()) & (db.game_part.creature_type==db.creature_type.id) & (db.creature_type.zombie==True) ).select(db.auth_user.id, count , db.auth_user.registration_id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.squads.name, db.game_part.squad_id, db.creature_type.name, db.game_part.zombie_expires_at, db.creature_type.immortal,db.creature_type.zombie, left=[db.squads.on(db.squads.id==db.game_part.squad_id),db.bite_event.on(db.bite_event.zombie_id==db.game_part.id)], groupby=db.auth_user.id,cache=(cache.ram, 1),cacheable=True)
        for player in players.exclude(lambda player: isZombieDead(player)==True):
            n=0
        return dict(players=players)

# Humans roster page.
def rosterhumans():
    if not currentgame():
        response.flash = 'No current or upcoming game!'
        redirect(URL('index'))
    else:
        players = db((db.auth_user.id==db.game_part.user_id) & (db.game_part.game_id==currentgame()) & (db.game_part.creature_type==db.creature_type.id) & (db.creature_type.zombie!=True) ).select(db.auth_user.id, db.auth_user.registration_id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.squads.name, db.game_part.squad_id, db.creature_type.name, left=db.squads.on(db.squads.id==db.game_part.squad_id),cache=(cache.ram, 1),cacheable=True)
    return dict(players=players)

# Default roster page. Pulls all the game_part info for the current game.
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


# The image gallery function for cycleimages DB.
def gallery():
    image = db.cycleimages[request.args(0)] or redirect(URL(r=request,f='index'))
    return dict(image=image)


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

# Create a post page
@auth.requires_membership('admins')
def create():
    response.view='default.html'
    response.flash = "Create a post!"
    form=SQLFORM(db.posts)
    if form.process().accepted:
        response.flash = 'Post accepted.'
    elif form.errors:
        response.flash = 'The post has errors, idiot!'
    else:
        response.flash = 'Make your post!'
    return dict(form=form)

# Edit a post page
@auth.requires_membership('admins')
def edit():
    response.view='default.html'
    post = db.posts(request.args(0)) or redirect(URL('error'))
    form=SQLFORM(db.posts, post, deletable = True)
    response.flash = 'Edit the post!'
    if form.validate():
        if form.deleted:
            db(db.posts.id==post.id).delete()
            redirect(URL('index'))
            response.flash = 'POST BALEETED!'
        else:
            post.update_record(**dict(form.vars))
            response.flash = 'Changes saved.'
    else:
        response.flash = 'Edit the post!'
    return dict(form=form)

# View post page. Also, looks up comments for post.
def view_post():
    post = db.posts[request.args(0)] or redirect(URL(r=request,f='index'))

    return dict(post=post, comments=False)

# Scaffolding stuff, manage users page
@auth.requires_membership('admins')
def manage_users():
    return dict(form=SQLFORM.smartgrid(db.auth_user))

# Scaffolding stuff, manage groups
@auth.requires_membership('admins')
def manage_groups():
    return dict(form=SQLFORM.grid(db.auth_membership))

# Returns the rules doc for the game. In the future I may make this a page and not a file.
def rules():
    redirect(URL('static', 'hvzrules.pdf'))

# View post page. Also, looks up comments for post.
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
         cparts = db((db.auth_user.id==db.game_part.user_id) & (db.auth_user.id==request.args(0)) & (db.game_part.game_id==db.games.id)).select(db.auth_user.id, db.auth_user.bio, db.auth_user.registration_id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.creature_type.zombie, db.creature_type.name, db.game_part.zombie_expires_at, db.creature_type.immortal, db.squads.id, db.squads.name, count ,db.game_part.game_id, db.games.id, db.games.game_name, db.game_part.pinktext, left=[db.squads.on(db.squads.id==db.game_part.squad_id),db.bite_event.on(db.bite_event.zombie_id==db.game_part.id)],groupby=~db.game_part.game_id, cache=(cache.ram, 300),cacheable=True)
         return dict(cparts=cparts)
     else:
         redirect(URL(r=request,f='index'))

# The public squadlist
def squadlist():
    if request.args(0):
        squads=db(db.squads.game_id==request.args(0)).select(orderby='<random>', cache=(cache.ram, 300),cacheable=True)
        return dict(squads=squads, gid=request.args(0))
    else:
        squads=db(db.squads.game_id).select(orderby=~db.squads.game_id, cache=(cache.ram, 300),cacheable=True)
        return dict(squads=squads, gid=False)

# squad info page
def squadinfo():
     squad = db.squads(request.args(0)) or redirect(URL('squadlist'))
     try:
         cpart=returncurrentuserpart()
     except:
         cpart=False
     if squad and cpart:
         #checks if the view should display a registration button or not
         if not isdead(cpart) and not cpart.squad_apps and not cpart.squad_id:
             app=True
         else:
             app=False
         members = db((db.game_part.squad_id==squad.id) & (db.game_part.squad_leader==False)).select(orderby=db.game_part.created, cache=(cache.ram, 60),cacheable=True)
         leader = db.game_part(squad.leader)
         return dict(squad=squad,members=members,leader=leader, app=app, cpart=cpart)
     else:
         members = db((db.game_part.squad_id==squad.id) & (db.game_part.squad_leader==False)).select(orderby=db.game_part.created, cache=(cache.ram, 60),cacheable=True)
         leader = db.game_part(squad.leader)
         return dict(squad=squad,members=members,leader=leader, app=False)

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

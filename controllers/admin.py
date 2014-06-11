# coding: utf8

# Admin page
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def index():
    if gameinfo.getId():
        missions = missionfeed(gameinfo.getId())
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
        biteTotal = db(db.bite_event.game_id == gameinfo.getId()).count()
        cureTotal = db(db.cure_event.game_id == gameinfo.getId()).count()
        return dict(missions=missions, humanTotal=humanTotal, zombieTotal=zombieTotal, deadTotal=deadTotal,
                    biteTotal=biteTotal,cureTotal=cureTotal)
    else:
        missions = False
        humanTotal = 0
        zombieTotal = 0
        deadTotal = 0
        biteTotal = 0
        cureTotal= 0
        return dict(missions=missions, humanTotal=humanTotal, zombieTotal=zombieTotal, deadTotal=deadTotal,
                    biteTotal=biteTotal,cureTotal=cureTotal)


# admin squad management interface
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def adminsquadlist():
    response.view = 'admintemplate.html'
    grid = SQLFORM.grid(db.squads, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=grid)


# admin player-type management interface
@auth.requires_membership('admins')
def manage_types():
    response.view = 'admintemplate.html'
    grid = SQLFORM.grid(db.creature_type, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=grid)


# post management interface
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def manage_posts():
    grid = SQLFORM.smartgrid(db.posts, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=grid)

# post management interface
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def manage_sum():
    response.view = 'admintemplate.html'
    grid = SQLFORM.smartgrid(db.summary, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=grid)


# admin user management interface
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def manage_users():
    users = db((db.auth_user.id)).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name,
                                         db.auth_user.handle, groupby=db.auth_user.id, cache=(cache.ram, 1),
                                         cacheable=True)
    return dict(users=users)


# Edit a game_part
@auth.requires_membership('admins')
def manage_user_parts():
    if request.args(0):
        parts = db((db.auth_user.id == db.game_part.user_id) & (db.game_part.game_id == db.games.id) &
                   (db.game_part.creature_type == db.creature_type.id) &
                   (db.game_part.user_id == request.args(0))).select(db.games.game_name, db.game_part.id,
                                                                     db.auth_user.first_name, db.auth_user.last_name,
                                                                     db.auth_user.handle, db.game_part.bitecode,
                                                                     db.squads.name, db.game_part.squad_id,
                                                                     db.creature_type.name,
                                                                     db.game_part.zombie_expires_at, db.auth_user.id,
                                                                     db.creature_type.zombie, db.creature_type.immortal,
                                                                     groupby=db.game_part.id, cache=(cache.ram, 60),
                                                                     cacheable=True)
        return dict(parts=parts)
    else:
        redirect(URL('admin', 'manage_users'))


# sassy post management interface
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def sassy_posts():
    response.view = 'admintemplate.html'
    form = SQLFORM.grid(db.sassypost, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=form)


# The mission list page
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def missionlist():
    grid = SQLFORM.smartgrid(db.missions, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=grid)


# The cure list page
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def curelist():
    unusedcures = db((db.games.id == db.cures.game_id) & (db.cures.used == False)).select(
        db.cures.id, db.cures.expiration, db.cures.used, db.cures.curecode, db.games.game_name,
        orderby=~db.cures.id)
    usedcures = db(
        (db.games.id == db.cures.game_id) & (db.cures.id == db.cure_event.cure_id) &
        (db.cure_event.player_id == db.game_part.id) & (db.auth_user.id == db.game_part.user_id)
    ).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.cure_event.created,
             db.cures.id, db.cures.curecode, db.games.game_name, orderby=~db.cures.id)
    return dict(unusedcures=unusedcures, usedcures=usedcures)


# takes a zombie game_part id and adds the food to it
@auth.requires_membership('admins')
def zombierewardfood():
    response.view = 'admintemplate.html'
    form = SQLFORM.factory(Field("Minutes", 'integer'),
                           submit_button="Add Time!!")
    session.flash = "Enter the Minutes to reward"
    if form.process().accepted:
        realtime = (form.vars.Minutes * 60)
        zombies = db((db.game_part.game_id == gameinfo.getId()) & (db.creature_type.id == db.game_part.creature_type) &
                     (db.creature_type.zombie == True)).select(
            db.game_part.id, db.game_part.game_id, db.creature_type.zombie,
            db.game_part.zombie_expires_at, db.creature_type.immortal)
        for zombie in zombies:
            if not (isZombieDead(zombie) or db.creature_type.immortal):
                stime = timedelta(seconds=realtime)
                newtime = zombie.game_part.zombie_expires_at + stime
                if newtime > gameinfo.addFoodTimer():
                    newtime = gameinfo.addFoodTimer()
                db(db.game_part.id == zombie.game_part.id).update(zombie_expires_at=newtime)
        session.flash = "All Zombies Given " + str(realtime / 60) + " minutes of life!"
        from admintools import adminlog
        adminlog(str(auth.user.first_name) + " " + str(auth.user.last_name) + " (" + str(auth.user.id) + ")" + " gave all zombies " + str(realtime / 60) + " minutes of life")
        form = ''
        return dict(form=form)
    return dict(form=form)


# Shambling dead interface 
@auth.requires_membership('admins')
def zombieraise():
    import random
    response.view = 'admintemplate.html'
    form = SQLFORM.factory(Field("confirm", label="type: I AM SURE to confirm", default=""),
                           submit_button="RAISE THE DEAD!", )
    if form.process().accepted:
        if form.vars.confirm.upper() == "I AM SURE":
            zombies = db(
                (db.game_part.game_id == gameinfo.getId()) & (db.creature_type.id == db.game_part.creature_type) &
                (db.creature_type.zombie == True)).select(
                db.game_part.id, db.game_part.game_id, db.creature_type.zombie,
                db.game_part.zombie_expires_at, db.creature_type.immortal)
            for zombie in zombies:
                if isZombieDead(zombie):
                    stime = timedelta(seconds=random.randrange(28800, 72000))
                    newtime = getEstNow() + stime
                    db(db.game_part.id == zombie.game_part.id).update(zombie_expires_at=newtime)

            session.flash = "THE SHAMBLING DEAD HAVE ARISEN ONCE AGAIN!"
            from admintools import adminlog
            adminlog(str(auth.user.first_name) + " " + str(auth.user.last_name) + " (" + str(auth.user.id) + ")" + " activated the shambling dead")
            form = ''
        return dict(form=form, )
    session.flash = "Confirm the raising of the dead? All dead will be raised and given random amounts of food."
    return dict(form=form, )


# edit a cure page
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def editcure():
    response.view = 'admintemplate.html'
    cure = db.cures(request.args(0)) or redirect(URL('error'))
    form = SQLFORM(db.cures, cure, deletable=True)
    if form.validate():
        from admintools import adminlog
        adminlog(str(auth.user.id) + " changed cure " + str(form.vars))
        if form.deleted:
            db(db.cures.id == cure.id).delete()
            redirect(URL('curelist'))
            session.flash = 'CURE BALEETED!'
        else:
            cure.update_record(**dict(form.vars))
            session.flash = 'Changes saved.'
    else:
        session.flash = 'Edit the cure.'
    return dict(form=form)


# Create a cure function
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def createcure():
    game = gameinfo.getId()
    if not game:
        session.msg = 'Can only create a cure when there is a game active'
        redirect(URL(c='admin', f='curelist'))
    else:
        authid = auth.user.id
        cure = db.cures.insert(game_id=gameinfo.getId(), curecode=generatecurecode(), used=False,
                               admincreator=authid, expiration=gameinfo.addFoodTimer())

        session.msg = 'Cure code created!'
        from admintools import adminlog
        adminlog(str(authid) + " created cure " + str(cure))
        redirect(URL(c='admin', f='curelist'))


# The admin game page
@auth.requires_membership('admins')
def games():
    games = db(db.games).select(orderby=db.games.created)
    return dict(games=games)


# The create a game page
@auth.requires_membership('admins')
def creategame():
    response.view = 'admintemplate.html'
    form = SQLFORM(db.games)
    if form.process().accepted:
        response.flash = 'game created!'
    elif form.errors:
        response.flash = 'The game has errors, idiot!'
    else:
        response.flash = 'Make your game!'
    return dict(form=form)


# edit a game page
@auth.requires_membership('admins')
def editgame():
    response.view = 'admintemplate.html'
    game = db.games(request.args(0)) or redirect(URL('error'))
    form = SQLFORM(db.games, game, deletable=False)
    session.flash = 'Edit the game'
    if form.validate():
        if form.deleted:
            db(db.games.id == game.id).delete()
            redirect(URL('games'))
            session.flash = 'GAME BALEETED!'
        else:
            game.update_record(**dict(form.vars))
            from admintools import adminlog
            adminlog(str(auth.user.first_name) + " " + str(auth.user.last_name) + " (" + str(auth.user.id) + ")" + " changed the game: " + str(form.vars))
            session.flash = 'Changes saved.'
    else:
        session.flash = 'Edit the game!'
    return dict(form=form)


# View the oz pool for a game
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def ozlist():
    if request.args(0):
        gid = request.args(0)
        users = db((db.auth_user.id == db.game_part.user_id) & (db.game_part.game_id == request.args(0)) & (
            db.game_part.creature_type == db.creature_type.id) & (db.game_part.original_request == True)).select(
            db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle,
            db.creature_type.hidden,
            db.creature_type.name, db.creature_type.immortal, db.game_part.zombie_expires_at, db.game_part.id
        )
        games = False
        return dict(users=users, games=games)
    else:
        users = False
        games = db(db.games).select(orderby=~db.games.created)
        return dict(games=games, users=users)


# Create a game_part for a game
@auth.requires_membership('admins')
def creategamepart():
    response.view = 'admintemplate.html'
    form = SQLFORM(db.game_part)
    if form.process().accepted:
        session.flash = 'Game participation created'
    elif form.errors:
        session.flash = 'has errors'
    return dict(form=form)


# Edit a game_part
@auth.requires_membership('admins')
def editgamepart():
    response.view = 'admintemplate.html'
    part = db.game_part(request.args(0)) or redirect(URL('error'))
    form = SQLFORM(db.game_part, part, deletable=True)
    if form.validate():
        if form.deleted:
            db(db.game_part.id == part.id).delete()
            redirect(URL('games'))
            session.flash = 'BALEETED!'
        else:
            part.update_record(**dict(form.vars))
            session.flash = 'Changes saved.'
    else:
        session.flash = 'Edit the participation'
    return dict(form=form, )

# Edit a user
@auth.requires_membership('admins')
def edituser():
    response.view = 'admintemplate.html'
    user = db.auth_user(request.args(0)) or redirect(URL('error'))
    form = SQLFORM(db.auth_user, user, deletable=False)
    if form.validate():
            user.update_record(**dict(form.vars))
            session.flash = 'Changes saved.'
    else:
        session.flash = 'Auth User Record! (Messing with this can screw up a lot of stuff!)'
    return dict(form=form, )


# reset a bitecode function, arg 0 is game_part.id, arg 1 is auth_user.id
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def regencode():
    if request.args(0) and request.args(1):
        db(db.game_part.id == request.args(0)).update(bitecode=generatebitecode())
        from admintools import adminlog
        adminlog(str(auth.user.first_name) + " " + str(auth.user.last_name) + " (" + str(auth.user.id) + ")" + " regened code for player " + str(request.args(0)))
        session.flash = "Bitecode regenerated"
        message = "Your bitecode has been regenerated. It is now: " + db.game_part(request.args(0)).bitecode
        sendemail(db.game_part(request.args(0)).registration_email, "HvZ New Bitecode", message)
        redirect(URL(c='admin', f='manage_user_parts', args=[request.args(1)]))
    else:
        redirect(URL(c='admin', f='manage_users'))


# Function for creating original zombies from the OZ pool.
@auth.requires_membership('admins')
def makeoz():
    db(db.game_part.id == request.args(0)).update(creature_type=6)
    userpart = db(db.game_part.id == request.args(0)).select()
    session.flash = 'made them an OZ!'
    from admintools import adminlog
    adminlog(str(auth.user.first_name) + " " + str(auth.user.last_name) + " (" + str(auth.user.id) + ")" + " made " + str(request.args(0)) + " an OZ")
    message = "You have been made an Original Zombie. \n"
    message += "You will appear as a Human on the website until you make your first bite. \n"
    message += "Access your bite page by going to the Human bitecode page on your menu. \n"
    message += "While you are hidden, you still have to wear a bandana like a regular zombie. \n"
    message += "Beware, you won't be hidden forever so don't wait too long before making a bite!"
    sendemail(userpart[0].registration_email, "HvZ Important Message!", message)
    redirect(URL(c='admin', f='ozlist', args=userpart[0].game_id))


# Function for granting moderator access
@auth.requires_membership('admins')
def makemod():
    response.view = 'admintemplate.html'
    user = db.auth_user(request.args(0))
    session.flash = 'Type YES to grant ' + user.first_name + ' ' + user.last_name + ' moderator access.'
    form = SQLFORM.factory(Field("Confirm", default=''), submit_button="Do it", )
    if form.process(onvalidation=validateconfirm).accepted:
        db.auth_membership.insert(user_id=request.args(0), group_id=527)
        session.flash = 'made ' + user.first_name + ' ' + user.last_name + ' a mod'
        from admintools import adminlog
        adminlog(str(auth.user.first_name) + " " + str(auth.user.last_name) + " (" + str(auth.user.id) + ")" + " made " + str(request.args(0)) + " a mod")
        return dict(form='')
    else:
        session.flash = 'Type YES to grant ' + user.first_name + ' ' + user.last_name + ' moderator access.'
        return dict(form=form)
    return dict(form=form)


# controller for the the open squad applications page
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def squadapplist():
    squadsapp = db((db.auth_user.id == db.game_part.user_id) & (db.game_part.id == db.squads_app.leader) & (
        db.games.id == db.squads_app.game_id) & (db.squads_app.reviewed == "False")).select(
        db.squads_app.id, db.squads_app.name, db.squads_app.description, db.squads_app.image,
        db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.games.game_name,
        db.auth_user.id, )
    return dict(squadsapp=squadsapp)


# This function is for the admin squad review page. It rejects a squad application.
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def denysquadapp():
    sappid = request.args(0)
    db(db.squads_app.id == sappid).update(reviewed=True, reviewer=auth.user.id)
    from admintools import adminlog
    adminlog(str(auth.user.id) + " denied squad app for " + str(request.args(0)))
    redirect(URL(c='admin', f='squadapplist'))


# This function is for the admin squad review page. It approves a squad application and creates it. It also makes the applicant the squad leader.
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def approvesquadapp():
    sappid = request.args(0)
    sq = db.squads_app(sappid)
    db(db.squads_app.id == sappid).update(reviewed=True, approved=True, reviewer=auth.user.id)
    newsquad = db.squads.insert(game_id=sq.game_id, name=sq.name, description=sq.description, image=sq.image,
                                leader=sq.leader,
                                sigid=sq.sigid)
    db(db.game_part.id == sq.leader).update(squad_leader=True, squad_id=newsquad)
    from admintools import adminlog
    adminlog(str(auth.user.first_name) + " " + str(auth.user.last_name) + " (" + str(auth.user.id) + ")" + " approved squad app for " + str(request.args(0)))
    redirect(URL(c='admin', f='squadapplist'))


# controller for the the open registration requests page
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def regrequestlist():
    regreq = db((db.registration_request.user_id == db.auth_user.id) & (db.registration_request.game_id == db.games.id) & (db.registration_request.reviewed == False)).select(
        db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.games.id,
        db.games.game_name,
        db.auth_user.registration_id, db.registration_request.id, db.registration_request.reviewed,
        db.registration_request.approved,
        db.registration_request.appeal, db.registration_request.judgement, groupby=db.auth_user.id)
    return dict(regreq=regreq)


# This function is for the admin reg request review page. It rejects a reg request.
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def denyregreq():
    regreqid = request.args(0)
    db(db.registration_request.id == regreqid).update(reviewed=True, approved=False, reviewer=auth.user.id)
    message = "Unfortunately, the Admins have denied your registration request. If you believe this was in error you may appeal via e-mail @ admin@umasshvz.com"
    sendemail(regreq.registration_email, "HvZ Registration Request Denied", message)
    from admintools import adminlog
    adminlog(str(auth.user.first_name) + " " + str(auth.user.last_name) + " (" + str(auth.user.id) + ")" + " denied reg app for " + str(request.args(0)))
    redirect(URL(c='admin', f='regrequestlist'))


# This function is for the admin reg request review page. It approves a reg reqest and creates a valid registration app.
@auth.requires(auth.has_membership(group_id='admins') or auth.has_membership(group_id='mods'))
def approveregreq():
    regcode = generatebitecode()
    regreqid = request.args(0)
    regreq = db.registration_request(regreqid)
    db(db.registration_request.id == regreqid).update(reviewed=True, approved=True, reviewer=auth.user.id)
    db.registration_app.insert(user_id=regreq.user_id, game_id=regreq.game_id, registration_code=regcode,
                               original_request=regreq.original_request, created=getEstNow(),
                               registration_email=regreq.registration_email)
    message = "The Admins have approved your registration request! This is your registration code: * " + regcode + " *. Head to http://www.umasshvz.com/pandemic/gamectrl/register to use it."
    sendemail(regreq.registration_email, "HvZ Registration code", message)
    from admintools import adminlog
    adminlog(str(auth.user.first_name) + " " + str(auth.user.last_name) + " (" + str(auth.user.id) + ")" + " approved reg app for " + str(request.args(0)))
    redirect(URL(c='admin', f='regrequestlist'))

# Function for removing immortality from immortal zombies
@auth.requires_membership('admins')
def removeimmortal():
    response.view = 'admintemplate.html'
    session.flash = 'Type YES to strip immortality from all immortal zombies in current game'
    form = SQLFORM.factory(Field("Confirm", default=''), submit_button="Do it", )
    if form.process(onvalidation=validateconfirm).accepted:
        realtime = (64800)
        zombies = db((db.game_part.game_id == gameinfo.getId()) & (db.creature_type.id == db.game_part.creature_type) &
                     (db.creature_type.immortal == True)).select(
            db.game_part.id, db.game_part.game_id, db.game_part.registration_email, db.creature_type.zombie,db.creature_type.id,
            db.game_part.zombie_expires_at, db.creature_type.immortal)
        for zombie in zombies:
            stime = timedelta(seconds=realtime)
            newtime = zombie.game_part.zombie_expires_at + stime
            db(db.game_part.id == zombie.game_part.id).update(zombie_expires_at=newtime, creature_type=2)
            message = "You have LOST your Immortality and have 18 hours until you starve!"
            sendemail(zombie.game_part.registration_email, "HvZ Immortality LOST", message)
        session.flash = "All Immortal Zombies have been stripped of their immortality!"
        from admintools import adminlog
        adminlog(str(auth.user.first_name) + " " + str(auth.user.last_name) + " (" + str(auth.user.id) + ")" + " stripped immortality form all immortals")
        form = ''
        return dict(form=form)
    return dict(form=form)

# This controller emails the adminlog to the head admin, moves the contents
# of the adminlog.txt to the adminlogold.txt, and wipes adminlog.txt.
# This is currently hardcoded to only work if run by specific auth_user(s)

@auth.requires_membership('admins')
def sendlog():
    from admintools import adminlog
    if auth.user.id == 2 or auth.user.id == 488:
        import os
        logdir = os.getcwd()
        logloc = logdir + '/adminlog.txt'
        try:
            logstatus = (os.stat(logloc).st_size!= 0)
        except:
            logstatus = False
        if logstatus:
            with open ("adminlog.txt", "r") as currentlog:
                logcontents=currentlog.read()
            oldlog = open("adminlogold.txt", "a")
            oldlog.write(str("\n" + logcontents))
            oldlog.close()
            sendemail("kimball@umass.edu", "Admin log updates", logcontents)
            os.remove(logloc)
        redirect(URL(c='admin', f='index'))
    else:
        redirect(URL(c='admin', f='index'))
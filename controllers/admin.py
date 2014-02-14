# coding: utf8

# Admin page
@auth.requires_membership('admins')
def index():
    if currentgame():
        missions = missionfeed(currentgame())
    else:
        missions = False
    return dict(missions=missions)


# admin squad management interface
@auth.requires_membership('admins')
def adminsquadlist():
    response.view = 'default.html'
    grid = SQLFORM.grid(db.squads, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=grid)


# admin player-type management interface
@auth.requires_membership('admins')
def manage_types():
    response.view = 'default.html'
    grid = SQLFORM.grid(db.creature_type, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=grid)


# admin game participation management interface
@auth.requires_membership('admins')
def manage_gameparts():
    response.view = 'default.html'
    grid = SQLFORM.grid(db.game_part, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=grid)


# post management interface
@auth.requires_membership('admins')
def manage_posts():
    grid = SQLFORM.smartgrid(db.posts, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=grid)


# admin user management interface
@auth.requires_membership('admins')
def manage_users():
    users = db((db.auth_user.id)).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name,
                                         db.auth_user.handle, groupby=db.auth_user.id, cache=(cache.ram, 1),
                                         cacheable=True)
    return dict(users=users)


@auth.requires_membership('admins')
def manage_users_old():
    response.view = 'default.html'
    form = SQLFORM.smartgrid(db.auth_user, linked_tables=['game_part'], csv=False)
    return dict(form=form)


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
                                                                     groupby=db.game_part.id, cache=(cache.ram, 1),
                                                                     cacheable=True)
        return dict(parts=parts)
    else:
        redirect(URL('admin', 'manage_users'))


# sassy post management interface
@auth.requires_membership('admins')
def sassy_posts():
    form = SQLFORM.grid(db.sassypost, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=form)


# The mission list page
@auth.requires_membership('admins')
def missionlist():
    grid = SQLFORM.smartgrid(db.missions, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=grid)


# The cure list page
@auth.requires_membership('admins')
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


# The flavorimages index page
@auth.requires_membership('admins')
def flavorimages():
    response.view = 'default.html'
    grid = SQLFORM.grid(db.cycleimages, csv=False, searchable=False, sortable=False, create=True)
    return dict(form=grid)


# takes a zombie game_part id and adds the food to it
@auth.requires_membership('admins')
def zombierewardfood():
    form = SQLFORM.factory(Field("Game", default=currentgame()), Field("Minutes", 'integer'),
                           submit_button="Add Time!!", )
    if form.process().accepted:
        realtime = (form.vars.Minutes * 60)
        zombies = db((db.game_part.game_id == form.vars.Game) & (db.game_part.creature_type != 1)).select()
        for zombie in zombies:
            if not isdead(zombie):
                stime = datetime.timedelta(seconds=realtime)
                newtime = zombie.zombie_expires_at + stime
                db(db.game_part.id == zombie.id).update(zombie_expires_at=newtime)
            status = "All Zombies Given " + str(realtime) + " minutes of life!"
        return dict(form=[], status=status)
    return dict(form=form, status="Enter the Minutes to reward")


# Shambling dead interface 
@auth.requires_membership('admins')
def zombieraise():
    import random
    response.view = 'admin/zombierewardfood.html'
    form = SQLFORM.factory(Field("Game", default=currentgame()),
                           Field("confirm", label="type: I AM SURE to confirm", default=""),
                           submit_button="RAISE THE DEAD!", )
    if form.process().accepted:
        if form.vars.confirm == "I AM SURE":
            zombies = db((db.game_part.game_id == form.vars.Game) & (db.game_part.creature_type != 1)).select()
            for zombie in zombies:
                if isdead(zombie):
                    stime = datetime.timedelta(seconds=random.randrange(10800, 43200))
                    newtime = request.now + stime
                    db(db.game_part.id == zombie.id).update(zombie_expires_at=newtime)
            status = "THE SHAMBLING DEAD HAVE ARISEN ONCE AGAIN!"
        return dict(form=[], status=status)
    return dict(form=form,
                status="Confirm the raising of the dead? All dead will be raised and given random amounts of food.")


# edit a cure page
@auth.requires_membership('admins')
def editcure():
    response.view = 'default.html'
    cure = db.cures(request.args(0)) or redirect(URL('error'))
    form = SQLFORM(db.cures, cure, deletable=True)
    if form.validate():
        if form.deleted:
            db(db.cures.id == cure.id).delete()
            redirect(URL('curelist'))
            response.flash = 'GAME BALEETED!'
        else:
            cure.update_record(**dict(form.vars))
            response.flash = 'Changes saved.'
    else:
        response.flash = 'Edit the cure.'
    return dict(form=form)


# Create a cure function
@auth.requires_membership('admins')
def createcure():
    game = gameinfo.getId()
    if not game:
        session.msg = 'Can only create a cure when there is a game active'
        redirect(URL(c='admin', f='curelist'))
    else:
        authid = auth.user.id
        db.cures.insert(game_id=gameinfo.getId(), curecode=generatecurecode(), used=False,
                        admincreator=authid,expiration=gameinfo.addFoodTimer())
        session.msg = 'Cure code created!'
        redirect(URL(c='admin', f='curelist'))


# The admin game page
@auth.requires_membership('admins')
def games():
    games = db(db.games).select(orderby=db.games.created)
    return dict(games=games)


# The create a game page
@auth.requires_membership('admins')
def creategame():
    response.view = 'default.html'
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
    response.view = 'default.html'
    game = db.games(request.args(0)) or redirect(URL('error'))
    form = SQLFORM(db.games, game, deletable=True)
    response.flash = 'Edit the game'
    if form.validate():
        if form.deleted:
            db(db.games.id == game.id).delete()
            redirect(URL('games'))
            response.flash = 'GAME BALEETED!'
        else:
            game.update_record(**dict(form.vars))
            response.flash = 'Changes saved.'
    else:
        response.flash = 'Edit the game!'
    return dict(form=form)


# View the game_part's in a game
@auth.requires_membership('admins')
def viewgameusers():
    gid = request.args[0]
    if db.games(gid):
        if request.args[1]:
            page = int(request.args[1])
        else:
            page = 0
        items_per_page = 40
        limitby = (page * items_per_page, (page + 1) * items_per_page + 1)
        response.flash = db.games(gid).game_name
        users = db(db.game_part.game_id == gid).select(orderby=db.game_part.id, limitby=limitby)
        return dict(users=users, page=page, items_per_page=items_per_page, gid=gid)
    else:
        redirect(URL(c='admin', f='games'))


# View the oz pool for a game
@auth.requires_membership('admins')
def ozlist():
    if request.args(0):
        gid = request.args(0)
        users = db((db.auth_user.id == db.game_part.user_id) & (db.game_part.game_id == request.args(0)) & (
            db.game_part.creature_type == db.creature_type.id) & (db.game_part.original_request == True)).select(
            db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle,
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
    response.view = 'default.html'
    form = SQLFORM(db.game_part)
    if form.process().accepted:
        response.flash = 'Game participation created'
    elif form.errors:
        response.flash = 'The game has errors, idiot!'
    return dict(form=form)


# Edit a game_part
@auth.requires_membership('admins')
def editgamepart():
    response.view = 'default.html'
    part = db.game_part(request.args(0)) or redirect(URL('error'))
    form = SQLFORM(db.game_part, part, deletable=True)
    if form.validate():
        if form.deleted:
            db(db.game_part.id == part.id).delete()
            redirect(URL('games'))
            response.flash = 'GAME BALEETED!'
        else:
            part.update_record(**dict(form.vars))
            response.flash = 'Changes saved.'
    else:
        response.flash = 'Edit the participation'
    return dict(form=form, )


# reset a bitecode function, arg 0 is game_part.id, arg 1 is auth_user.id
@auth.requires_membership('admins')
def regencode():
    if request.args[0] and request.args[1]:
        gid = request.args[0]
        db(db.game_part.id == gid).update(bitecode=generatebitecode())
        redirect(URL(c='admin', f='manage_user_parts', args=[request.args[1]]))
    else:
        redirect(URL(c='admin', f='manage_users'))


# Makes a user an OZ
@auth.requires_membership('admins')
def makeoz():
    db(db.game_part.id == request.args(0)).update(creature_type=3)
    userpart = db(db.game_part.id == request.args(0)).select()
    response.flash = 'made them an OZ!'
    redirect(URL(c='admin', f='ozlist', args=userpart[0].game_id))


# controller for the the open squad applications page
@auth.requires_membership('admins')
def squadapplist():
    squadsapp = db((db.auth_user.id == db.game_part.user_id) & (db.game_part.id == db.squads_app.leader) & (
        db.games.id == db.squads_app.game_id) & (db.squads_app.reviewed == "False")).select(
        db.squads_app.id, db.squads_app.name, db.squads_app.description, db.squads_app.image,
        db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.games.game_name,
        db.auth_user.id,
    )
    return dict(squadsapp=squadsapp)


# This function is for the admin squad review page. It rejects a squad application.
@auth.requires_membership('admins')
def denysquadapp():
    sappid = request.args[0]
    db(db.squads_app.id == sappid).update(reviewed=True, reviewer=auth.user.id)
    redirect(URL(c='admin', f='squadapplist'))


# This function is for the admin squad review page. It approves a squad application and creates it. It also makes the applicant the squad leader.
@auth.requires_membership('admins')
def approvesquadapp():
    sappid = request.args[0]
    sq = db.squads_app(sappid)
    db(db.squads_app.id == sappid).update(reviewed=True, approved=True, reviewer=auth.user.id)
    db.squads.insert(game_id=sq.game_id, name=sq.name, description=sq.description, image=sq.image, leader=sq.leader,
                     sigid=sq.sigid)
    search = db.squads.sigid.like(sq.sigid)
    results = db(search).select().first()
    db(db.game_part.id == sq.leader).update(squad_leader=True, squad_id=results.id)
    redirect(URL(c='admin', f='squadapplist'))


# controller for the the open registration requests page
@auth.requires_membership('admins')
def regrequestlist():
    regreq = db(
        (db.registration_request.user_id == db.auth_user.id) & (db.registration_request.game_id == db.games.id) & (
            db.registration_request.reviewed == False)).select(
        db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.games.id,
        db.games.game_name,
        db.auth_user.registration_id, db.registration_request.id, db.registration_request.reviewed,
        db.registration_request.approved,
        db.registration_request.appeal, db.registration_request.judgement, groupby=db.auth_user.id)
    return dict(regreq=regreq)


# This function is for the admin reg request review page. It rejects a reg request.
@auth.requires_membership('admins')
def denyregreq():
    regreqid = request.args[0]
    db(db.registration_request.id == regreqid).update(reviewed=True, approved=False, reviewer=auth.user.id)
    redirect(URL(c='admin', f='regrequestlist'))


# This function is for the admin reg request review page. It approves a reg reqest and creates a valid registration app.
@auth.requires_membership('admins')
def approveregreq():
    regcode = generatebitecode()
    regreqid = request.args[0]
    regreq = db.registration_request(regreqid)
    db(db.registration_request.id == regreqid).update(reviewed=True, approved=True, reviewer=auth.user.id)
    db.registration_app.insert(user_id=regreq.user_id, game_id=regreq.game_id, registration_code=regcode,
                               original_request=regreq.original_request, created=request.now,
                               registration_email=regreq.registration_email)
    message = "The Admins have approved your registration request! This is your registration code: * " + regcode + " *. Head to http://umasshvz.com to use it."
    sendemail(regreq.registration_email, "HvZ Registration code", message)
    redirect(URL(c='admin', f='regrequestlist'))

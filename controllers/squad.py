# This is for squad-related controllers


# The public squadlist
def squadlist():
    gpart = returncurrentuserpart()
    if not gameinfo.getId() and not request.args(0):
        msg = 'No current or upcoming game!'
        return dict(squads=False, gid=False,msg=msg)
    elif request.args(0):
        squads=db(db.squads.game_id==request.args(0)).select(orderby='<random>')
        msg= ''
        return dict(squads=squads, gid=request.args(0),msg=msg)
    elif gameinfo.getId():
        if gpart:
            if not gpart.game_part.squad_id and not gpart.game_part.squad_apps:
                msg = A("Create Squad", _class='btn btn-success btn-lg pull-right', _href=URL(c='squad', f='createsquadapp'))
            else:
                msg= ''
        else:
            msg= ''
        squads=db(db.squads.game_id==gameinfo.getId()).select(orderby='<random>')
        return dict(squads=squads, gid=False,msg=msg)


# squad info page
def squadinfo():
     squad = db.squads(request.args(0)) or redirect(URL(c='gamectrl',f='squadlist'))
     try:
         gpart=returncurrentuserpart()
     except:
         gpart=False
     players = db((db.auth_user.id==db.game_part.user_id) & (db.creature_type.id==db.game_part.creature_type) & (db.squads.id==db.game_part.squad_id) & (db.squads.id==request.args(0))).select(
             db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.auth_user.registration_id,
             db.creature_type.name, db.game_part.zombie_expires_at, db.game_part.squad_title,
             db.game_part.squad_leader,orderby=db.game_part.created)
     if squad and gpart:
         #checks if the view should display a registration button or not
         if not isZombieDead(gpart) and not gpart.game_part.squad_apps and not gpart.game_part.squad_id:
             app=True
         else:
             app=False
         return dict(squad=squad,players=players, app=app, gpart=gpart)
     else:
         return dict(squad=squad,players=players, app=False)


# This is the controller for the squad creation application page.
@auth.requires_login()
def createsquadapp():
    response.view = 'default.html'
    gpart = returncurrentuserpart()
    gid = gameinfo.getId()
    if gid and not (gpart.game_part.squad_id or gpart.game_part.squad_apps or isZombieDead(gpart)):
        form = SQLFORM(db.squads_app, fields=['name', 'description', 'image', ],
                       labels={'name': 'Your Squad Name', 'image': 'MUST BE 960px x 240px'},
                       submit_button="Submit Squad Application", )
        form.vars.leader = gpart.game_part.id
        form.vars.game_id = gid
        form.vars.sigid = generatebitecode()
        if form.process().accepted:
            db(db.game_part.id == gpart.game_part.id).update(squad_apps=1)
            form = "Squad Application Created!"
            return dict(form=form)
        return dict(form=form)
    elif gpart.game_part.squad_apps:
        form = "You already have a pending squad application!"
        return dict(form=form)
    elif gpart.game_part.squad_id:
        form = "You are already affiliated with a squad this game!"
    else:
        form = "Squad application form locked."
        return dict(form=form)


# This is the controller for the squad hq page for squad members.
@auth.requires_login()
def squadhq():
    squad = db.squads(request.args[0]) or redirect(URL(c='default', f='index'))
    gpart = returncurrentuserpart()
    if gpart.game_part.squad_id == request.args[0]:
        if squad:
            posts = db(db.squad_posts.squad_id == request.args(0)).select(orderby=~db.squad_posts.created)
            members = db(
                (db.auth_user.id == db.game_part.user_id) & (db.game_part.creature_type == db.creature_type.id) & (
                    db.squads.id == db.game_part.squad_id) & (db.squads.id == request.args[0])).select(
                db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.auth_user.id,
                db.game_part.zombie_expires_at, db.game_part.squad_leader, db.game_part.squad_title,
                db.creature_type.name, db.creature_type.zombie, db.creature_type.immortal,
                db.squads.name, db.squads.description, db.squads.image,
                orderby=db.game_part.created)
            return dict(squad=squad, posts=posts, members=members)
    else:
        redirect(URL(c='default', f='index'))


# View squad post page.
@auth.requires_login()
def viewsquadpost():
    post = db.squad_posts[request.args(0)] or redirect(URL(r=request, f='index'))
    gpart = returncurrentuserpart()
    if int(gpart.game_part.squad_id) == int(post.squad_id):
        squad = db.squads(post.squad_id)
        return dict(post=post, squad=squad)


# This is the controller for the squad admin page for squad leaders.
@auth.requires_login()
def squadadmin():
    squad = db.squads(request.args(0)) or redirect(URL(c='default', f='index'))
    gpart = returncurrentuserpart()
    if gpart.game_part.squad_id == request.args(0) and gpart.game_part.squad_leader:
        if squad:
            posts = db(db.squad_posts.squad_id == request.args(0)).select(orderby=~db.squad_posts.created)
            members = db(
                (db.auth_user.id == db.game_part.user_id) & (db.game_part.creature_type == db.creature_type.id) & (
                    db.squads.id == db.game_part.squad_id) & (db.squads.id == request.args[0])).select(
                db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.auth_user.id,
                db.game_part.zombie_expires_at, db.game_part.squad_leader, db.game_part.squad_title,
                db.creature_type.name, db.creature_type.zombie, db.creature_type.immortal, db.game_part.id,
                db.squads.name, db.squads.description, db.squads.image,
                orderby=db.game_part.created)
            squadsmemapp = db(
                (db.auth_user.id == db.game_part.user_id) & (db.game_part.creature_type == db.creature_type.id) &
                (db.squads_member_app.player_id == db.game_part.id) & (db.squads_member_app.squad_id == squad.id) &
                (db.squads_member_app.reviewed == False)).select()
            return dict(squad=squad, members=members, squadsmemapp=squadsmemapp, posts=posts)
    else:
        redirect(URL(c='default', f='index'))


# Create a post page
@auth.requires_login()
def createsquadpost():
    response.view = 'default.html'
    request.args(0) or redirect(URL(c='default', f='index'))
    gpart = returncurrentuserpart()
    if gpart.game_part.squad_id == request.args(0) and gpart.game_part.squad_leader:
        response.flash = "Create a post!"
        form = SQLFORM(db.squad_posts, fields=['title', 'description'])
        form.vars.sleader = gpart.game_part.id
        form.vars.squad_id = gpart.game_part.squad_id
        if form.process().accepted:
            session.flash = 'Post accepted.'
            form=A('Back to SL Admin',_href=URL('squad', 'squadadmin', args=gpart.game_part.squad_id), _class="btn btn-default")
        elif form.errors:
            session.flash = 'The post has errors, idiot!'
        return dict(form=form)


# Edit a post page
@auth.requires_login()
def editsquadpost():
    response.view = 'default.html'
    request.args(0) or redirect(URL(c='default', f='index'))
    gpart = returncurrentuserpart()
    post = db.squad_posts(request.args(0))
    if int(post.squad_id) == int(gpart.game_part.squad_id) and gpart.game_part.squad_leader:
        form = SQLFORM(db.squad_posts, post, showid=False, fields=['title', 'description'], deletable=True)
        session.flash = 'Edit the post!'
        if form.validate():
            if form.deleted:
                db(db.squad_posts.id == post.id).delete()
                redirect(URL(c='squad', f='squadadmin', args=gpart.game_part.squad_id))
                session.flash = 'POST BALEETED!'
            else:
                post.update_record(**dict(form.vars))
                session.flash = 'Changes saved.'
        else:
            session.flash = 'Edit the post!'
        return dict(form=form)
    else:
        redirect(URL(c='default', f='index'))


# This function is for the SL admin page. It rejects a member application and makes the neccesary database updates.
@auth.requires_login()
def denysquadmemberapp():
    smemappid = request.args[0]
    sq = db.squads_member_app(smemappid)
    gpart = returncurrentuserpart()
    sqd = db.squads(sq.squad_id)
    if gpart.game_part.id == sqd.leader:
        db(db.squads_member_app.id == smemappid).update(reviewed=True)
        redirect(URL(c='squad', f='squadadmin', args=gpart.game_part.squad_id))
    else:
        redirect(URL(c='default', f='index'))


# This function is for the SL admin page. It approves a member application and makes the neccesary database updates.
@auth.requires_login()
def approvesquadmemberapp():
    sid = request.args[0]
    sq = db.squads_member_app(sid)
    gpart = returncurrentuserpart()
    sqd = db.squads(sq.squad_id)
    if gpart.game_part.id == sqd.leader:
        db(db.squads_member_app.id == sid).update(reviewed=True, approved=True)
        db(db.game_part.id == sq.player_id).update(squad_id=sq.squad_id, squad_apps=1)
        redirect(URL(c='squad', f='squadadmin', args=gpart.game_part.squad_id))
    else:
        redirect(URL(c='default', f='index'))


# function for people to apply to a squad
@auth.requires_login()
def applytosquad():
    gpart = returncurrentuserpart()
    if request.args[0] and not gpart.game_part.squad_apps and not gpart.game_part.squad_id:
        squadinfo = db.squads(request.args[0])
        form = FORM(DIV(TEXTAREA(_style="width: 100%;", _name="Application", _id="appbody")), INPUT
        (_type="submit", _value="Apply"))
        if form.process(session=None, formname='squadapp').accepted:
            if not gpart.game_part.squad_id:
                squadapp = db((db.squads_member_app.player_id == gpart.game_part.id) & (db.squads_member_app.reviewed == False)).select()
                # checks for an existing squad application. if one exists it just updates that one instead of making a new one.
                if squadapp:
                    db(db.squads_member_app.player_id == gpart.game_part.id).update(squad_id=request.args[0],
                                                                                    description=form.vars.Application)
                else:
                    db.squads_member_app.insert(player_id=gpart.game_part.id, squad_id=request.args[0],
                                                description=form.vars.Application)
            session.flash = 'Application sent!'
            form = ''
        elif form.errors:
            session.flash = 'Form has errors'
        else:
            session.flash = 'Tell them why they should let you in!'
        return dict(form=form, squadinfo=squadinfo)


# function for squad leaders to change people's titles
@auth.requires_login()
def squadtitlechange():
    response.view = 'default.html'
    uid = request.args[0]
    gpart = returncurrentuserpart()
    if gpart.game_part.squad_leader and db.game_part(uid).squad_id == gpart.game_part.squad_id:
        sqmember = db.game_part(uid) or redirect(URL('error'))
        form = SQLFORM(db.game_part, sqmember, showid=False, fields=['squad_title'])
        if form.validate():
            sqmember.update_record(**dict(form.vars))
            session.flash = 'Changes saved'
            form=A('Back to SL Admin',_href=URL('squad', 'squadadmin', args=gpart.game_part.squad_id), _class="btn btn-default")
        else:
            session.flash = 'Change member title'
        return dict(form=form)


# kick squad member function
@auth.requires_login()
def kickmember():
    uid = request.args[0]
    mem = db.game_part(uid)
    gpart = returncurrentuserpart()
    # checks to make sure that the person getting kicked is in the squad of the person calling the controller and that they are the leader
    if mem.squad_id == gpart.game_part.squad_id and gpart.game_part.squad_leader:
        db(db.game_part.id == uid).update(squad_id=None, squad_title='', squad_apps=None)
        db(db.squads_member_app.player_id == uid).delete()
        redirect(URL(c='squad', f='squadadmin', args=mem.squad_id))
    else:
        redirect(URL(c='default', f='index'))

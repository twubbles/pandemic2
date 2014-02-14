# coding: utf8

# Index redirects to the default index controller
def index():
    redirect(URL(c='default', f='index'))


# events page
def eventfeed():
    events = db.executesql('SELECT * FROM bite_event ORDER BY id DESC;', as_dict=True)
    zombienames = db((db.auth_user.id == db.game_part.user_id) & (db.game_part.game_id == currentgame())).select(
        db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.game_part.id)
    return dict(events=events, zombienames=zombienames)


@auth.requires_login()
def resetregistration():
    if not returncurrentuserpart() and returncurrentuserapp() and gameinfo.checkReg():
        authid = auth.user.id
        db((db.registration_app.user_id == authid) & (db.registration_app.game_id == gameinfo.getId())).delete()
        redirect(URL(c='gamectrl', f='register'))
    else:
        redirect(URL(c='gamectrl', f='register'))


# controller for five-college student registration request
@auth.requires_login()
def register():
    if not returncurrentuserpart() and not returncurrentuserapp() and gameinfo.checkReg():
        form = SQLFORM.factory(Field("address", default='address@umass.edu'),
                               Field("Original", 'boolean', label="Original Zombie Request", ),
                               buttons=[
                                   TAG.button('Register', _type="submit", _class="btn btn-primary btn-lg btn-block")],
                               _class="table-noborder")
        if form.process().accepted:
            useremail = form.vars.address
            emails = db(db.emails).select()
            emaildoms = []
            for dom in emails:
                emaildoms.append(dom.email)
            esplit = useremail.rsplit('@')
            if esplit[1] in emaildoms:
                authid = auth.user.id
                regcode = generatebitecode()
                message = "This is your registration code: * " + regcode + " *. Head to http://leetmeatgolem.pythonanywhere.com/pandemic/gamectrl/register to use it."
                results = sendemail(useremail, "HvZ Registration code", message)
                db.registration_app.insert(user_id=authid, game_id=gameinfo.getId(), registration_code=regcode,
                                           original_request=form.vars.Original, created=request.now,
                                           registration_email=useremail)
                return dict(form="Check your email and refresh this page!", results=results, fbpost=False)
            else:
                session.flash = "invalid email or domain"
                return dict(form=form, results=[], fbpost=False)
        else:
            return dict(form=form, results=[], fbpost=False)
        return dict(form=form, results=[])
    elif not returncurrentuserpart() and returncurrentuserapp() and gameinfo.checkReg():
        session.flash = "Enter the code from your email"
        form = SQLFORM.factory(Field("regcode", label='Registration Code ', default=''), submit_button="Register me!", )
        if form.process().accepted:
            search = db.registration_app.game_id == gameinfo.getId()
            ccode = form.vars.regcode
            ccode = ccode.replace(' ', '').upper()
            if ccode:
                search = db.registration_app.registration_code.like(ccode)
                regapp = db(search).select().first()
                if regapp:
                    db.game_part.insert(user_id=regapp.user_id, game_id=regapp.game_id, bitecode=generatebitecode(),
                                        registration_email=regapp.registration_email,
                                        original_request=regapp.original_request, creature_type=1,
                                        zombie_expires_at=request.now)
                    db(db.registration_app.id == regapp.id).update(reviewed=True)
                    results = auth.user.first_name + " just registered for Humans vs Zombies!!"
                    session.flash = results
                    return dict(form=form, results=results, fbpost=True)
                else:
                    results = "Code didn't work!"
                    session.flash = "Code didn't work!"
                    return dict(form=form, results=results, fbpost=False)
        return dict(form=form, results="Enter your registration code", fbpost=False)
    elif not gameinfo.checkReg():
        return dict(form="Registration is Closed", results="Registration is Closed", fbpost=False)


# controller for non-five-college student registration request
@auth.requires_login()
def registerrequest():
    if gameinfo.checkReg() and not (returncurrentuserpart() or returncurrentuserapp() or returncurrentuserreqapp()):
        form = SQLFORM.factory(
            Field("address", default='address@email.com', requires=IS_NOT_EMPTY()),
            Field("original", 'boolean', label="Original Zombie Request ", ),
            Field("appeal", 'text', requires=IS_NOT_EMPTY(), label="Appeal ",
                  default="Reason why you should play even though you don't have a five-college email. Ex: Alumni, friend of student, visiting from another school, etc. Alums must state year of graduation. Friends of students must state the student they are friends with. Visitors must tell us what school they are from."),
        )
        if form.process().accepted:
            try:
                authid = auth.user.id
                useremail = form.vars.address
                db.registration_request.insert(
                    user_id=authid, game_id=gameinfo.getId(), original_request=form.vars.original,
                    registration_email=useremail, appeal=form.vars.appeal, created=request.now
                )
                message = "We have recieved your registration request and the game admins will review it promptly. A decision will be sent to you via email."
                sendemail(useremail, "HvZ Registration Request", message)
                return dict(form="Check your email.")
            except Exception:
                session.flash = "Invalid email"
                return dict(form=form)
        else:
            return dict(form=form)
        return dict(form=form)
    else:
        return dict(form="Registration is Closed")


#  Returns the page for cures. Uses variables defined in the menu.py model statusmenu function
@auth.requires_login()
def curezombie():
    response.view = 'default.html'
    # checks if user is logged in, a zombie, and not dead
    gpart = returncurrentuserpart()
    if gpart.creature_type.zombie and not isZombieDead(gpart):
        form = SQLFORM.factory(Field("Curecode", default=''), submit_button="Cure Me!", )
        if form.process().accepted:
            ccode = form.vars.Curecode
            ccode = ccode.replace(' ', '').upper()
            if ccode:
                search = db.cures.curecode.like(ccode)
                results = db(search & (db.games.id == db.cures.game_id)).select().first()
                if results:
                    forcurrentgame = (gameinfo.getId() == results.cures.game_id)
                    infected = gameinfo.checkInfection(gpart)
                    expired = isExpiredCure(results)
                    # checks to see if the curecode is not used/expired, for the current game, and that the player is not infected.
                    if forcurrentgame and not (results.cures.used or expired or infected):
                        db.cure_event.insert(player_id=gpart.game_part.id, game_id=gameinfo.getId(),
                                             cure_id=results.cures.id)
                        db(db.cures.id == results.cures.id).update(used=True, cure_user=gpart.game_part.id)
                        db(db.game_part.id == gpart.game_part.id).update(creature_type=1, bitecode=generatebitecode())
                        # results is changed to the text to appear in the facebook post and passed to the view.
                        results = gpart.auth_user.first_name + " " + gpart.auth_user.last_name + ' used a cure and is human again!'
                        session.flash = results
                        form = ''
                        return dict(form=form, results=results)
                    elif results.cures.used and forcurrentgame:
                        session.flash = 'This code has been used already!'
                        return dict(form=form, results=[])
                    elif expired and forcurrentgame:
                        session.flash = 'This code has expired!'
                        return dict(form=form, results=[])
                    elif not forcurrentgame:
                        session.flash = 'This code is for an older game!'
                        return dict(form=form, results=[])
                    elif infected:
                        session.flash = 'Your infection is irreversible!'
                        return dict(form=form, results=[])
                else:
                    session.flash = 'Invalid Cure code'
                    return dict(form=form, results=[])
            else:
                session.flash = 'Invalid Cure code'
                return dict(form=form, results=[])
        else:

            return dict(form=form, results=[])
    else:
        redirect(URL(c='default', f='index'))


# Returns the page for biting. Uses variables defined in the menu.py model statusmenu function
@auth.requires_login()
def bitecodepg():
    response.view = 'default.html'
    form = ''
    gpart = returncurrentuserpart()
    if gpart.creature_type.zombie and not isZombieDead(gpart):
        if request.args(0):
            bcode = request.args(0)
            bcode = bcode.replace(' ', '').upper()
            if bcode:
                search = db.game_part.bitecode.like(bcode)
                results = db((search) & (db.auth_user.id == db.game_part.user_id) & (
                    db.creature_type.id == db.game_part.creature_type) & (
                                 db.game_part.game_id == gameinfo.getId())).select().first()
                if results:
                    if results.creature_type.zombie:
                        session.flash = 'You tried to bite a zombie! ewww!'
                        return dict(form=form, results=[])
                    else:
                        # results is changed to the text to appear in the facebook post and passed to the view.
                        results = gpart.auth_user.first_name + ' ' + gpart.auth_user.last_name + ' bit ' + \
                                  results.auth_user.first_name + ' ' + results.auth_user.last_name
                        db.bite_event.insert(zombie_id=gpart.game_part.id, human_id=results.game_part.id,
                                             game_id=gameinfo.getId(), lat=request.args(1), lng=request.args(2))
                        db(db.game_part.id == gpart.game_part.id).update(zombie_expires_at=gameinfo.addFoodTimer())
                        db(db.game_part.id == human).update(zombie_expires_at=gameinfo.addFoodTimer(), creature_type=2)
                        session.flash = results
                        return dict(form=form, results=results)
                else:
                    session.flash = 'Invalid Bitecode'
                    return dict(form=form, results=[])
            else:
                session.flash = 'Invalid Bitecode'
                return dict(form=form, results=[])
        form = SQLFORM.factory(Field("Bitecode", default=''), Field("Latitude", default='0', writable=True),
                               Field("Longitude", default='0', writable=True), submit_button="Bite!", )
        if form.process().accepted:
            search = db.game_part.game_id == currentgame()
            bcode = form.vars.Bitecode
            bcode = bcode.replace(' ', '').upper()
            if bcode:
                search = db.game_part.bitecode.like(bcode)
                results = db((search) & (db.auth_user.id == db.game_part.user_id) & (
                    db.creature_type.id == db.game_part.creature_type) & (
                                 db.game_part.game_id == gameinfo.getId())).select().first()
                if results:
                    if results.creature_type.zombie:
                        session.flash = 'You tried to bite a zombie! ewww!'
                        return dict(form=form, results=[])
                    else:
                        # results is changed to the text to appear in the facebook post and passed to the view.
                        results = gpart.auth_user.first_name + ' ' + gpart.auth_user.last_name + ' bit ' + \
                                  results.auth_user.first_name + ' ' + results.auth_user.last_name
                        db.bite_event.insert(zombie_id=gpart.game_part.id, human_id=results.game_part.id,
                                             game_id=gameinfo.getId(), lat=form.vars.Latitude, lng=form.vars.Longitude)
                        db(db.game_part.id == gpart.game_part.id).update(zombie_expires_at=gameinfo.addFoodTimer())
                        db(db.game_part.id == human).update(zombie_expires_at=gameinfo.addFoodTimer(), creature_type=2)
                        session.flash = results
                        return dict(form=form, results=results)
                else:
                    session.flash = 'Invalid Bitecode'
                    return dict(form=form, results=[])
            else:
                session.flash = 'Invalid Bitecode'
                return dict(form=form, results=[])
        else:

            return dict(form=form, results=[])
    else:
        redirect(URL(c='default', f='index'))


# Function for creating original zombies from the OZ pool.
@auth.requires_membership('admins')
def makeoz():
    db(db.game_part.id == request.args(0)).update(creature_type=3)
    userpart = db(db.game_part.id == request.args(0)).select()
    response.flash = 'made them an OZ!'
    redirect(URL(c='admin', f='ozlist', args=userpart[0].game_id))


# This is the controller function for the squad application page.
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
            posts = db(db.squad_posts.squad_id == request.args(0)).select(orderby=~db.squad_posts.created, )
            members = db((db.game_part.squad_id == squad.id) & (db.game_part.squad_leader == False)).select(
                orderby=db.game_part.created)
            leader = db.game_part(squad.leader)
            return dict(squad=squad, posts=posts, members=members, leader=leader)
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
            posts = db(db.squad_posts.squad_id == request.args(0)).select(orderby=~db.squad_posts.created, )
            members = db((db.game_part.squad_id == squad.id) & (db.game_part.squad_leader == False)).select(
                orderby=db.game_part.created)
            leader = db.game_part(squad.leader)
            squadsmemapp = db(
                (db.squads_member_app.squad_id == squad.id) & (db.squads_member_app.reviewed == False)).select()
            return dict(squad=squad, members=members, leader=leader, squadsmemapp=squadsmemapp, posts=posts)
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
    if int(post.game_part.squad_id) == int(gpart.game_part.squad_id) and gpart.game_part.squad_leader:
        form = SQLFORM(db.squad_posts, post, showid=False, fields=['title', 'description'], deletable=True)
        session.flash = 'Edit the post!'
        if form.validate():
            if form.deleted:
                db(db.squad_posts.id == post.id).delete()
                redirect(URL(c='gamectrl', f='squadadmin', args=gpart.game_part.squad_id))
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
        redirect(URL(c='gamectrl', f='squadadmin', args=gpart.game_part.squad_id))
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
        redirect(URL(c='gamectrl', f='squadadmin', args=gpart.game_part.squad_id))
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
            if not appart.squad_id:
                squadapp = db(db.squads_member_app.player_id == gpart.game_part.id).select()
                # checks for an existing squad application. if one exists it just updates that one instead of making a new one.
                if squadapp:
                    db(db.squads_member_app.player_id == gpart.game_part.id).update(squad_id=request.args[0],
                                                                                    description=form.vars.Application)
                else:
                    db.squads_member_app.insert(player_id=gpart.game_part.id, squad_id=request.args[0],
                                                description=form.vars.Application)
            session.flash = 'Application sent! You will get an email with the decision.'
        elif form.errors:
            session.flash = 'form has errors'
        else:
            session.flash = 'Tell them why they should let you in:'
        return dict(form=form, squadinfo=squadinfo, msg=msg)


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
        redirect(URL(c='gamectrl', f='squadadmin', args=mem.squad_id))
    else:
        redirect(URL(c='default', f='index'))


# human bitecode qrcode page
@auth.requires_login()
def bitecodeqrcodepage():
    gpart = returncurrentuserpart()
    gpart.creature_type.zombie
    if not gpart.creature_type.zombie:
        return dict(gpart=gpart)
    else:
        redirect(URL(c='default', f='index'))

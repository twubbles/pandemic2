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
                    db.game_part.creature_type == db.creature_type.id) & (db.games.id == db.game_part.game_id) & (
                                 db.games.id == gameinfo.getId())).select().first()
                if results:
                    if results.creature_type.zombie:
                        session.flash = 'You tried to bite a zombie! ewww!'
                        return dict(form=form, results=[])
                    else:
                        db.bite_event.insert(zombie_id=gpart.game_part.id, human_id=results.game_part.id,
                                             game_id=gameinfo.getId(), lat=request.args(1), lng=request.args(2))
                        db(db.game_part.id == gpart.game_part.id).update(zombie_expires_at=gameinfo.addFoodTimer())
                        db(db.game_part.id == results.game_part.id).update(zombie_expires_at=gameinfo.addFoodTimer(),
                                                                           creature_type=2)
                        # results is changed to the text to appear in the facebook post and passed to the view.
                        results = gpart.auth_user.first_name + ' ' + gpart.auth_user.last_name + ' bit ' + \
                                  results.auth_user.first_name + ' ' + results.auth_user.last_name
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
                        db.bite_event.insert(zombie_id=gpart.game_part.id, human_id=results.game_part.id,
                                             game_id=gameinfo.getId(), lat=form.vars.Latitude, lng=form.vars.Longitude)
                        db(db.game_part.id == gpart.game_part.id).update(zombie_expires_at=gameinfo.addFoodTimer())
                        db(db.game_part.id == results.game_part.id).update(zombie_expires_at=gameinfo.addFoodTimer(),
                                                                           creature_type=2)
                        # results is changed to the text to appear in the facebook post and passed to the view.
                        results = gpart.auth_user.first_name + ' ' + gpart.auth_user.last_name + ' bit ' + \
                                  results.auth_user.first_name + ' ' + results.auth_user.last_name
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




# human bitecode qrcode page
@auth.requires_login()
def bitecodeqrcodepage():
    gpart = returncurrentuserpart()
    gpart.creature_type.zombie
    if not gpart.creature_type.zombie:
        return dict(gpart=gpart)
    else:
        redirect(URL(c='default', f='index'))

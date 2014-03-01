# coding: utf8

# Index redirects to the default index controller
def index():
    redirect(URL(c='default', f='index'))


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
                               buttons=[TAG.button('Register', _type="submit", _class="btn btn-primary btn-lg btn-block")],
                               _class="table-noborder")
        if form.process(onvalidation=validateumassemail).accepted:
            useremail = form.vars.address
            emails = db(db.emails).select()
            emaildoms = []
            for dom in emails:
                emaildoms.append(dom.email)
            esplit = useremail.rsplit('@')
            if esplit[1] in emaildoms:
                authid = auth.user.id
                regcode = generatebitecode()
                message = "This is your registration code: * " + regcode + " *. Head to http://www.umasshvz.com/pandemic/gamectrl/register to use it."
                sendemail(useremail, "HvZ Registration code", message)
                db.registration_app.insert(user_id=authid, game_id=gameinfo.getId(), registration_code=regcode,
                                           original_request=form.vars.Original, created=getEstNow(),
                                           registration_email=useremail)
                return dict(form="", results='', fbpost=False, askemail="Check your email and refresh this page!")
            else:
                session.flash = "invalid email or domain"
                return dict(form=form, results=[], fbpost=False, askemail="Use your five college email to sign up!")
        else:
            return dict(form=form, results=[], fbpost=False, askemail="Use your five college email to sign up!")
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
                    newcode = generatebitecode()
                    db.game_part.insert(user_id=regapp.user_id, game_id=regapp.game_id, bitecode=newcode,
                                        registration_email=regapp.registration_email,
                                        original_request=regapp.original_request, creature_type=1,
                                        zombie_expires_at=getEstNow())
                    db(db.registration_app.id == regapp.id).update(reviewed=True)
                    results = auth.user.first_name + " just registered for Humans vs Zombies!!"
                    session.flash = results
                    form=''
                    message = "You have successfully registered for " + gameinfo.getName() + "! Your bitecode is: " + str(newcode) + " write it down and give it to the zombie that bites you."
                    message = message + " Also, you can always find it again at: http://www.umasshvz.com/pandemic/gamectrl/bitecodeqrcodepage along with a QR code that a zombie can scan with their phone to bite you instead. "
                    message = message + " Good luck and remember to read the rules @ http://www.umasshvz.com/pandemic/default/rules "
                    message = message + " If you have any issues/problems/questions, you can reach the admin team @ admin@umasshvz.com"
                    message = message + "  --- UMASSHvZ --- "
                    sendemail(regapp.registration_email, "HvZ Welcome to " + gameinfo.getName(), message)
                    return dict(form="", results='', fbpost=True, askemail="You just registered!")
                else:
                    results = "Code didn't work!"
                    session.flash = "Code didn't work!"
                    return dict(form=form, results=results, fbpost=False)
        return dict(form=form, results="", fbpost=False, askemail="Enter the registration code from your email")
    elif not gameinfo.checkReg():
        return dict(form="Registration is Closed", results="", fbpost=False, askemail='Registration is Closed')


# controller for non-five-college student registration request
@auth.requires_login()
def registerrequest():
    if gameinfo.checkReg() and not returncurrentuserpart() and not (returncurrentuserapp() or returncurrentuserreqapp()):
        form = SQLFORM.factory(
            Field("address", default='address@email.com', requires=IS_NOT_EMPTY()),
            Field("original", 'boolean', label="OZ Request ", ),
            Field("appeal", 'text', requires=IS_NOT_EMPTY(), label="Appeal ",
                  default="Reason why you should play. Ex: Alumni, friend of student, visiting from another school, etc. Alums must state year of graduation. Friends of students must state the student they are friends with. Visitors must tell us what school they are from."),
        )
        if form.process(onvalidation=validateemail).accepted:
            try:
                authid = auth.user.id
                useremail = form.vars.address
                db.registration_request.insert(
                    user_id=authid, game_id=gameinfo.getId(), original_request=form.vars.original,
                    registration_email=useremail, appeal=form.vars.appeal, created=getEstNow()
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
                        session.flash = gpart.auth_user.first_name + " " + gpart.auth_user.last_name + ' used a cure and is human again!'
                        form = ''
                        return dict(form=form)
                    elif results.cures.used and forcurrentgame:
                        session.flash = 'This code has been used already!'
                        return dict(form=form)
                    elif expired and forcurrentgame:
                        session.flash = 'This code has expired!'
                        return dict(form=form)
                    elif not forcurrentgame:
                        session.flash = 'This code is for an older game!'
                        return dict(form=form)
                    elif infected:
                        session.flash = 'Your infection is irreversible!'
                        return dict(form=form)
                else:
                    session.flash = 'Invalid Cure code'
                    return dict(form=form)
            else:
                session.flash = 'Invalid Cure code'
                return dict(form=form)
        else:

            return dict(form=form, results=[])
    else:
        redirect(URL(c='default', f='index'))


# Returns the page for biting. Uses variables defined in the menu.py model statusmenu function
@auth.requires_login()
def bitecodepg():
    form = ''
    gpart = returncurrentuserpart()
    if request.args(0):
        defbitecode = request.args(0)
    else:
        defbitecode = "enter code here"
    if (gpart.creature_type.zombie or gpart.creature_type.hidden) and not isZombieDead(gpart):
        form = gameinfo.buildBiteForm(defbitecode)
        if form.process(onvalidation=validategeo).accepted:
            search = db.game_part.game_id == gameinfo.getId()
            bcode = form.vars.Bitecode
            lat=form.vars.Lat
            long=form.vars.Long
            share=form.vars.share
            timeshared=form.vars.timeshared
            bcode = bcode.replace(' ', '').upper()
            if bcode:
                search = db.game_part.bitecode.like(bcode)
                results = db((search) & (db.auth_user.id == db.game_part.user_id) & (db.creature_type.id == db.game_part.creature_type) & (
                                 db.game_part.game_id == gameinfo.getId())).select().first()
                if results:
                    if results.creature_type.zombie or results.creature_type.hidden:
                        session.flash = 'You tried to bite a zombie! ewww!'
                        return dict(form=form, results=[])
                    else:

                        # check if the bite is shared
                        if share:

                            # check if the time shared is within acceptable values
                            if not (timeshared > gameinfo.minShare() or timeshared < gameinfo.maxShare()):
                                session.flash = 'Invalid time to share'
                                redirect(URL(c='default', f='index', args=bcode))
                            else:
                                timetoshare = gameinfo.timePerFood() - timeshared
                            timetoadd = (gpart.game_part.zombie_expires_at + timedelta(seconds=timetoshare))
                            if timetoadd > gameinfo.addFoodTimer():
                                timetoadd = gameinfo.addFoodTimer()
                            biteid = db.bite_event.insert(zombie_id=gpart.game_part.id, human_id=results.game_part.id,
                                             game_id=gameinfo.getId(), lat=lat, lng=long)
                            db.bite_share.insert(game_id=gameinfo.getId(),share_id=gpart.game_part.id, time_shared=timeshared, bite_id=biteid)

                        else:
                            timetoadd = gameinfo.addFoodTimer()
                            db.bite_event.insert(zombie_id=gpart.game_part.id, human_id=results.game_part.id,
                                             game_id=gameinfo.getId(), lat=lat, lng=long)

                        # checks if zombie is a hidden OZ or not and updates their status accordingly
                        if gpart.creature_type.hidden:
                            db(db.game_part.id == gpart.game_part.id).update(zombie_expires_at=timetoadd,creature_type=3)
                        else:
                            db(db.game_part.id == gpart.game_part.id).update(zombie_expires_at=timetoadd)

                        # updates the bitten human's status and starve timer
                        db(db.game_part.id == results.game_part.id).update(zombie_expires_at=gameinfo.addFoodTimer(),
                                                                           creature_type=2)
                        # results is changed to the text to appear in the facebook post and passed to the view.
                        session.flash = gpart.auth_user.first_name + ' ' + gpart.auth_user.last_name + ' bit ' + \
                                  results.auth_user.first_name + ' ' + results.auth_user.last_name
                        results=session.flash
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
    if not (gpart.creature_type.zombie or gpart.creature_type.hidden):
        return dict(gpart=gpart)
    elif gpart.creature_type.hidden:
        redirect(URL('gamectrl', 'bitecodepg'))
    else:
        redirect(URL(c='default', f='index'))


# displays a zombie's biteshares
@auth.requires_login()
def biteshare():
    gpart = returncurrentuserpart()
    if gpart.creature_type.zombie and not isZombieDead(gpart):
        savedbites = db((db.bite_share.share_id == gpart.game_part.id) & (db.bite_share.game_id == gameinfo.getId())).select(
                        db.bite_share.ALL, db.auth_user.id, db.auth_user.first_name,db.auth_user.last_name, db.game_part.id,
                        db.game_part.user_id,
                        left=(db.game_part.on(db.game_part.id == db.bite_share.shared_with),db.auth_user.on(db.auth_user.id == db.game_part.user_id))
                        )
        return dict(form='', savedbites=savedbites, gpart=gpart)
    else:
        redirect(URL(c='default', f='index'))

# controller to choose the zombie to share a bite with
@auth.requires_login()
def shareabite():
    if request.args(0):
        gpart = returncurrentuserpart()
        biteshare = db.bite_share(request.args(0))
        if gpart.creature_type.zombie and not isZombieDead(gpart):
            if gpart.game_part.id == biteshare.share_id:
                zombies = db((db.auth_user.id == db.game_part.user_id) & (db.game_part.game_id == gameinfo.getId()) & (
            db.game_part.creature_type == db.creature_type.id)& (db.creature_type.zombie == True)).select(
            db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.game_part.id,
            db.creature_type.zombie, db.creature_type.name, db.game_part.zombie_expires_at, db.creature_type.immortal,
            cache=(cache.ram, 60), cacheable=True)

                return dict(zombies=zombies, biteshare=biteshare)
            else:
                redirect(URL(c='default', f='index'))

# Controller that actually shares a bite with a zombie
@auth.requires_login()
def sharewithzed():
    if request.args(0) and request.args(1):
        gpart = returncurrentuserpart()
        biteshare = db.bite_share(request.args(1))
        zombie = db.game_part(request.args(0))
        if gpart.creature_type.zombie and not isZombieDead(gpart):
            if (gpart.game_part.id == biteshare.share_id) and converttotz(zombie.zombie_expires_at) > getesttime() and not biteshare.is_share_used:

                mins = biteshare.time_shared/60
                diff = getesttime() - biteshare.created
                newdiff = 36 - int(((diff.total_seconds()/60)/60))
                minsleft = mins/36
                timeleft = minsleft*newdiff

                timetogive = ((timeleft*60))

                newtime =  zombie.zombie_expires_at + timedelta(seconds=timetogive)

                if newtime < gameinfo.addFoodTimer():
                    db(db.game_part.id == zombie.id).update(zombie_expires_at=newtime)
                else:
                    db(db.game_part.id == zombie.id).update(zombie_expires_at=gameinfo.addFoodTimer())

                db(db.bite_share.id == biteshare.id).update(shared_with=zombie.id, is_share_used=True, shared_at=getesttime())

                message = str(db.auth_user(zombie.user_id).first_name)
                message += ' '
                message += str(db.auth_user(zombie.user_id).last_name)
                message += ' shared a bite with you worth '
                message += str(timeleft)
                message += ' minutes!'

                sendemail(zombie.registration_email, "HvZ - A Bite was shared with you!" , message)

                results = 'You gave '
                results += str(db.auth_user(zombie.user_id).first_name)
                results += " "
                results += str(db.auth_user(zombie.user_id).last_name)
                results += " "
                results += str(timeleft)
                results += " minutes of brains"
                return dict(results=results)
            else:
                redirect(URL(c='default', f='index'))
        else:
            redirect(URL(c='default', f='index'))
    else:
        redirect(URL(c='default', f='index'))



# Bites and Stats page
def gamestatus():
    if gameinfo.getId():
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
        shareTotal = db((db.bite_share.game_id == gameinfo.getId()) & (db.bite_share.is_share_used == True)).count()

        bites = db(db.bite_event.game_id == gameinfo.getId()).select(db.bite_event.id, db.bite_event.zombie_id, db.bite_event.human_id, db.bite_event.game_id, db.bite_event.created, db.bite_event.lat, db.bite_event.lng,
                    db.auth_user.first_name, db.auth_user.last_name, db.auth_user.id,
                    db.auth_user.handle,
                    left=(db.game_part.on(db.game_part.id == db.bite_event.zombie_id),
                    db.auth_user.on(db.auth_user.id == db.game_part.user_id)),
                    orderby=~db.bite_event.created,
                    cache=(cache.ram, 60), cacheable=True)

        return dict(humanTotal=humanTotal, zombieTotal=zombieTotal, deadTotal=deadTotal,
                    biteTotal=biteTotal,cureTotal=cureTotal, shareTotal=shareTotal, bites=bites)
    else:
        redirect(URL(c='default', f='index'))





# coding: utf8

# Index redirects to the default index controller
def index():
    redirect(URL(c='default', f='index'))

# events page
def eventfeed():
    events = db.executesql('SELECT * FROM bite_event ORDER BY id DESC;',as_dict = True)
    zombienames = db((db.auth_user.id==db.game_part.user_id) & (db.game_part.game_id==currentgame())).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.game_part.id)
    return dict(events=events,zombienames=zombienames)

# events page
def bitetree():
    response.view='blank.html'
    events = db.executesql('SELECT * FROM bite_event ORDER BY id DESC;',as_dict = True)
    zombienames = db((db.auth_user.id==db.game_part.user_id) & (db.game_part.game_id==currentgame())).select(db.auth_user.id, db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.game_part.id)
    return dict(events=events,zombienames=zombienames)


@auth.requires_login()
def resetregistration():
    regalive=checkreg(currentgame())
    if not returncurrentuserpart() and returncurrentuserapp() and regalive:
        db((db.registration_app.user_id==auth.user.id) & (db.registration_app.game_id==currentgame())).delete()
        redirect(URL(c='gamectrl', f='register'))
    else:
        redirect(URL(c='gamectrl', f='register'))

@auth.requires_login()
# controller for five-college student registration request
def register():
    regalive=checkreg(currentgame())
    if not returncurrentuserpart() and not returncurrentuserapp() and regalive:
        form = SQLFORM.factory(Field("address", default='address@umass.edu'),
                Field("Original", 'boolean', label="Original Zombie Request",),
                buttons = [TAG.button('Register',_type="submit",_class="btn btn-primary btn-lg btn-block")],_class="table-noborder")
        if form.process().accepted:
            useremail = form.vars.address
            emails = db(db.emails).select()
            emaildoms = []
            for dom in emails:
                emaildoms.append(dom.email)
            esplit = useremail.rsplit('@')
            if esplit[1] in emaildoms:
                regcode = generatebitecode()
                message = "This is your registration code: * " + regcode + " *. Head to http://leetmeatgolem.pythonanywhere.com/pandemic/gamectrl/register to use it."
                results = sendemail(useremail, "HvZ Registration code", message)
                db.registration_app.insert(user_id=auth.user.id, game_id=currentgame(), registration_code=regcode, original_request=form.vars.Original, created=request.now, registration_email=useremail)
                return dict(form="Check your email and refresh this page!", results=results, fbpost=False)
            else:
                response.flash="invalid email or domain"
                return dict(form=form, results=[], fbpost=False)
        else:
            return dict(form=form, results=[], fbpost=False)
        return dict(form=form, results=[])
    elif not returncurrentuserpart() and returncurrentuserapp() and regalive:
        response.flash="Enter the code from your email"
        form = SQLFORM.factory(Field("regcode", label='Registration Code ', default=''),submit_button="Register me!",)
        if form.process().accepted:
            search = db.registration_app.game_id == currentgame()
            ccode = form.vars.regcode
            ccode = ccode.replace(' ','').upper()
            if ccode:
                search = db.registration_app.registration_code.like(ccode)
                regapp = db(search).select().first()
                if regapp:
                    db.game_part.insert(user_id=regapp.user_id, game_id=regapp.game_id, bitecode=generatebitecode(), registration_email=regapp.registration_email, original_request=regapp.original_request, creature_type=1, zombie_expires_at=request.now)
                    db(db.registration_app.id==regapp.id).update(reviewed=True)
                    results= auth.user.first_name + " just registered for Humans vs Zombies!!"
                    response.flash=results
                    return dict(form=form, results=results, fbpost=True)
                else:
                    results="Code didn't work!"
                    response.flash="Code didn't work!"
                    return dict(form=form, results=results, fbpost=False)
        return dict(form=form, results="Enter your registration code", fbpost=False)
    elif not regalive:
        return dict(form="Registration is Closed", results="Registration is Closed", fbpost=False)

@auth.requires_login()
# controller for non-five-college student registration request
def registerrequest():
    regalive=checkreg(currentgame())
    if not returncurrentuserpart() and not returncurrentuserapp() and not returncurrentuserreqapp() and regalive:
        form = SQLFORM.factory(
			Field("address", default='address@email.com', requires=IS_NOT_EMPTY()),
			Field("original", 'boolean', label="Original Zombie Request ",),
			Field("appeal", 'text', requires=IS_NOT_EMPTY(), label="Appeal ", default="Reason why you should play even though you don't have a five-college email. Ex: Alumni, friend of student, visiting from another school, etc. Alums must state year of graduation. Friends of students must state the student they are friends with. Visitors must tell us what school they are from."),
			)
        if form.process().accepted:
            try:
                useremail = form.vars.address
                db.registration_request.insert(
                                               user_id=auth.user.id,game_id=currentgame(),original_request=form.vars.original,
                                               registration_email=useremail,appeal=form.vars.appeal,created=request.now
                                               )
                message = "We have recieved your registration request and the game admins will review it promptly. A decision will be sent to you via email."
                sendemail(useremail, "HvZ Registration Request", message)
                return dict(form="Check your email.")
            except Exception:
                response.flash="Invalid email"
                return dict(form=form)
        else:
            return dict(form=form)
        return dict(form=form)
    else: return dict(form="Registration is Closed")

@auth.requires_login()
#  Returns the page for cures. Uses variables defined in the menu.py model statusmenu function
def curezombie():
    # checks if user is logged in, a zombie, and not dead
    if zombiestat and not deadstat:
        form = SQLFORM.factory(Field("Curecode", default=''),submit_button="Cure Me!",)
        if form.process().accepted:
            search = db.cures.game_id == currentgame()
            ccode = form.vars.Curecode
            ccode = ccode.replace(' ','').upper()
            if ccode:
                search = db.cures.curecode.like(ccode)
                results = db(search).select().first()
                if results:
                    forcurrentgame = currentgame() == results.game_id
                    expired = isexpired(results)
                    gpart = returncurrentuserpart()
                    infected = isinfected(gpart)
                    # checks to see if the curecode is not used/expired, for the current game, and that the player is not infected.
                    if not results.used and not expired and forcurrentgame and not infected:
                        db.cure_event.insert(player_id=gpart.id, game_id=currentgame(), cure_id=results.id)
                        db(db.cures.id==results.id).update(used=True)
                        db(db.game_part.id==gpart.id).update(creature_type=1, bitecode=generatebitecode())
                        # results is changed to the text to appear in the facebook post and passed to the view.
                        results = db.auth_user(gpart.user_id).first_name + ' ' + db.auth_user(gpart.user_id).last_name + ' used a cure and is human again!'
                        response.flash=results
                        return dict(form=form, results=results)
                    elif results.used and not expired and forcurrentgame:
                        response.flash='This code has been used already!'
                        return dict(form=form, results=[])
                    elif not results.used and expired and forcurrentgame:
                        response.flash='This code has expired!'
                        return dict(form=form, results=[])
                    elif results.used and expired and forcurrentgame:
                        response.flash='This code has been used and has expired!'
                        return dict(form=form, results=[])
                    elif not forcurrentgame:
                        response.flash='This code is for an older game!'
                        return dict(form=form, results=[])
                    elif infected:
                        response.flash='Your infection is irreversible!'
                        return dict(form=form, results=[])
                else:
                 response.flash='Invalid Cure code'
                 return dict(form=form, results=[])
            else:
                 response.flash='Invalid Cure code'
                 return dict(form=form, results=[])
        else:

            return dict(form=form, results=[])
    else:
        redirect(URL(c='default', f='index'))

@auth.requires_login()
# Returns the page for biting. Uses variables defined in the menu.py model statusmenu function
def bitecodepg():
    form=''
    if zombiestat and not deadstat:
        if request.args(0):
            search = db.game_part.game_id == currentgame()
            bcode = request.args(0)
            bcode = bcode.replace(' ','').upper()
            if bcode:
                gpart = returncurrentuserpart()
                search = db.game_part.bitecode.like(bcode)
                results = db(search).select().first()
                if results:
                    creattype = results['creature_type']
                    if db.creature_type(creattype).zombie:
                        response.flash='You tried to bite a zombie! ewww!'
                        return dict(form=form, results=[])
                    else:
                        human = results['id']
                        uid = results['user_id']
                        # results is changed to the text to appear in the facebook post and passed to the view.
                        results = db.auth_user(gpart.user_id).first_name + ' ' + db.auth_user(gpart.user_id).last_name + ' bit ' + db.auth_user(uid).first_name + ' ' + db.auth_user(uid).last_name
                        db.bite_event.insert(zombie_id=gpart.id, human_id=human, game_id=currentgame())
                        zombiefood = zombiebitefood(gpart.zombie_expires_at)
                        humanfood = zombiebitefood(request.now)
                        db(db.game_part.id==gpart.id).update(zombie_expires_at=zombiefood)
                        db(db.game_part.id==human).update(zombie_expires_at=humanfood,creature_type=2)
                        response.flash=results
                        return dict(form=form, results=results)
                else:
                    response.flash='Invalid Bitecode'
                    return dict(form=form, results=[])
            else:
                 response.flash='Invalid Bitecode'
                 return dict(form=form, results=[])
        form = SQLFORM.factory(Field("Bitecode", default=''),submit_button="Bite!",)
        if form.process().accepted:
            search = db.game_part.game_id == currentgame()
            bcode = form.vars.Bitecode
            bcode = bcode.replace(' ','').upper()
            if bcode:
                gpart = returncurrentuserpart()
                search = db.game_part.bitecode.like(bcode)
                results = db(search).select().first()
                if results:
                    creattype = results['creature_type']
                    if db.creature_type(creattype).zombie:
                        response.flash='You tried to bite a zombie! ewww!'
                        return dict(form=form, results=[])
                    else:
                        human = results['id']
                        uid = results['user_id']
                        # results is changed to the text to appear in the facebook post and passed to the view.
                        results = db.auth_user(gpart.user_id).first_name + ' ' + db.auth_user(gpart.user_id).last_name + ' bit ' + db.auth_user(uid).first_name + ' ' + db.auth_user(uid).last_name
                        db.bite_event.insert(zombie_id=gpart.id, human_id=human, game_id=currentgame())
                        zombiefood = zombiebitefood(gpart.zombie_expires_at)
                        humanfood = zombiebitefood(request.now)
                        db(db.game_part.id==gpart.id).update(zombie_expires_at=zombiefood)
                        db(db.game_part.id==human).update(zombie_expires_at=humanfood,creature_type=2)
                        response.flash=results
                        return dict(form=form, results=results)
                else:
                    response.flash='Invalid Bitecode'
                    return dict(form=form, results=[])
            else:
                 response.flash='Invalid Bitecode'
                 return dict(form=form, results=[])
        else:

            return dict(form=form, results=[])
    else:
        redirect(URL(c='default', f='index'))

# Function for creating original zombies from the OZ pool.
@auth.requires_membership('admins')
def makeoz():
    db(db.game_part.id==request.args(0)).update(creature_type=3)
    userpart = db(db.game_part.id==request.args(0)).select()
    response.flash='made them an OZ!'
    redirect(URL(c='admin', f='ozlist', args=userpart[0].game_id))

@auth.requires_login()
# This is the controller function for the squad application page.
def createsquadapp():
    response.view='default.html'
    gid=currentgame()
    gpart=returncurrentuserpart()
    try:
        if gid and not deadstat and not gpart.squad_id and not gpart.squad_apps:
            form = SQLFORM(db.squads_app,fields = ['name','description','image',],labels = {'name':'Your Squad Name:','image':'MUST BE 960px x 240px'},submit_button="Submit Squad Application",)
            form.vars.leader=gpart.id
            form.vars.game_id=gid
            form.vars.sigid=generatebitecode()
            if form.process().accepted:
                db(db.game_part.id==gpart.id).update(squad_apps=1)
                response.flash="Squad Application Created!"
            return dict(form=form)
        elif gpart.squad_apps or gpart.squad_id :
            response.flash="You are already affiliated with a squad this game!"
            form = "Squad application form locked."
            return dict(form=form)
        else:
            redirect(URL(c='default', f='index'))
    except:
        redirect(URL(c='default', f='index'))

# This is the controller for the squad hq page for squad members.
@auth.requires_login()
def squadhq():
    squad = db.squads(request.args[0]) or redirect(URL(c='default', f='index'))
    gpart=returncurrentuserpart()
    if gpart.squad_id == request.args[0]:
       if squad:
         posts = db(db.squad_posts.squad_id==request.args(0)).select(orderby=~db.squad_posts.created,)
         members = db((db.game_part.squad_id==squad.id) & (db.game_part.squad_leader==False)).select(orderby=db.game_part.created)
         leader = db.game_part(squad.leader)
         return dict(squad=squad,posts=posts, members=members,leader=leader)
    else:
        redirect(URL(c='default', f='index'))

# View squad post page.
@auth.requires_login()
def viewsquadpost():
    post = db.squad_posts[request.args(0)] or redirect(URL(r=request,f='index'))
    gpart=returncurrentuserpart()
    if int(gpart.squad_id) == int(post.squad_id):
        squad = db.squads(post.squad_id)
        return dict(post=post, squad=squad)

# This is the controller for the squad admin page for squad leaders.
@auth.requires_login()
def squadadmin():
    squad = db.squads(request.args(0)) or redirect(URL(c='default', f='index'))
    gpart=returncurrentuserpart()
    if gpart.squad_id == request.args(0) and gpart.squad_leader:
       if squad:
         posts = db(db.squad_posts.squad_id==request.args(0)).select(orderby=~db.squad_posts.created,)
         members = db((db.game_part.squad_id==squad.id) & (db.game_part.squad_leader==False)).select(orderby=db.game_part.created)
         leader = db.game_part(squad.leader)
         squadsmemapp=db((db.squads_member_app.squad_id==squad.id) & (db.squads_member_app.reviewed==False)).select()
         return dict(squad=squad,members=members,leader=leader,squadsmemapp=squadsmemapp, posts=posts)
    else:
        redirect(URL(c='default', f='index'))

# Create a post page
@auth.requires_login()
def createsquadpost():
    response.view='default.html'
    request.args(0) or redirect(URL(c='default', f='index'))
    gpart=returncurrentuserpart()
    if gpart.squad_id == request.args(0) and gpart.squad_leader:
       response.flash = "Create a post!"
       form=SQLFORM(db.squad_posts, fields=['title','description'])
       form.vars.sleader = gpart.id
       form.vars.squad_id = gpart.squad_id
       if form.process().accepted:
               response.flash = 'Post accepted.'
       elif form.errors:
               response.flash = 'The post has errors, idiot!'
       return dict(form=form)

# Edit a post page
@auth.requires_login()
def editsquadpost():
    response.view='default.html'
    request.args(0) or redirect(URL(c='default', f='index'))
    gpart=returncurrentuserpart()
    post = db.squad_posts(request.args(0))
    if int(post.squad_id) == int(gpart.squad_id) and gpart.squad_leader:
        form=SQLFORM(db.squad_posts, post, showid=False, fields=['title','description'], deletable = True)
        response.flash = 'Edit the post!'
        if form.validate():
            if form.deleted:
                db(db.squad_posts.id==post.id).delete()
                redirect(URL(c='gamectrl', f='squadadmin', args=gpart.squad_id))
                response.flash = 'POST BALEETED!'
            else:
                post.update_record(**dict(form.vars))
                response.flash = 'Changes saved.'
        else:
            response.flash = 'Edit the post!'
        return dict(form=form)
    else:
        redirect(URL(c='default', f='index'))

# This function is for the SL admin page. It rejects a member application and makes the neccesary database updates.
@auth.requires_login()
def denysquadmemberapp():
   smemappid=request.args[0]
   sq=db.squads_member_app(smemappid)
   gpart=returncurrentuserpart()
   sqd=db.squads(sq.squad_id)
   if gpart.id == sqd.leader:
       db(db.squads_member_app.id==smemappid).update(reviewed=True)
       redirect(URL(c='gamectrl', f='squadadmin', args=sq.squad_id))
   else:
       redirect(URL(c='default', f='index'))

# This function is for the SL admin page. It approves a member application and makes the neccesary database updates.
@auth.requires_login()
def approvesquadmemberapp():
   sid=request.args[0]
   sq=db.squads_member_app(sid)
   gpart=returncurrentuserpart()
   sqd=db.squads(sq.squad_id)
   if gpart.id == sqd.leader:
       db(db.squads_member_app.id==sid).update(reviewed=True,approved=True)
       db(db.game_part.id==sq.player_id).update(squad_id=sq.squad_id,squad_apps=1)
       redirect(URL(c='gamectrl', f='squadadmin', args=sq.squad_id))
   else:
       redirect(URL(c='default', f='index'))

# function for people to apply to a squad
@auth.requires_login()
def applytosquad():
    sid=request.args[0]
    gpart=db.game_part(request.args[1])
    if not gpart.squad_id:
        squadapp = db(db.squads_member_app.player_id==gpart.id).select()
        # checks for an existing squad application. if one exists it just updates that one instead of making a new one.
        if squadapp:
            db(db.squads_member_app.player_id==gpart.id).update(squad_id=sid)
            redirect(URL(c='default', f='squadinfo', args=sid))
        else:
            db.squads_member_app.insert(player_id=gpart.id,squad_id=sid)
            redirect(URL(c='default', f='squadinfo', args=sid))

# function for squad leaders to change people's titles
@auth.requires_login()
def squadtitlechange():
    response.view='default.html'
    uid=request.args[0]
    gpart=returncurrentuserpart()
    if gpart.squad_leader and db.game_part(uid).squad_id == gpart.squad_id:
        sqmember = db.game_part(uid) or redirect(URL('error'))
        form=SQLFORM(db.game_part, sqmember,showid=False,fields = ['squad_title'])
        if form.validate():
            sqmember.update_record(**dict(form.vars))
            response.flash = 'Changes saved'
        else:
            response.flash = 'Change member title'
        return dict(form=form)

# kick squad member function
@auth.requires_login()
def kickmember():
   uid=request.args[0]
   mem=db.game_part(uid)
   sqid = mem.squad_id
   gpart=returncurrentuserpart()
   # checks to make sure that the person getting kicked is in the squad of the person calling the controller and that they are the leader
   if mem.squad_id == gpart.squad_id and gpart.squad_leader:
       db(db.game_part.id==uid).update(squad_id=None,squad_title='', squad_apps=None)
       db(db.squads_member_app.player_id==uid).delete()
       redirect(URL(c='gamectrl', f='squadadmin', args=sqid))
   else:
       redirect(URL(c='default', f='index'))


# human bitecode qrcode page

def bitecodeqrcodepage():
    gpart=returncurrentuserpart()
    zombiestat=db.creature_type(gpart.creature_type).zombie
    if authstat and not zombiestat:
        return dict(gpart=gpart)
    else:
        redirect(URL(c='default', f='index'))

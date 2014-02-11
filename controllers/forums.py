# coding: utf8

@auth.requires_login()
def index():
    cats = db(db.forum_cats).select(db.forum_cats.ALL)
    return dict(cats=cats)

@auth.requires_login()
def viewcat():
    cat = db.forum_cats(request.args(0))
    forums = db(db.forum_forums.cat_id == request.args(0)).select()
    return dict(forums=forums, cat=cat)

@auth.requires_login()
def viewforum():
    if returncurrentuserpart():
        gpart = returncurrentuserpart()
        fid = request.args[0]
        if db.forum_forums(fid):
            forum = db.forum_forums(fid)
            if auth.has_membership('admins') or forum.human and not db.creature_type(gpart.creature_type).zombie and not gpart.banned or forum.zombie and db.creature_type(gpart.creature_type).zombie and not isdead(gpart) and not gpart.banned:
                try:
                    if request.args[1]:
                        page=int(request.args[1])
                    else: page=0
                except Exception:
                    page=0
                    pass
                items_per_page=30
                limitby=(page*items_per_page,(page+1)*items_per_page+1)
                threads = db(db.forum_threads.forum_id == request.args[0]).select(orderby=~db.forum_threads.updated,limitby=limitby)
                return dict(threads=threads,page=page,items_per_page=items_per_page,fid=fid,forum=forum)
            else: redirect(URL(c='forums', f='index'))
        else:
            redirect(URL(c='forums', f='index'))
    else: redirect(URL(c='forums', f='index'))


@auth.requires_login()
def viewthread():
	tid = request.args[0]
	if db.forum_threads(tid):
		gpart = returncurrentuserpart()
		forum = db.forum_threads(tid).forum_id
		if auth.has_membership('admins') or forum.human and not db.creature_type(gpart.creature_type).zombie and not gpart.banned or forum.zombie and db.creature_type(gpart.creature_type).zombie and not isdead(gpart) and not gpart.banned:
			thread = db.forum_threads(tid)
			try:
				if request.args[1]:
					page=int(request.args[1])
				else: page=0
			except Exception:
				page=0
				pass
			items_per_page=25
			limitby=(page*items_per_page,(page+1)*items_per_page+1)
			posts = db(db.forum_posts.thread_id == request.args[0]).select(orderby=db.forum_posts.created,limitby=limitby)
			return dict(posts=posts,page=page,items_per_page=items_per_page,tid=tid,thread=thread)
		else: redirect(URL(c='forums', f='index'))
	else: redirect(URL(c='forums', f='index'))

@auth.requires_login()
def createthread():
    response.view='default.html'
    if request.args and returncurrentuserpart():
        gpart = returncurrentuserpart()
        posttimeout = db.games(currentgame()).posttimeout
        fid = request.args[0]
        if gpart.lastpost:timeout = request.now - gpart.lastpost
        else:timeout = datetime.timedelta(minutes=posttimeout*5+1)
        if auth.has_membership('admins') or db.forum_forums(fid).human and not db.creature_type(gpart.creature_type).zombie and timeout >= datetime.timedelta(minutes=posttimeout*5) and not gpart.banned or db.forum_forums(fid).zombie and db.creature_type(gpart.creature_type).zombie and not isdead(gpart) and timeout >= datetime.timedelta(minutes=posttimeout*5) and not gpart.banned:
            form = SQLFORM.factory(Field("thread", label="Thread Title", default='Thread Title'),Field("postbody", 'text', label="Body",))
            if form.process().accepted:
                threadid = db.forum_threads.insert(forum_id=fid,name=form.vars.thread,author=gpart.user_id,created=request.now,updated=request.now,publicfor=db.forum_forums(fid).publicfor,player=db.forum_forums(fid).player,human=db.forum_forums(fid).human,zombie=db.forum_forums(fid).zombie)
                db.forum_posts.insert(thread_id=threadid,body=form.vars.postbody,author=gpart.user_id,created=request.now)
                db(db.game_part.id==gpart.id).update(lastpost=request.now)
                redirect(URL(c='forums', f='viewthread', args=threadid))
            return locals()
        elif timeout < datetime.timedelta(minutes=posttimeout):
            import random
            sass = db(db.sassypost).select(db.sassypost.ALL)
            roll = random.randrange(1,len(sass))
            form = H1(sass[roll].phrase)
            return locals()
        else: redirect(URL(c='forums', f='index'))
    else: redirect(URL(c='forums', f='index'))


@auth.requires_login()
def createpost():
    response.view='default.html'
    if request.args and returncurrentuserpart():
        gpart = returncurrentuserpart()
        posttimeout = db.games(currentgame()).posttimeout
        tid = request.args[0]
        fid = db.forum_threads(tid).forum_id
        if gpart.lastpost:
            timeout = request.now - gpart.lastpost
        else:
            timeout = datetime.timedelta(minutes=posttimeout+1)
        if auth.has_membership('admins') or db.forum_forums(fid).human and not db.creature_type(gpart.creature_type).zombie and timeout >= datetime.timedelta(minutes=posttimeout) and not gpart.banned or db.forum_forums(fid).zombie and db.creature_type(gpart.creature_type).zombie and not isdead(gpart) and timeout >= datetime.timedelta(minutes=posttimeout) and not gpart.banned:
            form = SQLFORM.factory(Field("postbody", 'text', label="Post",))
            if form.process().accepted:
				db.forum_posts.insert(thread_id=tid,body=form.vars.postbody,author=gpart.user_id,created=request.now)
				db(db.forum_threads.id == tid).update(updated=request.now)
				db(db.game_part.id==gpart.id).update(lastpost=request.now)
				redirect(URL(c='forums', f='viewthread', args=tid))
            return locals()
        elif timeout < datetime.timedelta(minutes=posttimeout):
            import random
            sass = db(db.sassypost).select(db.sassypost.ALL)
            roll = random.randrange(1,len(sass))
            form = H1(sass[roll].phrase)
            return locals()
        else: redirect(URL(c='forums', f='index'))
    else: redirect(URL(c='forums', f='index'))


@auth.requires_login()
def editpost():
	response.view='default.html'
	post = db.forum_posts(request.args(0)) or redirect(URL('error'))
	gpart = returncurrentuserpart()
	if auth.has_membership('admins') or gpart.user_id == post.author and not gpart.banned and not post.moderated:
		form=SQLFORM(db.forum_posts, post, deletable = False)
		response.flash = 'Edit the post!'
		if form.validate():
			post.update_record(**dict(form.vars,edited=request.now))
			response.flash = 'Changes saved.'
			redirect(URL(c='forums', f='viewthread', args=post.thread_id))
		else:
			response.flash = 'Edit the post!'
		return dict(form=form)
	else:
		redirect(URL(c='forums', f='index'))

@auth.requires_membership('admins')
def editthread():
    response.view='default.html'
    thread = db.forum_threads(request.args(0)) or redirect(URL('error'))
    form=SQLFORM(db.forum_threads, thread, deletable = True)
    response.flash = 'Edit the thread!'
    if form.validate():
        if form.deleted:
            db(db.forum_threads.id==thread.id).delete()
            redirect(URL(c='forums', f='index'))
            response.flash = 'THREAD BALEETED!'
        else:
            thread.update_record(**dict(form.vars))
            response.flash = 'Changes saved.'
    else:
        response.flash = "Edit the thread."
    return dict(form=form)

    redirect(URL(c='forums', f='index'))

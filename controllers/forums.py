# coding: utf8

@auth.requires_login()
def index():
    listcats = db(db.forum_cats.id).select(db.forum_cats.id, db.forum_cats.name, db.forum_cats.description, db.forum_cats.game_id,orderby=~db.forum_cats.id, cache=(cache.ram, 600), cacheable=True)
    listforums = db(db.forum_forums.id).select(cache=(cache.ram, 600), cacheable=True)
    forumnav=OL('',LI(A('Index',_href=URL(c='forums', f='index'))), _class='breadcrumb margin-sm')
    return dict(listcats=listcats,listforums=listforums, forumnav=forumnav)

@auth.requires_login()
def viewforum():
    gpart = returncurrentuserpart()
    authcheck = forumAccess(gpart,request.args(0)) or redirect(URL(c='forums', f='index'))
    if authcheck:
        count = db.forum_posts.thread_id.count()
        threads = db((db.forum_threads.forum_id == request.args(0)) & (db.auth_user.id == db.forum_threads.author) & (db.forum_threads.id == db.forum_posts.thread_id)).select(
            db.auth_user.first_name, db.auth_user.last_name, db.auth_user.handle, db.auth_user.id,
            db.forum_threads.id, db.forum_threads.name,
            db.forum_threads.forum_id, db.forum_threads.created, count, groupby=~db.forum_threads.created)

        foruminfo = db.forum_forums(request.args(0))
        cata = db.forum_cats(foruminfo.cat_id)
        forumnav=OL('',LI(A('Index',_href=URL(c='forums', f='index'))),
                    LI(A(cata.name,_href=URL(c='forums', f='index', args=cata.id))),
                    LI(A(foruminfo.name,_href=URL(c='forums', f='viewforum', args=foruminfo.id))),
                    _class='breadcrumb margin-sm')
        return dict(threads=threads, forumnav=forumnav, foruminfo=foruminfo)
    else: redirect(URL(c='forums', f='index'))

@auth.requires_login()
def editpost():
    response.view = 'default.html'
    post = db.forum_posts(request.args(0)) or redirect(URL('index',extension='html'))
    gpart = returncurrentuserpart()
    if auth.has_membership('admins') or gpart.auth_user.id == post.author:
        form = SQLFORM(db.forum_posts, post, deletable=True, fields = ['body', 'created', 'edited'])
        session.flash = 'Edit the post!'
        if form.validate():
            if form.deleted:
                db(db.forum_posts.id == post.id).delete()
                session.flash = 'POST BALEETED!'
                redirect(URL(c='forums', f='viewthread',args=post.thread_id,extension='html'))
            else:
                post.update_record(**dict(form.vars, edited=getEstNow()))
                session.flash = 'Changes saved.'
                redirect(URL(c='forums', f='viewthread', args=post.thread_id, extension='html'))
        else:
            session.flash = 'Edit the post!'
        return dict(form=form)
    else:
        redirect(URL(c='forums', f='index', extension='html'))


@auth.requires_login()
def createpost():
    response.view='default.html'
    gpart = returncurrentuserpart()
    foruminfo = db(db.forum_forums.id == request.args(0)).select(cache=(cache.ram, 1), cacheable=True).last()
    authcheck = forumAccess(gpart,request.args(0)) or redirect(URL(c='forums', f='index'))
    if authcheck:
        form = SQLFORM.factory(Field("thread", label="", default='Thread Title'),Field("postbody", 'text', label="",default='Post Body'),Field('author',db.auth_user,writable=False,label="",default=gpart.auth_user.id))
        form.vars.author = gpart.auth_user.id
        if form.process(onvalidation=forumCheck).accepted:
            threadid = db.forum_threads.insert(forum_id=foruminfo.id,name=form.vars.thread,
                                               author=form.vars.author,created=getEstNow(),
                                               updated=getEstNow(),player=foruminfo.player,
                                               human=foruminfo.human,zombie=foruminfo.zombie
                                                )
            db.forum_posts.insert(thread_id=threadid,body=form.vars.postbody,author=form.vars.author,created=getEstNow())
            redirect(URL(c='forums', f='viewthread', args=threadid, extension='html'))
        elif form.errors:
            session.flash = getSassyPost()
        return dict(form=form)


@auth.requires_login()
def viewthread():
    if request.args(0):
        gpart = returncurrentuserpart()
        threadinfo = db.forum_threads(request.args(0))
        if forumAccess(gpart,threadinfo.forum_id):
            foruminfo = db.forum_forums(threadinfo.forum_id)
            cata = db.forum_cats(foruminfo.cat_id)
            forumnav=OL('',LI(A('Index',_href=URL(c='forums', f='index', extension='html'))),
                LI(A(cata.name,_href=URL(c='forums', f='index', args=cata.id, extension='html'))),
                LI(A(foruminfo.name,_href=URL(c='forums', f='viewforum', args=foruminfo.id, extension='html'))),
                 LI(A(threadinfo.name,_href=URL(c='forums', f='viewthread', args=threadinfo.id, extension='html'))),
                _class='breadcrumb margin-sm')
            return dict(threadinfo=threadinfo, gpart=gpart, forumnav=forumnav)
    else: redirect(URL(c='forums', f='index'))

@auth.requires_signature()
def posttothread():
    form=SQLFORM(db.forum_posts,fields = ['body'],labels = {'body':''},submit_button = 'Post')
    form.vars.thread_id = request.args(1)
    form.vars.author = request.args(0)
    if form.process(onvalidation=forumCheck).accepted:
        session.flash = 'Post made!'
        response.js = "$('.text').markItUp(mySettings);"
        return dict(form=form)
    elif form.errors:
        response.js = "$('.text').markItUp(mySettings);"
        session.flash = getSassyPost()
    return dict(form=form)

@auth.requires_signature()
def getthreadposts():
    if request.args(0) and request.args(1):
        posts = db((db.forum_posts.thread_id == request.args(1)) & (db.auth_user.id == db.forum_posts.author)).select(orderby=db.forum_posts.id)
        return dict(posts=posts)
    else:
        return dict(posts='')



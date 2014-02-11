# coding: utf8
response.static_version = '1.0.0'

# This model has various common functions in it.
import re

# Converts the current time, whatever zone it may be in, to EST, and returns it.
def getesttime():
    from datetime import datetime
    from pytz import timezone
    localtz = timezone('US/Eastern')
    now_utc =datetime.now(timezone('UTC'))
    now_east = now_utc.astimezone(timezone('US/Eastern'))
    return now_east

# Converts TZ unaware datetime objects to EST aware.    
def converttotz(unaware):
    from datetime import datetime
    from pytz import timezone
    localtz = timezone('US/Eastern')
    return localtz.localize(unaware)

# Takes a user's facebook URL as input, splices the FB user ID, and plugs it into the FB graph API to retrive the profile thumb.
def fbphoto(fburl):
     fbid = re.findall(r'\d+',str(fburl))
     return 'http://graph.facebook.com/'+str( fbid[0])+'/picture'

# Takes a user's facebook URL as input, splices the FB user ID, and plugs it into the FB graph API to retrive the profile picture.
def fbphotofull(fburl):
     fbid = re.findall(r'\d+',str(fburl))
     return 'http://graph.facebook.com/'+str( fbid[0])+'/picture?width=200&height=200'


# Accepts a tz unaware datetime object and returns an easier to read datetime string. credit to Jeb Smith for the snippet this is based on.     
def pretty_date(d):
    diff = getesttime() - converttotz(d)
    s = diff.seconds
    if diff.days > 7 or diff.days < 0:
        return d.strftime('%I:%M %p') + ' - ' + d.strftime('%a %m/%d')
    elif diff.days == 1:
        return '1 day ago'
    elif diff.days > 1:
        return '{0} days ago'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        return '{0} seconds ago'.format(s)
    elif s < 120:
        return '1 minute ago'
    elif s < 3600:
        return '{0} minutes ago'.format(s/60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{0} hours ago'.format(s/3600)

# Takes an image object, size tuple, and path and returns the filename of a thumbnail of that image.
def resize_image(image, size, path):
    from PIL import Image
    import os.path
    try:
        img = Image.open('%sstatic/images/%s' % (request.folder, image))
        img.thumbnail(size, Image.ANTIALIAS)
        root, ext = os.path.splitext(image)
        filename = '%s_%s%s' %(root, path, ext)
        img.save('%sstatic/images/%s' % (request.folder, filename))
    except Exception, e:
        return e
    else:
        return filename

		
def user_bar():
    action = '/user'
    if auth.user:
        logout=LI('logout', _href=action+'/logout')
        profile=A('profile', _href=action+'/profile')
        bar = [
                LI(A(auth.user.first_name + " " + auth.user.last_name,
                UL(LI(A('Profile',_href=URL(c='default',f='user', args='profile')), _class=''),
                LI(A('Logout',_href=URL(c='default',f='user', args='logout')), _class=''),
                _class='dropdown-menu', _id='statusmenu'),
                _href="#", _class="dropdown-toggle", 
                **{'_data-toggle':'dropdown'}),_class='dropdown')
        ]
    else:
        bar = [LI(A('Login', _href=URL('default', 'user', args=['login'], vars=dict(_next='/pandemic2/default/index'))), _class=" ")]
    return bar
		
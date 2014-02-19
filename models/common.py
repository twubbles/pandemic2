# coding: utf8
response.static_version = '1.0.0'

# import any modules needed here. web2py freaks out if you have imports in more than one place
import re
from datetime import datetime
from datetime import timedelta
from pytz import timezone
import pytz
from gluon.tools import prettydate

# This model has various common functions in it.

# Converts the current time, whatever zone it may be in, to EST, and returns it. Set to convert pacific to EST
def getesttime():
    pactz = timezone('US/Pacific-New')
    localtz = timezone('US/Eastern')
    now_pac = pactz.localize(datetime.now())
    now_east = now_pac.astimezone(localtz)
    fmt = "%Y-%m-%d %H:%M:%S"
    return now_east

# Converts TZ unaware datetime objects to EST aware.    
def converttotz(unaware):
    pactz = timezone('US/Pacific-New')
    pactime = pactz.localize(unaware)
    localtz = timezone('US/Eastern')
    now_east = pactime.astimezone(localtz)
    fmt = "%Y-%m-%d %H:%M:%S"
    return now_east

# Takes a user's facebook URL as input, splices the FB user ID, and plugs it into the FB graph API to retrive the profile thumb.
def fbphoto(fburl):
     fbid = re.findall(r'\d+',str(fburl))
     return 'http://graph.facebook.com/'+str( fbid[0])+'/picture'

# Takes a user's facebook URL as input, splices the FB user ID, and plugs it into the FB graph API to retrive the profile picture.
def fbphotofull(fburl):
     fbid = re.findall(r'\d+',str(fburl))
     return 'http://graph.facebook.com/'+str( fbid[0])+'/picture?width=200&height=200'


# Accepts a tz unaware datetime object and returns an easier to read datetime string.
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


def adminlog(string):
	try:
		file = open("adminlog.txt", "a")
		file.write(str(getesttime()) + ' ' + string + "\n")
		file.close()
		msg = True
	except:
		msg = False
	return msg
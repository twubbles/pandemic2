# -*- coding: utf-8 -*-

# This model has various common functions in it.
# it is also the first model to load so put any global imports here

# this reloads the modules on change for development purposes and should be removed in production
from gluon.custom_import import track_changes; track_changes(True)

# import the timezone hack module
from fixtime import getEstNow


# Takes a user's facebook URL as input, splices the FB user ID, and plugs it into the FB graph API to retrive the profile thumb.
def fbphoto(fburl):
    from re import findall
    fbid = re.findall(r'\d+', str(fburl))
    return 'http://graph.facebook.com/' + str(fbid[0]) + '/picture'


# Takes a user's facebook URL as input, splices the FB user ID, and plugs it into the FB graph API to retrive the profile picture.
def fbphotofull(fburl):
    from re import findall
    fbid = re.findall(r'\d+', str(fburl))
    return 'http://graph.facebook.com/' + str(fbid[0]) + '/picture?width=200&height=200'


# Accepts a datetime object and returns an easier to read datetime string.
def pretty_date(d):
    diff = getEstNow() - d
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
        return '{0} minutes ago'.format(s / 60)
    elif s < 7200:
        return '1 hour ago'
    else:
        return '{0} hours ago'.format(s / 3600)


# Constructs the user button for the top left corner
def user_bar():
    action = '/user'
    if auth.user:
        logout = LI('logout', _href=action + '/logout')
        profile = A('profile', _href=action + '/profile')
        bar = [
            LI(A(auth.user.first_name + " " + auth.user.last_name,
                 UL(LI(A('Profile', _href=URL(c='default', f='user', args='profile')), _class=''),
                    LI(A('Logout', _href=URL(c='default', f='user', args='logout')), _class=''),
                    _class='dropdown-menu', _id='statusmenu'),
                 _href="#", _class="dropdown-toggle",
                 **{'_data-toggle': 'dropdown'}), _class='dropdown')
        ]
    else:
        bar = [LI(A('Login', _href=URL('default', 'user', args=['login'], vars=dict(_next='/pandemic2/default/index'))),
                  _class=" ")]
    return bar


def breadcrumbs(arg_title=None):
    # make links pretty by capitalizing and using 'home' instead of 'default'
    pretty = lambda s: s.replace('default', 'Home').replace('_', ' ').capitalize()
    menus = [LI(A(T('UMASSHvZ'), _href=URL(r=request, c='default', f='index')))]
    if request.controller != 'default':
        # add link to current controller
        menus.append(LI(A(T(pretty(request.controller)), _href=URL(r=request, c=request.controller, f='index'))))
        if request.function == 'index':
            # are at root of controller
            menus[-1] = LI(A(T(pretty(request.controller)), _href=URL(r=request, c=request.controller, f=request.function)))
        else:
            # are at function within controller
            menus.append(LI(A(T(pretty(request.function)), _href=URL(r=request, c=request.controller, f=request.function))))
        # you can set a title putting using breadcrumbs('My Detail Title')
        if request.args and arg_title:
            menus.append(LI(A(T(arg_title)),
                         _href=URL(r=request, c=request.controller, f=request.function, args=[request.args])))
    else:
        #menus.append(A(pretty(request.controller), _href=URL(r=request, c=request.controller, f='index')))
        if request.function == 'index':
            # are at root of controller
            #menus[-1] = pretty(request.controller)
            pass
            #menus.append(A(pretty(request.controller), _href=URL(r=request, c=request.controller, f=request.function)))
        else:
            # are at function within controller
            menus.append(LI(A(T(pretty(request.function)), _href=URL(r=request, c=request.controller, f=request.function))))
        # you can set a title putting using breadcrumbs('My Detail Title')
        if request.args and arg_title:
            menus.append(LI(A(T(arg_title), _href=URL(r=request, f=request.function, args=[request.args]))))

    return OL(XML('  '.join(str(m.xml().replace(' data-w2p_disable_with="default"', '')) for m in menus)), _id="breadcrumbs")


# takes saturation and variance as args and returns an rgb color value for css
def randomcolors(s, v):
    import random
    import colorsys
    num = random.randint(0, 359)
    num /= 360.0
    gratio = 0.618033988749895
    num += gratio
    num %= 1
    rgb = colorsys.hsv_to_rgb(num, s, v)
    r = str(int(255 * rgb[0]))
    g = str(int(255 * rgb[1]))
    b = str(int(255 * rgb[2]))
    colorcode = "rgb(" + r + ", " + g + ", " + b + ")"
    return colorcode
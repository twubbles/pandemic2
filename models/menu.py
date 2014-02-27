# -*- coding: utf-8 -*-

response.static_version = '1.0.0'

authstat = auth.is_logged_in()
# The logo/header

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Ed Clairmont <eclairm@tacotech.net>'
response.meta.description = 'pandemic'
response.meta.keywords = 'web2py, python, framework, hvz, umasshvz, humans vs zombies, zombies, humans'
response.meta.generator = 'UmassHvZ Pandemic Engine'

## your http://google.com/analytics id
response.google_analytics_id = None

# if not authstat:
#    response.menu = [(SPAN('You need to Login', _class='headerhvz'), False, URL('default', 'index'), []),]


# ---- Status menu logic begin ----

# calls the function that returns the info about the current user's game status
### This also will expose the gpart vars to any model after this or controller/view that is active.
gpart=returncurrentuserpart()
if gpart and auth.is_logged_in() and not gpart.game_part.banned:

    # checks if the player is dead
    deadstat=isZombieDead(gpart)
    stime = pretty_date(gpart.game_part.zombie_expires_at)

    # Logic to display correct menu for the user's status in game (ie. human/zombie/dead etc)
    # Human menu
    if not gpart.creature_type.zombie:
        response.statusmenu = [
                LI(A(gpart.creature_type.name,UL(LI(A('Bitecode', _href=URL('gamectrl', 'bitecodeqrcodepage'), _class='')),
				LI(A(gpart.game_part.bitecode, _href=URL('gamectrl', 'bitecodeqrcodepage'), _class=''), _class=''),
				_class='dropdown-menu', _id='statusmenu'), _href="#", _class="dropdown-toggle",
				**{'_data-toggle':'dropdown'}),_class='dropdown')
				]

    # Immortal Zombie Menu
    elif gpart.creature_type.zombie and gpart.creature_type.immortal:
        response.statusmenu = [
            LI(A(gpart.creature_type.name, UL(
            LI(A('Bite Somebody', _href=URL('gamectrl', 'bitecodepg')), _class=''),
            LI(A('Share a Bite', _href=URL('gamectrl', 'biteshare')), _class=''),
            LI(A('Cure', _href=URL('gamectrl', 'curezombie')), _class=''),
            _class='dropdown-menu', _id='gamemenu'),_href="#", _class="dropdown-toggle",
            **{'_data-toggle': 'dropdown'}), _class='dropdown')
            ]
    # Regular Zombie Menu(s)
    elif gpart.creature_type.zombie and not gpart.creature_type.immortal:
        # Menu for zombies that are still alive
        if not deadstat:
            response.statusmenu = [
                LI(A("Starve @ " +stime,UL(
                LI(A('Bite Somebody', _href=URL('gamectrl', 'bitecodepg')), _class=''),
                LI(A('Share a Bite', _href=URL('gamectrl', 'biteshare')), _class=''),
                LI(A('Cure', _href=URL('gamectrl', 'curezombie')), _class=''),
                _class='dropdown-menu', _id='gamemenu'),
                _href="#", _class="dropdown-toggle", **{'_data-toggle':'dropdown'}),_class='dropdown')
                ]
        # Menu for dead zombies
        else:
            response.statusmenu = [
                LI(A('Dead ',
                UL(LI(A("Starved " +stime, _href="#"), _class=''),
                _class='dropdown-menu', _id='statusmenu'),
                _href="#", _class="dropdown-toggle",
                **{'_data-toggle':'dropdown'}),_class='dropdown')
                ]

    # Logic for squad menus
    if gpart.game_part.squad_id:
        # regular squad member menu
        if not gpart.game_part.squad_leader:
            response.squadmenu = [
                LI(A('Squad ',UL(
                LI(A('Squad HQ', _href=URL('squad', 'squadhq', args=gpart.game_part.squad_id), _class=''),
                _class=''),_class='dropdown-menu', _id='gamemenu'),
                _href="#", _class="dropdown-toggle", **{'_data-toggle':'dropdown'}),_class='dropdown')
                ]
        # squad leader menu
        elif gpart.game_part.squad_leader:
            response.squadmenu = [
                LI(A('Squad ',UL(
                LI(A('Squad HQ', _href=URL('squad', 'squadhq', args=gpart.game_part.squad_id), _class='')),
                LI(A('Manage Squad', _href=URL('squad', 'squadadmin', args=gpart.game_part.squad_id), _class=''),
                _class=''),_class='dropdown-menu', _id='gamemenu'),
                _href="#", _class="dropdown-toggle", **{'_data-toggle':'dropdown'}),_class='dropdown')
                ]

# Menu if banned
elif gpart and gpart.game_part.banned:
    response.statusmenu = [LI(A('BANNED',_href=URL('gamectrl', 'banned'), _class="",),_class='')]

# menu if no current gamepart and registration open
elif not gpart and gameinfo.checkReg:
    response.statusmenu = [
        LI(A('Register',_href=URL('gamectrl', 'register'), _class="btn btn-default navbar-btn", _id='loginnavbutton'),_class=' ')
    ]
# ---- End Status menu logic ----


# Generic HvZ Menu
response.menu = [
    LI(A('Game',UL(
        LI(A('Roster', _href=URL('default', 'roster')), _class=''),
        LI(A('Forums', _href=URL('forums', 'index')), _class=''),
        LI(A('Squads', _href=URL('squad', 'squadlist')), _class=''),
        LI(A('Ruleset', _href=URL('default', 'rules')), _class=''),
        LI(A('Game Stats', _href=URL('gamectrl', 'gamestatus')), _class=''),
        LI(A('Dev', _href=URL('default', 'status')), _class=''),_class='dropdown-menu', _id='gamemenu'),
        _href="#", _class="dropdown-toggle", **{'_data-toggle':'dropdown'}),_class='dropdown')
        ]

# Admin menu for logged in admins
if auth.is_logged_in() and auth.has_membership('admins'):
    response.adminmenu = [
        LI(A('Admin',_href=URL('admin', 'index'), _class=""),_class=' ')
        ]
# Admin menu for logged in mods
elif auth.is_logged_in() and auth.has_membership('mods'):
    response.adminmenu = [
        LI(A('Admin',_href=URL('admin', 'index'), _class=""),_class=' ')
        ]

# disables adminmenu for non-admins
else:
    response.adminmenu = ' '



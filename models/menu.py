# -*- coding: utf-8 -*-

response.static_version = '1.0.0'

authstat = auth.is_logged_in()
# The logo/header

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Ed Clairmont <jeclairm@gmail.com>'
response.meta.description = 'pandemic'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

# if not authstat:
#    response.menu = [(SPAN('You need to Login', _class='headerhvz'), False, URL('default', 'index'), []),]


# ---- Status menu logic begin ----


# Human menu
if returncurrentuserpart():
    gpart=returncurrentuserpart()
    zombiestat=db.creature_type(gpart.creature_type).zombie
    deadstat=isdead(gpart)
    stime=pretty_date(gpart.zombie_expires_at)
    leaderstat=gpart.squad_leader
    squadstat=gpart.squad_id
    if authstat and not zombiestat and not gpart.banned:
        bcode = gpart.bitecode
        ctype = db.creature_type(gpart.creature_type).name
        response.statusmenu = [
                LI(A(ctype,UL(LI(A('Bitecode', _href=URL('gamectrl', 'bitecodeqrcodepage'), _class='')),
				LI(A(bcode, _href=URL('gamectrl', 'bitecodeqrcodepage'), _class=''), _class=''),
                LI(A('Create Squad', _href=URL('gamectrl', 'createsquadapp'), _class=''), _class=''),
				_class='dropdown-menu', _id='statusmenu'), _href="#", _class="dropdown-toggle",
				**{'_data-toggle':'dropdown'}),_class='dropdown')				
				]
# Zombie menus   
    elif authstat and zombiestat and not gpart.banned:
        ctype = db.creature_type(gpart.creature_type).name
        
        # non-immortal Zombie menu   
        if not db.creature_type(gpart.creature_type).immortal and not deadstat:
            response.statusmenu = [
                LI(A(ctype,UL(LI(A('Bite Somebody', _href=URL('gamectrl', 'bitecodepg')), _class=''),
				LI(A('Cure', _href=URL('gamectrl', 'curezombie')), _class=''),
				LI(A('Starve: ' +stime, _href="#"), _class=''),_class='dropdown-menu', _id='gamemenu'),
				_href="#", _class="dropdown-toggle", **{'_data-toggle':'dropdown'}),_class='dropdown')
            ]
            
            # Immortal zombie menu  
        elif db.creature_type(gpart.creature_type).immortal and not gpart.banned: 
            response.statusmenu = [
                LI(A(ctype,UL(LI(A('Bite Somebody', _href=URL('gamectrl', 'bitecodepg')), _class=''),
				LI(A('Cure', _href=URL('gamectrl', 'curezombie')), _class=''),
				_class='dropdown-menu', _id='gamemenu'),
				_href="#", _class="dropdown-toggle", **{'_data-toggle':'dropdown'}),_class='dropdown')
            ]
            
            # Starved menu            
        elif deadstat and not gpart.banned:
               response.statusmenu = [
					LI(A('Dead ',
					UL(LI(A(stime, _href="#"), _class=''),
					_class='dropdown-menu', _id='statusmenu'),
					_href="#", _class="dropdown-toggle", 
					**{'_data-toggle':'dropdown'}),_class='dropdown')
				]
                
# Squad leader menu                
    if leaderstat and squadstat and not gpart.banned:
        response.squadmenu = [
            LI(A('Squad ',
            UL(LI(A('Squad HQ', _href=URL('gamectrl', 'squadhq', args=gpart.squad_id), _class='')),
            LI(A('Manage Squad', _href=URL('gamectrl', 'squadadmin', args=gpart.squad_id), _class=''),
            _class=''),_class='dropdown-menu', _id='gamemenu'),
            _href="#", _class="dropdown-toggle", **{'_data-toggle':'dropdown'}),_class='dropdown')
        ]
        
# Squad member menu         
    elif squadstat and not leaderstat and not gpart.banned:
        response.squadmenu = [
            LI(A('Squad ',
            UL(LI(A('Squad HQ', _href=URL('gamectrl', 'squadhq', args=gpart.squad_id), _class=''),
            _class=''),_class='dropdown-menu', _id='gamemenu'),
            _href="#", _class="dropdown-toggle", **{'_data-toggle':'dropdown'}),_class='dropdown')
        ]
# Menu if banned   
    elif gpart.banned:
        response.statusmenu = [
         (SPAN('BANNED', _class='headerhvz'), False, URL('default', 'index'),),]    
        
# Menu if not registered for upcoming or current game
elif not returncurrentuserpart() and currentgame() or isgameupcoming():
    response.statusmenu = [
		 	 LI(A('Register',_href=URL('gamectrl', 'register'), _class="btn btn-default navbar-btn", _id='loginnavbutton'),_class=' ')
         ]    
# ---- End Status menu logic ----
    

                      
# Generic HvZ Menu        
response.menu = [
            LI(A('Game',
			UL(LI(A('Roster', _href=URL('default', 'roster')), _class=''),
			LI(A('Forums', _href="/forums"), _class=''),
			LI(A('Squads', _href=URL('default', 'squadlist')), _class=''),
			LI(A('Ruleset', _href=URL('default', 'rules')), _class=''),_class='dropdown-menu', _id='gamemenu'),
			_href="#", _class="dropdown-toggle", **{'_data-toggle':'dropdown'}),_class='dropdown')
]

# Admin menu for logged in admins      
if authstat and auth.has_membership('admins'):
        response.adminmenu = [
            LI(A('Admin',_href=URL('admin', 'index'), _class=""),_class=' ')
        ]
        
# disables adminmenu for non-admins        
else: 
    response.adminmenu = ' '

# landing page link
response.landing = [(SPAN('UMASSHvZ', _class='headerhvz'), False, URL('default', 'index'),[]),]

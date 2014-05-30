# coding: utf8

from fixtime import *

def getEstNow():
    return getNow()

### Begin GameObject Definition
class GameObject(object):
    def __init__(self, id=False, start_at=False, end_at=False, time_per_food=False, stun_timer=0, cure_timer=0,
                 bite_shares_per_food=0,
                 pause_starts_at=0, pause_ends_at=0, created=0, posttimeout=1, signup_start_at=0, signup_end_at=0, game_name=''):
        self.id = id
        self.start_at = start_at
        self.end_at = end_at
        self.time_per_food = time_per_food
        self.stun_timer = stun_timer
        self.cure_timer = cure_timer
        self.signup_start_at = signup_start_at
        self.signup_end_at = signup_end_at
        self.bite_shares_per_food = bite_shares_per_food
        self.pause_starts_at = pause_starts_at
        self.pause_ends_at = pause_ends_at
        self.created = created
        self.posttimeout = posttimeout
        self.game_name = game_name

    def getId(self):
        return self.id

    def gameStart(self):
        return self.start_at

    def gameEnd(self):
        return self.end_at

    def getName(self):
        return self.game_name

    def isGameActive(self):
        if self.start_at > getEstNow() and self.end_at < getEstNow():
            return True
        else:
            return False

    def isGameUpcoming(self):
        if self.start_at < getEstNow() and self.end_at < getEstNow():
            return True
        else:
            return False


# GameVars class definition
class GameVars(GameObject):

    def starveTimer(self):
        return self.time_per_food

    def stunTime(self):
        return self.stun_timer

    def postTimer(self):
        return self.posttimeout


    # checks if registration is open and returns True or False
    def checkReg(self):
        if getEstNow() > self.signup_start_at and getEstNow() <  self.signup_end_at:
            return True
        else:
            return False

    # returns a new starve timer based on the current time per food
    def addFoodTimer(self):
        newtime = getEstNow() + timedelta(seconds=self.time_per_food)
        return newtime

    # returns a starvetimer with only half of the time
    def shareBite(self):
        newtime = getEstNow() + timedelta(seconds=(self.time_per_food/2))
        return newtime

    # checks if a the cure timer has elapsed since a player was last bitten (takes a joined rows object)
    def checkInfection(self, player):
        bitecheck = db(
            (db.bite_event.human_id == player.game_part.id) & (db.bite_event.game_id == self.id)).select().last()
        if bitecheck:
            inftimer = getEstNow() - bitecheck.created
            if self.cure_timer > inftimer.seconds:
                return False
            else:
                return True
        else:
            return False

    # This is called by the bitecodepg controller and returns a bitecode form based on current game variables
    def buildBiteForm(self,qrargs):
        if self.bite_shares_per_food > 0:
            maxshare = int((self.time_per_food*.85))
            form = SQLFORM.factory(Field("Bitecode", default=qrargs),
                                   Field("Lat", default='', writable=True, requires=IS_NOT_EMPTY()),
                                   Field("Long", writable=True, requires=IS_NOT_EMPTY()),
                                   Field("share", 'boolean', label="Share this bite?"),
                                   Field("timeshared", 'integer', default=maxshare, label="Time to share"),
                                   submit_button="Bite!")
        else:
            form = SQLFORM.factory(Field("Bitecode", default=qrargs),
                                   Field("Lat", default='', writable=True, requires=IS_NOT_EMPTY()),
                                   Field("Long", writable=True, requires=IS_NOT_EMPTY()),
                                   Field("share", 'boolean', default=False, writable=False,readable=True),
                                   submit_button="Bite!")
        return form

    def sharingActive(self):
        if self.bite_shares_per_food > 0:
            return True
        else:
            return False

# returns the maximum amout of a share, based on the current time_per_food
    def maxShare(self):
        return int((self.time_per_food*.85))

# returns the minimum amout of a share, based on the current time_per_food
    def minShare(self):
        return int((self.time_per_food*.15))

# returns the total time_per_food
    def timePerFood(self):
        return self.time_per_food

### end GameVars class definition ###
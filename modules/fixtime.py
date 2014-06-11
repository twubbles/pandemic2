# fix for hosting on a server in different timezone
# set the hours to the difference between timezones

from datetime import datetime
from datetime import timedelta

def getEstNow():
    pstnow  = datetime.now()
    tzchange = timedelta(hours=3)
    estnow = pstnow + tzchange
    return estnow

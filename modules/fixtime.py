# datetime.now() tz hack to change the current time from PST to EST, use this instead of doing a datetime.now() to get the current datetime
from datetime import *

def getNow():
    pstnow  = datetime.now()
    tzchange = timedelta(hours=3)
    estnow = pstnow + tzchange
    return estnow
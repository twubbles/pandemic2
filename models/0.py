# This model is for preloading anything the engine needs

# this reloads the modules on change for development purposes and should be removed in production
from gluon.custom_import import track_changes; track_changes(True)

from fixtime import *

def getEstNow():
    return getNow()
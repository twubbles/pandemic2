# Module with various functions related to game administration

from fixtime import getEstNow

# adds a string on a new line to the adminlog text file
def adminlog(string):
    try:
        file = open("adminlog.txt", "a")
        file.write(str(getEstNow()) + ' ' + string + "\n")
        file.close()
        msg = True
    except:
        msg = False
    return msg



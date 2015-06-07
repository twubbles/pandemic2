# def sendlog():
# import os
#     logdir = os.getcwd()
#     logloc = logdir + '/adminlog.txt'
#     try:
#         logstatus = (os.stat(logloc).st_size!= 0)
#     except:
#         logstatus = False
#     if logstatus:
#         with open ("adminlog.txt", "r") as currentlog:
#             logcontents=currentlog.read()
#         oldlog = open("adminlogold.txt", "a")
#         oldlog.write(str("\n" + logcontents))
#         oldlog.close()
#         sendemail("jeclairm@gmail.com", "Admin log updates", logcontents)
#         os.remove(logloc)



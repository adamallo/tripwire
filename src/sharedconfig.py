import imp, re, os

##Configuration varibles
confvars=imp.load_source("config", os.path.dirname(os.path.abspath(__file__))+"/config.txt")
#applescript=os.path.dirname(os.path.abspath(__file__))+"apple_center_window.osascript" Problem with spaces in the directory name
applescript=confvars.centerscript
slackUrl=confvars.url
slackText=confvars.text
slackIcon=confvars.icon
slackUsername=confvars.username

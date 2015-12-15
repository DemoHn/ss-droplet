__author__ = 'Mingchuan'
# date : 2015-11-17

# errcode

errcode = {}

# socket
errcode['400'] = "json parsing error"
errcode['401'] = "input data is not complete"
errcode['402'] = "operation is not allowed"
errcode['403'] = "client IP not Host!"
errcode['405'] = "unknown keyword"
# new_service dispatch error
errcode['420'] = "dispatch unknown error"
errcode['421'] = "dispatch out of quota"
errcode['422'] = "can't dispatch a port"
errcode['423'] = "create instance error"
errcode['424'] = "process creation error"

# service_idf error
errcode['430'] = "service_idf not available"
errcode['431'] = "device num is full"

# process error
errcode['450'] = "kill process error"
errcode["451"] = "create process error"

# when triggering try...except...
errcode["500"] = "fatal error"
errcode['520'] = "data is null"

# database
errcode["600"] = "database error"
errcode["610"] = "can't fetch data"
errcode["620"] = "data is null"
errcode["621"] = "ssid does not exist"
errcode["700"] = "illegal command"

# server_list change_remains error
errcode["710"] = "decline too much"
errcode["720"] = "lid not active"

# login
errcode["730"] = "username duplicated"
errcode["731"] = "no such account"

#route error
#register error
errcode["800"] = "null username is illegal"
errcode["801"] = "password should not shorter than six characters"

errcode["810"] = "unknown error"
errcode["811"] = "no such username"
errcode["812"] = "password error"

errcode["830"] = "auth error"

# check purchase string
errcode["840"] = "purchase check error"
errcode["841"] = "no service to purchase"

# register new sub-server
errcode["860"] = "server key error"

# commuication with sub-nodes error
errcode["880"] = "HTTP commuication error"

# bind error
errcode["900"] = "bind account error"
errcode["901"] = "router IDF not unique"

# about server instance
errcode["1200"] = "create ss-obfs instance failed"

# change traffic error
errcode["1210"] = "traffic increment can't be negative"
errcode["1211"] = "traffic decrement can't be negative"
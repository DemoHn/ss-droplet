errcode = {}

errcode['500'] = "fatal error"
errcode['520'] = "data is null"

# socket
errcode['400'] = "input data is not json"
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
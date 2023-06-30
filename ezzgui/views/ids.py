
_id = 0

def last():
    return _id

def next():
    global _id
    _id += 1
    return _id
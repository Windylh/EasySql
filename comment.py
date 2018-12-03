import hashlib


def str2md5(s):
    s = s.encode('utf-8')
    return hashlib.md5(s).hexdigest()

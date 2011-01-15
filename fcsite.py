#-*- coding:utf-8 -*-

SITE_URL = "http://thefightclub.jp/fc"

def toUTF8(s):
    return s.encode("utf-8", "replace")

def toSafeString(s):
    try:
        return toUTF8(unicode(s.strip(), "cp932"))
    except UnicodeDecodeError:
        # already safe string
        return s

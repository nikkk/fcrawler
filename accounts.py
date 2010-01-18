#-*- coding:utf-8 -*-

import sys
import os

DOT_FCRAWLER_PATH = os.getenv("HOME") + os.path.sep + ".fcrawler"

class Accounts(object):
    def __init__(self):
        pass

    def error(self, msg):
        sys.stderr.write(msg + "\n")
        sys.exit(1)

    def readValue(self, key):
        try:
            f = open(DOT_FCRAWLER_PATH)
            try:
                for line in f:
                    if line.startswith(key):
                        i = len(key)
                        # pass ' ' and '='
                        while i < len(line) and line[i] == " " or line[i] == "=":
                            i += 1
                        return line[i:].strip()
                self.error("%s に %s の値が見つからない" % (DOT_FCRAWLER_PATH, key))
            finally:
                f.close()
        except Exception, e:
            self.error("%s の読み込み中にエラー: %s" % (DOT_FCRAWLER_PATH, e.message))

    googleCalendarEmailCache = None
    def googleCalendarEmail(self):
        if not self.googleCalendarEmailCache:
            self.googleCalendarEmailCache = self.readValue("googleCalendarEmail")
        return self.googleCalendarEmailCache

    googleCalendarPasswordCache = None
    def googleCalendarPassword(self):
        if not self.googleCalendarPasswordCache:
            self.googleCalendarPasswordCache = self.readValue("googleCalendarPassword")
        return self.googleCalendarPasswordCache

    fightclubPasswordCache = None
    def fightclubPassword(self):
        if not self.fightclubPasswordCache:
            self.fightclubPasswordCache = self.readValue("fightclubPassword")
        return self.fightclubPasswordCache

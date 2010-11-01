#-*- coding:utf-8 -*-

import urllib
import re
from fcsite import *


ENTRIED_MEMBERS_LIST_BEGIN = re.compile(r"^1 \.[ <].*")
ENTRIED_MEMBERS_LIST_END = re.compile(r"^<input type=hidden")
ENTRIED_MEMBER = re.compile(r"^[1-9]")

class State(object):
    def __init__(self, acc, url):
        self.account = acc
        self.url = url

    def constructFor(self, key):
        source = self.getSource(key)
        self.members = self.parse(source)

    def getSource(self, key):
        params = urllib.urlencode({
                "name" : self.account.fightclubName(),
                "id" : self.account.fightclubPassword(),
                "key" : key,
                "ej" : "0"
                })
        return urllib.urlopen(self.url, params)

    def parse(self, source):
        bodyLines = []
        inBody = False
        for line in source:
            line = toSafeString(line)
            if ENTRIED_MEMBERS_LIST_BEGIN.match(line):
                inBody = True
                bodyLines.append(line)
            elif ENTRIED_MEMBERS_LIST_END.match(line):
                inBody = False
                return self.analyze(bodyLines)
            elif inBody:
                bodyLines.append(line)
        return None

    def analyze(self, lines):
        cleaned = []
        for line in lines:
            line = self.convertBallMark(line)
            line = self.eraseDecorationTags(line)
            cleaned.append(line.strip())
        return self.parseMembers("".join(cleaned))

    def convertBallMark(self, line):
        return line.replace("<font color=red>v</font>", "[v]")

    def eraseDecorationTags(self, line):
        l = line
        l = l.replace("<font color=blue>参加  ", "")
        l = l.replace("</font>", "")
        l = l.replace("<b>", "")
        l = l.replace("</b>", "")
        return l

    def parseMembers(self, line):
        tokens = line.split("<br>")
        return [t.strip() for t in tokens if ENTRIED_MEMBER.match(t)]

    def asEventContent(self):
        content = "状況：\n"
        mems = "\n".join([" " + self.format(m) for m in self.members])
        return content + mems

    def format(self, line):
        l = line
        l = l.replace(" . ", ". ")
        l = l.replace(" .[", ". [")
        l = l.replace("  ", ": ")
        return l

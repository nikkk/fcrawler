#-*- coding:utf-8 -*-

import urllib
import re
import schedule
from fcsite import *
from pushback import PushbackWrapper

class ScheduleList(object):
    def __init__(self, acc, urlProvider):
        self.account = acc
        self.idx = 0
        self.schedules = []
        self.crawled = False
        self.urlProvider = urlProvider

    def __iter__(self):
        return self

    def crawl(self):
        if self.crawled:
            return
        self.doCrawl()
        self.crawled = True

    def doCrawl(self):
        url = self.urlProvider(self.account)
        source = self.getSource(url)
        self.parse(source)

    def getSource(self, url):
        return urllib.urlopen(url)

    def parse(self, source):
        for line in source:
            line = toSafeString(line)
            if self.beginEntry(line):
                s = self.constructSchedule(source)
                self.schedules.append(s)

    def next(self):
        self.crawl()
        i = self.idx
        if len(self.schedules) <= i:
            raise StopIteration()
        s = self.schedules[i]
        self.idx = i + 1
        return s


def fcURL(acc, baseURL):
    fcPass = acc.fightclubPassword()
    return baseURL % (fcPass)

def renshuURL(acc):
    return fcURL(acc, "http://cgi.members.interq.or.jp/cool/masashi/fc/000.cgi?fs=2&id=%s&ej=0")

def shiaiURL(acc):
    return fcURL(acc, "http://cgi.members.interq.or.jp/cool/masashi/fc/002.cgi?fs=2&id=%s&ej=0")


# 練習情報の解析に利用
RENSHU_ENTRY_BEGIN = re.compile(r"<form action='touroku.cgi' method='post'>")

class RenshuList(ScheduleList):
    def __init__(self, acc):
        ScheduleList.__init__(self, acc, renshuURL)

    def beginEntry(self, line):
        return RENSHU_ENTRY_BEGIN.match(line)

    def constructSchedule(self, source):
        s = schedule.Renshu(self.account)
        s.construct(source)
        return s


# 試合情報の解析に利用
SHIAI_ENTRY_BEGIN = re.compile(r"^(<hr>)?<form action='shiai_touroku.cgi'")

class ShiaiList(ScheduleList):
    def __init__(self, acc):
        ScheduleList.__init__(self, acc, shiaiURL)

    def getSource(self, url):
        return PushbackWrapper(urllib.urlopen(url))

    def beginEntry(self, line):
        return SHIAI_ENTRY_BEGIN.match(line)

    def constructSchedule(self, source):
        s = schedule.Shiai(self.account)
        lastline = s.construct(source)
        source.pushback(lastline)
        return s

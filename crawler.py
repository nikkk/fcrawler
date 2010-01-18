#-*- coding:utf-8 -*-

import re
import urllib
import schedule
import analyzer
import accounts

# 練習情報の解析に利用
RENSHU_REGEX = re.compile(r"^<font size=[0-9]+>([^<].+)$")
# 試合情報の解析に利用
SHIAI_BEGIN_REGEX = re.compile(r"^<font size=[0-9]+ color='#333333'>")
SHIAI_END_REGEX = re.compile(r"^<br>")

def toSafeString(s):
    return analyzer.toUTF8(unicode(s.strip(), "shift_jis"))

class Crawler(object):
    def __init__(self, acc = accounts.Accounts()):
        self.acc = acc
        self.analyzer = analyzer.Analyzer()
        self.alreadyCrawlRenshu = False
        self.alreadyCrawlShiai = False

    def fcURL(self, baseURL):
        fcPass = self.acc.fightclubPassword()
        return baseURL % (fcPass)

    def renshuURL(self):
        return self.fcURL("http://cgi.members.interq.or.jp/cool/masashi/fc/000.cgi?fs=2&id=%s&ej=0")

    def shiaiURL(self):
        return self.fcURL("http://cgi.members.interq.or.jp/cool/masashi/fc/002.cgi?fs=2&id=%s&ej=0")

    def crawlRenshu(self):
        if self.alreadyCrawlRenshu:
            return

        renshuSource = urllib.urlopen(self.renshuURL())
        self.parseRenshuSource(renshuSource)

        self.alreadyCrawlRenshu = True

    def parseRenshuSource(self, source):
        for line in source:
            line = toSafeString(line)
            matcher = RENSHU_REGEX.match(line)
            if matcher:
                renshu = matcher.groups()[0]
                # "<font size=x>任意" の行にもマッチしてしまうので
                # これを省く。練習情報の行は、必ず "場所" で始まる。
                if renshu.startswith("場所"):
                    self.analyzer.analyzeRenshu(renshu)

    def crawlShiai(self):
        if self.alreadyCrawlShiai:
            return

        shiaiSource = urllib.urlopen(self.shiaiURL())
        self.parseShiaiSource(shiaiSource)

        self.alreadyCrawlShiai = True

    def parseShiaiSource(self, source):
        inBody = False
        bodyLines = []
        for line in source:
            line = toSafeString(line)
            if SHIAI_BEGIN_REGEX.match(line):
                inBody = True
            elif SHIAI_END_REGEX.match(line) and inBody:
                inBody = False
                if bodyLines:
                    self.analyzer.analyzeShiai(bodyLines)
                    bodyLines = []
            elif inBody:
                bodyLines.append(line)

    ####
    # イテレータの実装

    def __iter__(self):
        return self

    def next(self):
        self.crawlRenshu()
        nextSchedule = self.analyzer.nextRenshu()
        if nextSchedule:
            return nextSchedule

        self.crawlShiai()
        nextSchedule = self.analyzer.nextShiai()
        if nextSchedule:
            return nextSchedule

        raise StopIteration()

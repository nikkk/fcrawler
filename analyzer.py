#-*- coding:utf-8 -*-

import re
import schedule

# 練習情報の解析に利用
RENSHU_BASHO_REGEX = re.compile("^場所：(.*)$")
NITIJI_REGEX = re.compile("^日時：(.*)$")
COURT_REGEX = re.compile("^コート：(.*)$")
# 試合情報の解析に利用
TAIKAIMEI_REGEX = re.compile(r"^大会名：([^<]*)<br>$")
SHIAIBI_REGEX = re.compile(r"^試合日：([^<]*)<br>$")
UKETUKE_REGEX = re.compile(r"^受付開始：([^<]*)<br>$")
SHIAI_BASHO_REGEX = re.compile(r"^場所：([^<]*)<br>$")

def toUTF8(s):
    return s.encode("utf-8", "replace")

MALE_SINGLES = "男S"
FEMALE_SINGLES = "女S"
MALE_DOUBLES = "男D"
FEMALE_DOUBLES = "女D"
MIX_DOUBLES = "混D"
TEAM = "団体"

TAIKAIME_PATTERNS = {
    "男子シングルス" : MALE_SINGLES,
    "男子ダブルス" : MALE_DOUBLES,
    "男子S" : MALE_SINGLES,
    "男子D" : MALE_DOUBLES,
    "男ダブ" : MALE_DOUBLES,
    "女子シングルス" : FEMALE_SINGLES,
    "女子ダブルス" : FEMALE_DOUBLES,
    "女子S" : FEMALE_SINGLES,
    "女子D" : FEMALE_DOUBLES,
    "女ダブ" : FEMALE_DOUBLES,
    "ミックスダブルス" : MIX_DOUBLES,
    "混合D" : MIX_DOUBLES,
    "団体" : TEAM,
    }

class Analyzer(object):
    def __init__(self):
        self.renshuSchedules = []
        self.renshuIndex = 0
        self.shiaiSchedules = []
        self.shiaiIndex = 0

    def nextRenshu(self):
        if self.renshuIndex < len(self.renshuSchedules):
            s = self.renshuSchedules[self.renshuIndex]
            self.renshuIndex += 1
            return s
        else:
            return None

    def nextShiai(self):
        if self.shiaiIndex < len(self.shiaiSchedules):
            s = self.shiaiSchedules[self.shiaiIndex]
            self.shiaiIndex += 1
            return s
        else:
            return None

    #########
    # 練習情報の解析

    def analyzeRenshu(self, renshu):
        at = courts = date = timeFrom = timeTo = None
        tokens = renshu.split("<br>")
        for token in tokens:
            # at:
            #   場所：$at
            matcher = RENSHU_BASHO_REGEX.match(token)
            if matcher:
                at = self.bashoToAt(matcher.groups()[0])
                continue
            # date, timeFrom, timeTo:
            #   日時：yyMMdd(E)(mm時〜mm時の間)
            matcher = NITIJI_REGEX.match(token)
            if matcher:
                date, timeFrom, timeTo = \
                    self.nitijiToDateTimes(matcher.groups()[0])
                continue
            # courts
            #   コート：$courts
            matcher = COURT_REGEX.match(token)
            if matcher:
                courts = self.courtToCourts(matcher.groups()[0])
                continue
        at = "%s (%s)" % (at, courts)
        category = "練習"
        description = "\n".join(tokens)

        s = schedule.Schedule(
            category, date, timeFrom, timeTo, at, description)
        self.renshuSchedules.append(s)

    def spotNameOnMap(self, basho):
        if "博多の森" in basho:
            return "東平尾公園"
        return basho

    def bashoToAt(self, basho):
        at = None
        if "(" in basho or "（" in basho:
            at = []
            for c in unicode(basho, "utf-8"):
                if c == u"(" or c == u"（":
                    break
                at.append(c)
            at = toUTF8("".join(at))
        else:
            at = basho
        return self.spotNameOnMap(at)

    def skipNotDigits(self, i, s, length):
        if not length:
            length = len(s)
        while i < length and not s[i].isdigit():
            i += 1
        return i

    def collectDigits(self, i, s, length):
        if not length:
            length = len(s)
        result = []
        while i < length and s[i].isdigit():
            result.append(s[i])
            i += 1
        return (i, result)

    def nitijiToDateTimes(self, nitiji):
        # date (yyMMdd -> yyyy-MM-dd)
        date = "20%s-%s-%s" % (nitiji[0:2], nitiji[2:4], nitiji[4:6])
        # timeFrom と timeTo の解析
        i = 6 # date の続きからってことで
        length = len(nitiji) # length はあらかじめ計算しておく
        ## timeFrom (yyMMdd(E)(mm時.*) -> mm:00)
        ### timeFrom までの文字を飛ばす
        i = self.skipNotDigits(i, nitiji, length)
        i, timeFrom = self.collectDigits(i, nitiji, length)
        timeFrom.append(":00")
        ## timeTo   (yyMMdd(E)(xx時〜mm時の間) -> mm:00)
        ### timeFrom と timeTo の間の部分を飛ばす
        i = self.skipNotDigits(i, nitiji, length)
        i, timeTo = self.collectDigits(i, nitiji, length)
        timeTo.append(":00")

        return (date, "".join(timeFrom), "".join(timeTo))

    def courtToCourts(self, court):
        tokens = court.split(",")
        courts = [t for t in tokens if not "-" in t]
        return ", ".join(courts)

    ######
    # 試合情報の解析

    def analyzeShiai(self, shiai):
        category = date = timeFrom = at = None
        for line in shiai:
            # category:
            #   男S, 女S, 男D, 女D, 混D, 団体
            #   大会名：$大会名 $category<br>
            #     フォーマットが不定
            matcher = TAIKAIMEI_REGEX.match(line)
            if matcher:
                category = self.taikaimeiToCategory(matcher.groups()[0])
                continue
            # date:
            #   yyyy-MM-dd
            #   試合日：$date<br>
            #     (yyyy/MM/dd)
            matcher = SHIAIBI_REGEX.match(line)
            if matcher:
                date = self.shiaibiToDate(matcher.groups()[0])
                continue
            # timeFrom:
            #   hh:mm
            #   受付開始：$timeFrom<br>
            matcher = UKETUKE_REGEX.match(line)
            if matcher:
                timeFrom = self.uketukeToTimeFrom(matcher.groups()[0])
                continue
            # at:
            #   フォーマット問わず? 博多の森 -> 東平尾公園
            #   場所：$at
            matcher = SHIAI_BASHO_REGEX.match(line)
            if matcher:
                at = self.bashoToAt(matcher.groups()[0])
                continue
        timeTo = "17:00"
        description = "\n".join(shiai).replace("<br>", "")

        s = schedule.Schedule(
            category, date, timeFrom, timeTo, at, description)
        self.shiaiSchedules.append(s)

    def taikaimeiToCategory(self, taikaimei):
        matched = [c for p, c in TAIKAIME_PATTERNS.items() if p in taikaimei]
        if not matched:
            return taikaimei
        else:
            category = "".join(matched)
            return "%s試合" % (category)

    def shiaibiToDate(self, shiaibi):
        return shiaibi.replace("/", "-")

    def uketukeToTimeFrom(self, uketuke):
        return uketuke

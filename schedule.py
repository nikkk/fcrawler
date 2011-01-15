#-*- coding:utf-8 -*-

import gdata.calendar as gcal
import atom
from fcsite import *
import re
import state

class Schedule(object):
    def __init__(self, acc, stateURL):
        self.state = state.State(acc, stateURL)
        self.key = None

    def construct(self, source):
        content = self.parse(source)
        if not content:
            raise ValueError('failed to construct')
        self.doConstruct(content)
        self.state.constructFor(self.key)

    def doConstruct(self, content):
        at, category, date, description, timeFrom, timeTo = content
        self.at = at
        self.category = category
        self.date = date
        self.description = description
        self.timeFrom = timeFrom
        self.timeTo = timeTo

    def makeContentText(self):
        text = self.description + "\n"
        text = text + self.state.asEventContent() + "\n"
        text = text + "\n" + self.tag()
        return text

    def toEvent(self):
        event = gcal.CalendarEventEntry()
        event.title = atom.Title(text = 'FC ' + self.category + ' at ' + self.at)
        event.content = atom.Content(text = self.makeContentText())
        event.where = gcal.Where(value_string = self.at)
        # 日付フォーマット = yyyy-MM-ddThh:mm:ss.SSS+09:00
        start = self.date + "T" + self.timeFrom + ":00.000+09:00"
        end = self.date + "T" + self.timeTo + ":00.000+09:00"
        event.when.append(gcal.When(start_time = start, end_time = end))
        return event


KEY_REGEX = re.compile(r"^<input type='hidden' name='key' value='([0-9]+)'>")

# 練習情報の解析に利用
RENSHU_REGEX = re.compile(r"^<font size=[0-9]+>([^<].+)$")
RENSHU_STATE_URL = SITE_URL + "/touroku.cgi"
RENSHU_BASHO_REGEX = re.compile("^場所：(.*)$")
NITIJI_REGEX = re.compile("^日時：(.*)$")
COURT_REGEX = re.compile("^コート：(.*)$")

# 試合情報の解析に利用
SHIAI_BEGIN_REGEX = re.compile(r"^<font size=[0-9]+ color='#333333'>")
SHIAI_END_REGEX = re.compile(r"^<hr>")
SHIAI_STATE_URL = SITE_URL + "/shiai_touroku.cgi"
TAIKAIMEI_REGEX = re.compile(r"^大会名：([^<]*)<br>$")
SHIAIBI_REGEX = re.compile(r"^試合日：([^<]*)<br>$")
UKETUKE_REGEX = re.compile(r"^受付開始：([^<]*)<br>$")
SHIAI_BASHO_REGEX = re.compile(r"^場所：([^<]*)<br>$")
MALE_SINGLES = "男S"
FEMALE_SINGLES = "女S"
MALE_DOUBLES = "男D"
FEMALE_DOUBLES = "女D"
MIX_DOUBLES = "混D"
TEAM = "団体"

TAIKAIME_PATTERNS = {
    "男子シングルス" : (MALE_SINGLES, []),
    "男子シングル" : (MALE_SINGLES, []),
    "男子ダブルス" : (MALE_DOUBLES, []),
    "男子S" : (MALE_SINGLES, []),
    "男子D" : (MALE_DOUBLES, []),
    "男ダブ" : (MALE_DOUBLES, []),
    "女子シングルス" : (FEMALE_SINGLES, []),
    "女子シングル" : (FEMALE_SINGLES, []),
    "女子ダブルス" : (FEMALE_DOUBLES, []),
    "女子S" : (FEMALE_SINGLES, []),
    "女子D" : (FEMALE_DOUBLES, []),
    "女ダブ" : (FEMALE_DOUBLES, []),
    "ミックスダブルス" : (MIX_DOUBLES, []),
    "混合D" : (MIX_DOUBLES, []),
    "団体" : (TEAM, []),
    "男子・女子ダブルス" : (MALE_DOUBLES + FEMALE_DOUBLES, [FEMALE_DOUBLES]),
    }

#########
# 解析に用いるヘルパー関数

def bashoToAt(basho):
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
    return spotNameOnMap(at).strip()

def spotNameOnMap(basho):
    if "博多の森" in basho:
        return "東平尾公園"
    return basho.strip()

def skipUntilOpenParen(i, s, length):
    while i < length and not s[i] != "(":
        i += 1
    return i

def skipNotDigits(i, s, length):
    if not length:
        length = len(s)
    while i < length and not s[i].isdigit():
        i += 1
    return i

def collectDigits(i, s, length):
    if not length:
        length = len(s)
    result = []
    while i < length and s[i].isdigit():
        result.append(s[i])
        i += 1
    return (i, result)

def nitijiToDateTimes(nitiji):
    # date (yyMMdd -> yyyy-MM-dd)
    date = "20%s-%s-%s" % (nitiji[0:2], nitiji[2:4], nitiji[4:6])
    # timeFrom と timeTo の解析
    i = 6 # date の続きからってことで
    length = len(nitiji) # length はあらかじめ計算しておく
    ## timeFrom (yyMMdd.*(E)(mm時.*) -> (E)(mm時.*))
    i = skipUntilOpenParen(i, nitiji, length)
    ## timeFrom (yyMMdd(E)(mm時.*) -> mm:00)
    ### timeFrom までの文字を飛ばす
    i = skipNotDigits(i, nitiji, length)
    i, timeFrom = collectDigits(i, nitiji, length)
    timeFrom.append(":00")
    ## timeTo   (yyMMdd(E)(xx時〜mm時の間) -> mm:00)
    ### timeFrom と timeTo の間の部分を飛ばす
    i = skipNotDigits(i, nitiji, length)
    i, timeTo = collectDigits(i, nitiji, length)
    timeTo.append(":00")

    return (date, "".join(timeFrom), "".join(timeTo))

def courtToCourts(court):
    tokens = court.split(",")
    courts = [t for t in tokens if not "-" in t]
    return ", ".join([s.strip() for s in courts])

def unique(items):
  result = []
  for item in items:
      if not item in result:
          result.append(item)
  return result

def findCategoryByName(name, categories):
    for cat in categories:
        if cat[0] == name:
            return cat
    return None

def cleanCategories(matched):
    categories = unique(matched)
    conflicts = []
    for cat in categories:
        cs = cat[1]
        conflicts.extend(cs)
    return [cat[0] for cat in categories if not cat[0] in conflicts]

def taikaimeiToCategory(taikaimei):
    matched = [c for p, c in TAIKAIME_PATTERNS.items() if p in taikaimei]
    if not matched:
        return taikaimei.strip()
    else:
        categories = cleanCategories(matched)
        category = "".join(categories)
        return "%s試合" % (category.strip())

def shiaibiToDate(shiaibi):
    if shiaibi.count("/") == 2:
        return shiaibi.replace("/", "-").strip()
    elif len(shiaibi) == 8:
        y = shiaibi[0:4]
        m = shiaibi[4:6]
        d = shiaibi[6:8]
        return y + "-" + m + "-" + d
    else:
        msg = "よく分からない形式の日付 (試合日): %s" % (shiaibi)
        raise ValueError(msg)

def uketukeToTimeFrom(uketuke):
    if uketuke == "--:--":
        return "08:45"
    else:
        return uketuke.strip()


class Renshu(Schedule):
    def __init__(self, acc):
        Schedule.__init__(self, acc, RENSHU_STATE_URL)

    def parse(self, source):
        for line in source:
            line = toSafeString(line)
            matcher = KEY_REGEX.match(line)
            if not self.key and matcher:
                self.key = matcher.groups()[0]
                continue
            matcher = RENSHU_REGEX.match(line)
            if self.key and matcher:
                renshu = matcher.groups()[0]
                # "<font size=x>任意" の行にもマッチしてしまうので
                # これを省く。練習情報の行は、必ず "場所" で始まる。
                if renshu.startswith("場所"):
                    return self.analyze(renshu)
        return None

    def analyze(self, renshu):
        at = courts = date = timeFrom = timeTo = None
        tokens = renshu.split("<br>")
        for token in tokens:
            # at:
            #   場所：$at
            matcher = RENSHU_BASHO_REGEX.match(token)
            if matcher:
                at = bashoToAt(matcher.groups()[0])
                continue
            # date, timeFrom, timeTo:
            #   日時：yyMMdd(E)(mm時〜mm時の間)
            matcher = NITIJI_REGEX.match(token)
            if matcher:
                date, timeFrom, timeTo = \
                    nitijiToDateTimes(matcher.groups()[0])
                continue
            # courts
            #   コート：$courts
            matcher = COURT_REGEX.match(token)
            if matcher:
                courts = courtToCourts(matcher.groups()[0])
                continue
        at = "%s (%s)" % (at, courts)
        category = "練習"
        description = "\n".join(tokens)
        return (at, category, date, description, timeFrom, timeTo)

    def tag(self):
        return "[fcrawler-r]"


class Shiai(Schedule):
    def __init__(self, acc):
        Schedule.__init__(self, acc, SHIAI_STATE_URL)

    def construct(self, source):
        super(Shiai, self).construct(source)
        return self.lastline

    def parse(self, source):
        inBody = False
        bodyLines = []
        for line in source:
            line = toSafeString(line)
            matcher = KEY_REGEX.match(line)
            if not self.key and matcher:
                self.key = matcher.groups()[0]
                continue
            if self.key and SHIAI_BEGIN_REGEX.match(line):
                inBody = True
            elif self.key and SHIAI_END_REGEX.match(line) and inBody:
                self.lastline = line
                if bodyLines:
                    return self.analyze(bodyLines)
            elif inBody:
                bodyLines.append(line)
        return None

    def analyze(self, shiai):
        category = date = timeFrom = at = None
        for line in shiai:
            # category:
            #   男S, 女S, 男D, 女D, 混D, 団体
            #   大会名：$大会名 $category<br>
            #     フォーマットが不定
            matcher = TAIKAIMEI_REGEX.match(line)
            if matcher:
                category = taikaimeiToCategory(matcher.groups()[0])
                continue
            # date:
            #   yyyy-MM-dd
            #   試合日：$date<br>
            #     (yyyy/MM/dd)
            matcher = SHIAIBI_REGEX.match(line)
            if matcher:
                date = shiaibiToDate(matcher.groups()[0])
                continue
            # timeFrom:
            #   hh:mm
            #   受付開始：$timeFrom<br>
            matcher = UKETUKE_REGEX.match(line)
            if matcher:
                timeFrom = uketukeToTimeFrom(matcher.groups()[0])
                continue
            # at:
            #   フォーマット問わず? 博多の森 -> 東平尾公園
            #   場所：$at
            matcher = SHIAI_BASHO_REGEX.match(line)
            if matcher:
                at = bashoToAt(matcher.groups()[0])
                continue
        timeTo = "17:00"
        description = "\n".join(shiai).replace("<br>", "")

        return (at, category, date, description, timeFrom, timeTo)

    def tag(self):
        return "[fcrawler-s]"

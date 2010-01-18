#-*- coding:utf-8 -*-

import gdata.calendar as gcal
import atom

class Schedule(object):
    def __init__(self, category, date, timeFrom, timeTo, at, description):
        self.category = category
        self.date = date # yyyy-MM-dd
        self.timeFrom = timeFrom # hh:mm
        self.timeTo = timeTo # hh:mm
        self.at = at
        self.description = description

    def toEvent(self):
        event = gcal.CalendarEventEntry()
        event.title = atom.Title(text = 'FC ' + self.category + ' at ' + self.at)
        event.content = atom.Content(text = self.description)
        event.where = gcal.Where(value_string = self.at)
        # 日付フォーマット = yyyy-MM-ddThh:mm:ss.SSS+09:00
        start = self.date + "T" + self.timeFrom + ":00.000+09:00"
        end = self.date + "T" + self.timeTo + ":00.000+09:00"
        event.when.append(gcal.When(start_time = start, end_time = end))
        return event

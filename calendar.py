#-*- coding:utf-8 -*-

import gdata.calendar.service as service

ID = "n81e7gg0tv8ubqrrfd0fco7md8@group.calendar.google.com"
URL = "/calendar/feeds/%s/private/full" % (ID)

class Calendar(object):
    def __init__(self, client):
        self.client = client

    def register(self, events, date, tag):
        self.cleanTaggedEvents(date, tag)
        for e in events:
            self.client.InsertEvent(e, URL)

    def cleanTaggedEvents(self, date, tag):
        query = service.CalendarEventQuery(ID, 'private', 'full')
        query.start_min = date + "T00:00:00.000+09:00"
        query.start_max = date + "T23:59:59.000+09:00"
        feed = self.client.CalendarQuery(query)
        removee = [e for e in feed.entry if e.content.text and tag in e.content.text]
        for e in removee:
            self.client.DeleteEvent(e.GetEditLink().href)

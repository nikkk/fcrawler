#-*- coding:utf-8 -*-

import gdata.calendar.service as service

ID = "n81e7gg0tv8ubqrrfd0fco7md8@group.calendar.google.com"
URL = "/calendar/feeds/%s/private/full" % (ID)

class Calendar(object):
    def __init__(self, client):
        self.client = client

    def alreadyRegistered(self, event):
        query = service.CalendarEventQuery(ID, 'private', 'full')
        query.start_min = event.when[0].start_time
        query.start_max = event.when[0].end_time
        feed = self.client.CalendarQuery(query)
        newTitle = event.title.text
        for e in feed.entry:
            title = e.title.text
            if title == newTitle:
                return True
        return False

    def register(self, event):
        if not self.alreadyRegistered(event):
            self.client.InsertEvent(event, URL)

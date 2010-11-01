#!/usr/bin/env python
#-*- coding:utf-8 -*-

# TODO メッセージを出す

import gdata.calendar.service as service
from schedulelist import *
from calendar import *
from accounts import *

def makeClient(acc):
    client = service.CalendarService()
    client.email = acc.googleCalendarEmail()
    client.password = acc.googleCalendarPassword()
    client.ProgrammaticLogin()
    return client

def registerSchedules(calendar, schedules):
    events = {}
    for schedule in schedules:
        k = (schedule.date, schedule.tag())
        es = events.get(k, [])
        es.append(schedule.toEvent())
        events[k] = es

    for (date, tag), es in events.iteritems():
        calendar.register(es, date, tag)

def main(args):
    accounts = Accounts()
    client = makeClient(accounts)
    calendar = Calendar(client)

    registerSchedules(calendar, RenshuList(accounts))
    registerSchedules(calendar, ShiaiList(accounts))

if __name__ == '__main__':
    import sys
    main(sys.argv)

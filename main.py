#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gdata.calendar.service as service
from crawler import *
from calendar import *
from accounts import *

def makeClient(acc):
    client = service.CalendarService()
    client.email = acc.googleCalendarEmail()
    client.password = acc.googleCalendarPassword()
    client.ProgrammaticLogin()
    return client

def main(args):
    accounts = Accounts()
    crawler = Crawler(accounts)
    client = makeClient(accounts)
    calendar = Calendar(client)

    for schedule in crawler:
        event = schedule.toEvent()
        calendar.register(event)

if __name__ == '__main__':
    import sys
    main(sys.argv)

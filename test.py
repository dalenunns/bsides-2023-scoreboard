#!/bin/python
import urllib.request
import json 
from dateutil import parser
from datetime import datetime
from dateutil.relativedelta import relativedelta

def display_session_data(session):
    sessionType = session["type"]
    sessionTitle = session["title"]
    sessionStart = session["start"]
    sessionSpeaker = ""

    if ("persons" in session):
        if (len(session["persons"]) > 0):
            sessionSpeaker = session["persons"][0]["public_name"]

    print (f'{sessionTitle} - {sessionSpeaker}')
    print (f'{sessionType} - Starts At: {sessionStart}')


your_url = 'https://pretalx.com/bsides-cape-town-2023/schedule/export/schedule.json'
with urllib.request.urlopen(your_url) as url:
    #currentTime = datetime.now()
    currentTime = parser.parse("2023-12-02 7:30:00+02:00")
    data = json.loads(url.read().decode())

    nextSession = False

    for t in data["schedule"]["conference"]["days"][0]["rooms"]["Workshop 1"]:
        talkStartTime = parser.parse(t["date"])
        talkDuration = parser.parse(t["duration"]).time()
        talkEndTime = talkStartTime + relativedelta(minutes=talkDuration.minute, hours=talkDuration.hour)

        # Talk Live Now
        if talkStartTime <= currentTime <= talkEndTime:
            print (f'Current: {currentTime}')
            print (f'Start:{talkStartTime} - End: {talkEndTime} - Duration: {talkDuration}')

            display_session_data(t)

            print('-----------')

        # Next Talk
        nextTimeSlot = currentTime + relativedelta(minutes=talkDuration.minute, hours=talkDuration.hour)

        if talkStartTime <= nextTimeSlot <= talkEndTime:
            nextSession = True
            print (f'Next: {nextTimeSlot}')
            print (f'Start:{talkStartTime} - End: {talkEndTime} - Duration: {talkDuration}')

            display_session_data(t)

            print('-----------')

    if not nextSession:
        for t in data["schedule"]["conference"]["days"][0]["rooms"]["Workshop 1"]:
                talkStartTime = parser.parse(t["date"])
                talkDuration = parser.parse(t["duration"]).time()
                talkEndTime = talkStartTime + relativedelta(minutes=talkDuration.minute, hours=talkDuration.hour)

                print (f'Current: {currentTime}')
                print (f'Start:{talkStartTime} - End: {talkEndTime} - Duration: {talkDuration}')
                
                
                if currentTime <= talkStartTime:
                    print ('Next Session')
                    print (f'Current: {currentTime}')
                    print (f'Start:{talkStartTime} - End: {talkEndTime} - Duration: {talkDuration}')

                    display_session_data(t)

                    print('-----------')
                    break

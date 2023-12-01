#!/bin/python
import urllib.request
import json 
from dateutil import parser
from datetime import datetime
from dateutil.relativedelta import relativedelta

from datetime import datetime
from pytz import timezone    

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

    return {
        "Type":sessionType,
        "Title":sessionTitle,
        "Speaker":sessionSpeaker,
        "StartTime":sessionStart
    }

def empty_data():
    return {
            "Type":'',
            "Title":'',
            "Speaker":'',
            "StartTime":'',
            "EndTime": '',
            "Duration": '',
            "Display":'None'
        }


def scan_track_data(currentTime, track):
    nextSession = False

    track_data = {}

    for t in track:
        talkStartTime = parser.parse(t["date"])
        talkDuration = parser.parse(t["duration"]).time()
        talkEndTime = talkStartTime + relativedelta(minutes=talkDuration.minute, hours=talkDuration.hour)

        # Talk Live Now
        if talkStartTime <= currentTime <= talkEndTime:
            print ("Live NOW")
            # print (f'Current: {currentTime}')
            # print (f'Start:{talkStartTime} - End: {talkEndTime} - Duration: {talkDuration}')

            session_data = display_session_data(t)
            session_data["EndTime"] = str(talkEndTime.time())
            session_data["Duration"] = str(int(((talkEndTime - talkStartTime).total_seconds()/60)))
            session_data["Display"] = 'Block'

            if ("NOW" not in session_data):
                track_data["NOW"] = session_data

            print('-----------')

        # Next Talk
        nextTimeSlot = currentTime + relativedelta(minutes=talkDuration.minute, hours=talkDuration.hour)

        if talkStartTime <= nextTimeSlot <= talkEndTime:
            nextSession = True
            print ("Next:")
            # print (f'Next: {nextTimeSlot}')
            # print (f'Start:{talkStartTime} - End: {talkEndTime} - Duration: {talkDuration}')

            session_data = display_session_data(t)
            session_data["EndTime"] = str(talkEndTime.time())
            session_data["Duration"] = str(int(((talkEndTime - talkStartTime).total_seconds()/60)))
            session_data["Display"] = 'Block'
            
            if ("NEXT" not in session_data):
                track_data["NEXT"] = session_data

            print('-----------')

    if not nextSession:
        for t in track:
                talkStartTime = parser.parse(t["date"])
                talkDuration = parser.parse(t["duration"]).time()
                talkEndTime = talkStartTime + relativedelta(minutes=talkDuration.minute, hours=talkDuration.hour)

                # print (f'Current: {currentTime}')
                # print (f'Start:{talkStartTime} - End: {talkEndTime} - Duration: {talkDuration}')
                
                
                if currentTime <= talkStartTime:
                    print ('Later On')
                    # print (f'Current: {currentTime}')
                    # print (f'Start:{talkStartTime} - End: {talkEndTime} - Duration: {talkDuration}')

                    session_data = display_session_data(t)
                    session_data["EndTime"] = str(talkEndTime.time())
                    session_data["Duration"] = str(int(((talkEndTime - talkStartTime).total_seconds()/60)))
                    session_data["Display"] = 'Block'

                    if ("NEXT" not in session_data):
                        track_data["NEXT"] = session_data


                    print('-----------')
                    break

    if ("NEXT" not in track_data):
        track_data["NEXT"] = empty_data()

    if ("NOW" not in track_data):
        track_data["NOW"] = empty_data()

    return track_data


def fetch_schedule_data():
    your_url = 'https://pretalx.com/bsides-cape-town-2023/schedule/export/schedule.json'
    with urllib.request.urlopen(your_url) as url:
        south_africa = timezone('Africa/Johannesburg')
        currentTime = datetime.now(south_africa)
        #currentTime = parser.parse("2023-12-02 5:50:01+02:00")
        data = json.loads(url.read().decode())

        schedule_data = {}

        for track in data["schedule"]["conference"]["days"][0]["rooms"]:
            nextSession = False    
            print (track)
            schedule_data[track] = scan_track_data(currentTime, data["schedule"]["conference"]["days"][0]["rooms"][track])

        return schedule_data


#!/bin/python

import flask
import html
import json
import subprocess
import time
import os
from flask import send_file, request 
from datetime import datetime
from MessageAnnouncer import MessageAnnouncer

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from flask_caching import Cache

app = flask.Flask(__name__, static_url_path='/static')
announcer = MessageAnnouncer()

executors = {
    'default': ThreadPoolExecutor(16),
    'processpool': ProcessPoolExecutor(4)
}

sched = BackgroundScheduler(timezone='Asia/Seoul', executors=executors)

app.config["SECRET_KEY"] = "blah"
app.config["CACHE_TYPE"] = "FileSystemCache"
app.config["CACHE_DIR"] = "cache/"
cache = Cache(app)

cache.set("sponsor_image_idx", 0)
cache.set("speaker_image_idx", 0)

def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg

### Tasks

# Update scoreboard
def update_scoreboard_task():
    cmd = 'chromium-browser --no-sandbox --headless --disable-gpu --window-size=1920,1080 --timeout=30000 --screenshot=static/scoreboard.png https://2023challenges.bsidescapetown.co.za/scoreboard?fullscreen=1'
    returned_value = subprocess.call(cmd, shell=True)    
    update_scoreboard()

# Show a Sponsor Image
def show_sponsor_task():
    sponsor_image_idx = cache.get("sponsor_image_idx")
    sponsor_image_idx += 1
    cache.set("sponsor_image_idx", sponsor_image_idx)
    displayimage(f'/sponsorfetch?{time.time()}', 30)

# Show a Speaker Image
def show_speaker_task():
    speaker_image_idx = cache.get("speaker_image_idx")
    speaker_image_idx += 1
    cache.set("speaker_image_idx", speaker_image_idx)
    displayimage(f'/speakerfetch?{time.time()}', 30)

###

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/pi')
def pi():
    return send_file('static/pi.html')


@app.route('/scoreboardfetch')
def scoreboardfetch():    
    return send_file('static/scoreboard.png')

@app.route('/sponsorfetch')
def sponsorfetch():
    sponsor_image_idx = cache.get("sponsor_image_idx")
    sponsorFiles = os.listdir('static/sponsors/')
    if (sponsor_image_idx > len(sponsorFiles)):
        cache.set("sponsor_image_idx", 0)
    print (f'Fetching Sponsor {sponsor_image_idx}/{len(sponsorFiles)} - {sponsorFiles[sponsor_image_idx -1]}')
    return send_file(f'static/sponsors/{sponsorFiles[sponsor_image_idx -1]}')

@app.route('/speakerfetch')
def speakerfetch():
    speaker_image_idx = cache.get("speaker_image_idx")
    speakerFiles = os.listdir('static/speakers/')
    if (speaker_image_idx > len(speakerFiles)):
        cache.set("speaker_image_idx", 0)
    print (f'Fetching Speaker {speaker_image_idx}/{len(speakerFiles)} - {speakerFiles[speaker_image_idx -1]}')
    return send_file(f'static/speakers/{speakerFiles[speaker_image_idx -1]}')


# Command & Control Frontend
@app.route('/control')
def control():
    return send_file('static/control.html')

# Force Scoreboard Update
@app.route('/control/update-scoreboard', methods=['POST'])
def update_scoreboard():
    message = f'<img src="/scoreboardfetch?{time.time()}" width="100%" height="100%"/>'

    msg = format_sse(data=message, event='png-scoreboard')

    announcer.announce(msg=msg)
    return {}, 200

# Send a Message
@app.route('/control/message', methods=['POST'])
def message():
    message = ','.join(json.dumps(f'{x}') for x in request.form["message"].splitlines())
    type_msg = f'<div id="element" class="message-overlay"></div><script>new TypeIt("#element", {{strings: [{message}],  speed: 100, html: false, loop: false, lifelike: true, afterComplete: () => setTimeout(function () {{document.getElementById("element").style.display = "none"}},10000) }}).go(); </script>'

    msg = format_sse(data=type_msg, event='message')

    announcer.announce(msg=msg)
    return {}, 200

# Turn on / off Test Pattern
@app.route('/control/test-pattern')
def testpattern():
    state = request.args.get('state', default = "on")
    if (state=="on"):
        test_pattern_style = '<style> .test-pattern { top:0; left:0; z-index: 1000; position: absolute; background-color: #FFFFFF; background-image: url("/static/TestPattern.png"); width: 100%; height: 100%; background-repeat: no-repeat; background-size: contain, cover; background-position: center;} </style>'
        test_pattern_msg = '<div class="test-pattern" width="100%" height="100%"></div>'
    else:
        test_pattern_style = ''
        test_pattern_msg = ''

    msg = format_sse(data=test_pattern_style + test_pattern_msg, event='message')
    announcer.announce(msg=msg)
    return {}, 200

# Display an image
@app.route('/control/display-image')
def displayimage():
    image = request.args.get('image')
    timeout = request.args.get('timeout', default=60, type=int)

    return displayimage(image, timeout)

def displayimage(imagePath, timeout):
    image_style = f'<style> .display-image {{ top:0; left:0; z-index: 90; position: absolute; background-color: #FFFFFF; background-image: url("{imagePath}"); width: 100%; height: 100%; background-repeat: no-repeat; background-size: contain, cover; background-position: center;}} </style>'
    image_msg = '<div id="myImage" class="display-image" width="100%" height="100%"></div>'
    image_script = f'<script>setTimeout(function () {{removeAllChildren(document.getElementById("display-png"))}}, {timeout*1000})</script>'
    
    msg = format_sse(data=image_style + image_msg + image_script, event='display')
    announcer.announce(msg=msg)
    return {}, 200



# Event Stream for the frontend
@app.route('/listen', methods=['GET'])
def listen():

    def stream():
        messages = announcer.listen()  # returns a queue.Queue
        while True:
            msg = messages.get()  # blocks until a new message arrives
            yield msg

    return flask.Response(stream(), mimetype='text/event-stream')

# Fetch screenshot of the scoreboard
sched.add_job(update_scoreboard_task, 'interval', minutes=1)
sched.add_job(show_sponsor_task, 'interval', minutes=3)
sched.add_job(show_speaker_task, 'interval', minutes=2)

if __name__ == '__main__':
    sched.start()
    app.run(debug=True, use_reloader=False, host="192.168.1.22")
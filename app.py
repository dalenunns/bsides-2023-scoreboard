import flask
import html
import json
from flask import send_file, request 
from datetime import datetime
from MessageAnnouncer import MessageAnnouncer

app = flask.Flask(__name__, static_url_path='/static')
announcer = MessageAnnouncer()

def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/pi')
def pi():
    return send_file('static/pi.html')


# Command & Control Frontend
@app.route('/control')
def control():
    return send_file('static/control.html')


@app.route('/message', methods=['POST'])
def message():
    message = ','.join(json.dumps(f'{x}') for x in request.form["message"].splitlines())
    type_msg = f'<div id="element" class="message-overlay"></div><script>new TypeIt("#element", {{strings: [{message}],  speed: 100, html: false, loop: false, lifelike: true, afterComplete: () => setTimeout(function () {{document.getElementById("element").style.display = "none"}},10000) }}).go(); </script>'

    msg = format_sse(data=type_msg, event='message')

    announcer.announce(msg=msg)
    return {}, 200

@app.route('/hack')
def hack():
    video_autoplay_msg = '<video id="myVideo" class="video-overlay" autoplay muted src="/static/JoltAd.mp4" type="video/mp4" width=100%></video>'
    video_autohide_msg = f'<script>document.getElementById("myVideo").onended = function() {{setTimeout(function () {{document.getElementById("myVideo").style.display = "none"}}, 1000)}}</script>'

    msg = format_sse(data=video_autoplay_msg+video_autohide_msg, event='message')
    announcer.announce(msg=msg)
    return {}, 200

@app.route('/test')
def test():
    test_pattern_style = '<style> .test-pattern { top:0; left:0; z-index: 90; position: absolute; background-color: #FFFFFF; background-image: url("/static/TestPattern.png"); width: 100%; height: 100%; background-repeat: no-repeat; background-size: contain, cover; background-position: center;} </style>'
    test_pattern_msg = '<div class="test-pattern" width="100%" height="100%"></div>'
    msg = format_sse(data=test_pattern_style + test_pattern_msg, event='message')
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
import flask
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

# Command & Control Frontend
@app.route('/control')
def control():
    return send_file('static/control.html')



@app.route('/ping')
def ping():
    msg = format_sse(data=f'<b>Hello {datetime.now()} World</b>', event='message')
    
    announcer.announce(msg=msg)
    return {}, 200

@app.route('/message', methods=['POST'])
def message():
    print(request.form)
    type_msg = f'<div id="element"></div><script>new TypeIt("#element", {{strings: "{request.form["message"]}",  speed: 75, loop: false, lifelike: true }}).go(); </script>'

    msg = format_sse(data=type_msg, event='message')

    announcer.announce(msg=msg)
    return {}, 200

@app.route('/hack')
def hack():
    #msg = format_sse(data='<iframe width="420" height="315" src="https://www.youtube.com/embed/34CZjsEI1yU?autoplay=1&mute=1"></iframe>', event='message')
    msg = format_sse(data='<video autoplay muted src="/static/JoltAd.mp4" type="video/mp4" width=100%></video>', event='scoreboard')
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
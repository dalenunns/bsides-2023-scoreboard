import flask
from flask import send_file 
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

@app.route('/hack')
def hack():
    msg = format_sse(data='<iframe width="420" height="315" src="https://www.youtube.com/embed/34CZjsEI1yU?autoplay=1&mute=1"></iframe>', event='message')
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
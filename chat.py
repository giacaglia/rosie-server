import os
import redis
import gevent
from flask import Flask, render_template
from flask_sockets import Sockets
import base64
REDIS_URL = os.environ['REDISCLOUD_URL']
REDIS_CHAN_FRAME = 'frame_1'
REDIS_CHAN_2_FRAME = 'frame_2'
REDIS_CHAN_KEY_HANDLER = 'key_handler'

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ

sockets = Sockets(app)
redis = redis.from_url(REDIS_URL)

class CameraBackend(object):
    def __init__(self):
        self.frame = ""
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN_FRAME)

    def __iter_data(self):
        for message in self.pubsub.listen():
            if message: # ['pattern', 'type', 'channel', 'data']
                data = message["data"]
                frame = str(data)
                yield base64.b64encode(frame)

    def get_frame(self):
        return self.frame

    def register(self, client):
        self.clients.append(client)

    def send(self, client, data):
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        gevent.spawn(self.run)

chats = CameraBackend()
chats.start()

@app.route('/')
def hello():
    return render_template('index.html')

@sockets.route('/submit')
def inbox(ws):
    while not ws.closed:
        gevent.sleep()
        base64_frame = ws.receive()
        if base64_frame:
            frame = base64.b64decode(base64_frame)
            redis.publish(REDIS_CHAN_FRAME, frame)

@sockets.route('/receive')
def outbox(ws):
    chats.register(ws)
    while not ws.closed:
        gevent.sleep()

#
#
# Second camera
#
#
class SecondCameraBackend(object):
    def __init__(self):
        self.frame = ""
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN_2_FRAME)

    def __iter_data(self):
        for message in self.pubsub.listen():
            if message: # ['pattern', 'type', 'channel', 'data']
                data = message["data"]
                frame = str(data)
                yield base64.b64encode(frame)

    def get_frame(self):
        return self.frame

    def register(self, client):
        self.clients.append(client)

    def send(self, client, data):
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        gevent.spawn(self.run)

second_chats = SecondCameraBackend()
second_chats.start()

@sockets.route('/submit_second')
def inbox(ws):
    while not ws.closed:
        gevent.sleep(0.1)
        base64_frame = ws.receive()
        if base64_frame:
            second_frame = base64.b64decode(base64_frame)
            redis.publish(REDIS_CHAN_2_FRAME, second_frame)

@sockets.route('/receive_second')
def outbox(ws):
    second_chats.register(ws)
    while not ws.closed:
        gevent.sleep()

#
#
# Key Down Handler
#
#
class KeyDownHandler(object):
    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN_KEY_HANDLER)

    def __iter_data(self):
        for message in self.pubsub.listen():
            if message:
                data = message["data"]
                print("data")
                print(data)
                yield data


    def register(self, client):
        self.clients.append(client)

    def send(self, client, data):
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        for data in self.__iter_data():
            print("It's iterating")
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        gevent.spawn(self.run)


key_handler = KeyDownHandler()
key_handler.start()

@sockets.route('/key_down')
def inbox(ws):
    while not ws.closed:
        gevent.sleep(0.1)
        message = ws.receive()
        redis.publish(REDIS_CHAN_KEY_HANDLER, message)

@sockets.route('/receive_key_down')
def outbox(ws):
    key_handler.register(ws)
    while not ws.closed:
        gevent.sleep()

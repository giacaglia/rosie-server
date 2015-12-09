import os
import redis
import gevent
from flask import Flask, render_template
from flask_sockets import Sockets
import base64
REDIS_URL = os.environ['REDISCLOUD_URL']
REDIS_CHAN = 'frame1'
REDIS_CHAN_2 = 'frame2'
REDIS_CHAN_KEY_HANDLER = 'key_handler'

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ

sockets = Sockets(app)
redis = redis.from_url(REDIS_URL)

class ChatBackend(object):
    """Interface for registering and updating WebSocket clients."""
    def __init__(self):
        self.frame = ""
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)

    def __iter_data(self):
        for message in self.pubsub.listen():
            if message: # ['pattern', 'type', 'channel', 'data']
                data = message["data"]
                frame = str(data)
                yield base64.b64encode(frame)

    def get_frame(self):
        return self.frame

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)

chats = ChatBackend()
chats.start()

@app.route('/')
def hello():
    return render_template('index.html')

@sockets.route('/submit')
def inbox(ws):
    """Receives incoming chat messages, inserts them into Redis."""
    while not ws.closed:
        # Sleep to prevent *contstant* context-switches.
        gevent.sleep()
        base64_frame = ws.receive()
        if base64_frame:
            frame = base64.b64decode(base64_frame)
            redis.publish(REDIS_CHAN, frame)

@sockets.route('/receive')
def outbox(ws):
    """Sends outgoing chat messages, via `ChatBackend`."""
    chats.register(ws)

    while not ws.closed:
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep()


#
# Second camera
#
#
#
#
class SecondChatBackend(object):
    """Interface for registering and updating WebSocket clients."""
    def __init__(self):
        self.frame = ""
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN_2)

    def __iter_data(self):
        for message in self.pubsub.listen():
            if message: # ['pattern', 'type', 'channel', 'data']
                data = message["data"]
                frame = str(data)
                yield base64.b64encode(frame)

    def get_frame(self):
        return self.frame

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)

second_chats = SecondChatBackend()
second_chats.start()

@sockets.route('/submit_second')
def inbox(ws):
    while not ws.closed:
        gevent.sleep(0.1)
        base64_frame = ws.receive()
        if base64_frame:
            second_frame = base64.b64decode(base64_frame)
            redis.publish(REDIS_CHAN_2, second_frame)

@sockets.route('/receive_second')
def outbox(ws):
    """Sends outgoing chat messages, via `ChatBackend`."""
    second_chats.register(ws)

    while not ws.closed:
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep()

#
#
# Send down key
#
#
class KeyDownHandler(object):
    """Interface for registering and updating WebSocket clients."""
    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN_KEY_HANDLER)

    def __iter_data(self):
        for message in self.pubsub.listen():
            if message: # ['pattern', 'type', 'channel', 'data']
                data = message["data"]
                yield str(data)

    def register(self, client):
        self.clients.append(client)

    def send(self, client, data):
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)


key_handler = KeyDownHandler()
key_handler.start()

@sockets.route('/key_down')
def inbox(ws):
    while not ws.closed:
        gevent.sleep(0.1)
        message = ws.receive()
        print(message)
        redis.publish(REDIS_CHAN_KEY_HANDLER, message)

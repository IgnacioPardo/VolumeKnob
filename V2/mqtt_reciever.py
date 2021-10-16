# Example of using the MQTT client class to subscribe to a feed and print out
# any changes made to the feed.  Edit the variables below to configure the key,
# username, and feed to subscribe to for changes.

# Import standard python modules.
import sys

import multiprocessing
import subprocess

import sys
import glob

# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient

import os

from keys import *

# Set to the ID of the feed to subscribe to for updates.
FEED_ID = 'Test'

prev = -1
process = None

# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID))
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe(FEED_ID)

def subscribe(client, userdata, mid, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print('Subscribed to {0} with QoS {1}'.format(FEED_ID, granted_qos[0]))

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)


def setVolume(v):
    print("Setting volume")
    subprocess.call(["osascript", "-e set volume output volume "+ str(v)])
    return v

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    global prev, process
    new = int(payload)# + (-100)
    if prev != new:
        #if type(process) is multiprocessing.Process:
        #    process.terminate()
        #process = multiprocessing.Process(target=setVolume, args=(new,))
        #process.start()
        setVolume(new)
        prev = new
        subprocess.call(["clear"])
        t = ("🔇" if new == 0 else "🔊" if new > 70 else "🔉" if new > 40 else "🔈") + str(new)
        print(t)

    print('Feed {0} received new value: {1}'.format(feed_id, payload))


# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message
client.on_subscribe  = subscribe

# Connect to the Adafruit IO server.
client.connect()

# Start a message loop that blocks forever waiting for MQTT messages to be
# received.  Note there are other options for running the event loop like doing
# so in a background thread--see the mqtt_client.py example to learn more.
client.loop_blocking()

"""
Simple example of using radzmq.
"""
from radzmq import RadZMQ
import random

ctx = RadZMQ()

url = "inproc://publishing"

with ctx.pub.bound(url) as publisher, ctx.sub.connected_subscriber(url) as subscriber:
    for i in range(10):
        publisher.send([str(random.random())])
        message = subscriber.recv(decode=True)
        for part in message:
            print part

"""
Simple example of configuration with nicezmq decorators.
"""
from nicezmq import NiceZMQ
import gevent
import random
from zmq import green as zmq

ctx = NiceZMQ(zmq.Context())

@ctx.sub.listen("inproc://testing")
def print_message(message):
    print message

@ctx.sub.listen("inproc://testing")
def print_differently(message):
    item = message[0].encode('utf-8')
    print item

with ctx.pub.bound("inproc://testing") as pub:
    def produce():
        while True:
            gevent.sleep(1)
            pub.send([str(random.random())])

    greenlets = ctx.start(gevent.spawn_link)
    greenlets.append(gevent.spawn_link(produce))

    gevent.joinall(greenlets)

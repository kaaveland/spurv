"""
Simple example of configuration with nicezmq decorators.
"""
from nicezmq import NiceZMQ
import gevent
import random
from zmq import green as zmq

ctx = NiceZMQ(zmq.Context())

@ctx.sub.listen("inproc://testing", subs="nothinggoeshere")
def print_message(message):
    print message

@ctx.sub.listen("inproc://testing", subs="test")
def print_differently(message):
    for item in message:
        print item.encode(ctx.encoding)

@ctx.rep.listen("inproc://test-req", bind=False)
def ack_message(message):
    print "Acking ", message
    return ["Ack"] + message

with ctx.pub.bound(ctx.endpoint(print_message)) as pub,\
      ctx.req.bound(ctx.endpoint(ack_message)) as req:
    def produce():
        while True:
            gevent.sleep(1)
            pub.send(["test", str(random.random())])
    def request():
        while True:
            print "Sending request"
            req.send(str(random.random()))
            gevent.sleep(1)
            print req.recv()

    greenlets = ctx.start(gevent.spawn_link)
    greenlets.append(gevent.spawn_link(produce))
    greenlets.append(gevent.spawn_link(request))
    gevent.joinall(greenlets)

"""
Simple example of configuration with spurv decorators.
"""
from spurv import Spurv
import gevent
import random
from zmq import green as zmq

ctx = Spurv(zmq.Context())

@ctx.sub.listen("inproc://testing", subs="one")
def print_message(message):
    print "Subscriber one", message

@ctx.sub.listen("inproc://testing", subs="two")
def print_differently(message):
    print "Subscriber two", message

@ctx.rep.listen("inproc://test-req", bind=False)
def ack_message(message):
    return ["Ack"] + message

with ctx.pub.bound(ctx.url_to(print_message)) as pub,\
      ctx.req.bound(ctx.url_to(ack_message)) as req:
    def produce():
        while True:
            gevent.sleep(1)
            if random.random() < 0.5:
                pub.send(["one", str(random.random())])
            else:
                pub.send(["two", "Not random at all"])
    def request():
        while True:
            req.send(str(random.random()))
            gevent.sleep(1)
            print "Requestor", req.recv()
    greenlets = ctx.start(gevent.spawn_link)
    greenlets.append(gevent.spawn_link(produce))
    greenlets.append(gevent.spawn_link(request))
    gevent.joinall(greenlets)

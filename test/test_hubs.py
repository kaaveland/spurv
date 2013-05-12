# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of nicezmq. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

from nose import tools as test
from nicezmq import Hub, Sub, Pub, Socket, Req, Rep, u
from zmq import Context

class destroying(object):

    def __init__(self, thing):
        self.thing = thing

    def __enter__(self):
        return self.thing

    def __exit__(self, type_, value, traceback):
        self.thing.destroy()

def test_can_create_hubs():
    with destroying(Context()) as ctx:
        Hub(ctx)
        Sub(ctx)
        Pub(ctx)
        Req(ctx)
        Rep(ctx)

def test_hubs_should_create_wrapped_sockets():
    with destroying(Context()) as ctx:
        pub, sub = Pub(ctx, Socket), Sub(ctx, Socket)
        with pub.socket() as sock:
            test.assert_is_instance(sock, Socket)
        with sub.socket() as sock:
            test.assert_is_instance(sock, Socket)

url = "inproc://testing"

def test_pubsub_simple_message_passing():
    with destroying(Context()) as ctx:
        pub, sub = Pub(ctx), Sub(ctx)
        with pub.bound(url) as publisher, sub.connected_subscriber(url, '') as subscriber:
            publisher.send("test")
            test.eq_(["test"], subscriber.recv(decode=True))
            publisher.send(["test", "test"])
            test.eq_(["test", "test"], subscriber.recv(decode=True))

def test_repreq_simple_message_passing():
    with destroying(Context()) as ctx:
        req, rep = Req(ctx), Rep(ctx)
        with rep.bound(url) as reply, req.connected(url) as request:
            message = [u("Testing"), u("Testing")]
            request.send(message)
            got = reply.recv(decode=True)
            test.eq_(message, got)
            reply.send(message)
            got = request.recv(decode=True)
            test.eq_(message, got)

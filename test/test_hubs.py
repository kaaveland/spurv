# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of radzmq. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

from nose import tools as test
from radzmq import Hub, Sub, Pub, Socket, Req, Rep, u, HUB_TYPES
from zmq import Context, ZMQError
from mock import Mock

class destroying(object):

    def __init__(self, thing):
        self.thing = thing

    def __enter__(self):
        return self.thing

    def __exit__(self, type_, value, traceback):
        self.thing.destroy()

def test_can_create_hubs():
    with destroying(Context()) as ctx:
        for hub_type in HUB_TYPES:
            hub_type(ctx)

def test_hubs_should_create_wrapped_sockets():
    with destroying(Context()) as ctx:
        for hub_type in HUB_TYPES:
            hub = hub_type(ctx)
            test.assert_is_instance(hub.socket(), Socket)

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

def test_sub_listen_for_howlers():
    with destroying(Context()) as ctx:
        sub = Sub(ctx)
        @sub.listen("inproc://test", bind=True)
        def foo():
            pass
        test.assert_in(foo.__name__, sub.handlers)
        not_none = object()
        spawner = Mock(return_value=not_none)
        test.assert_in(not_none, sub.start(spawner))

def test_rep_listen_for_howlers():
    with destroying(Context()) as ctx:
        rep = Rep(ctx)
        @rep.listen("inproc://test")
        def foo():
            pass
        test.assert_in(foo.__name__, rep.handlers)
        not_none = object()
        spawner = Mock(return_value=not_none)
        test.assert_in(not_none, rep.start(spawner))

def test_bind_random_port():
    with destroying(Context()) as ctx:
        rep = Rep(ctx)
        socket = rep.bound("tcp://*", True)
        test.assert_is_not_none(socket.port)
        try:
            rep.bound("tcp://*:{}".format(socket.port))
            test.fail("Port should already be bound")
        except ZMQError:
            pass # Expected

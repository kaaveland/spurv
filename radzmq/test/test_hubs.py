# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of radzmq. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.
from ..hub import Sub, Pub, Socket, Req, Rep, HUB_TYPES
from ..enc import u, is_unicode, is_bytes
from zmq import Context, ZMQError
from mock import Mock, MagicMock

zmqsock = Mock()
socket = Socket(zmqsock)

def test_should_recv_list():
    inp = [u("hoaueoa")]
    zmqsock.recv_multipart = MagicMock(return_value=inp)
    out = socket.recv()
    assert inp == out

def test_should_decode_items():
    inp = [u("åp.,åp").encode("utf-8"), u("å,.å,.").encode("utf-8")]
    zmqsock.recv_multipart = MagicMock(return_value=inp)
    out = socket.recv(decode=True)
    for output in out:
        assert is_unicode(output)

def test_should_decode_specific_items_if_asked_for():
    inp = [u("å,.å,").encode("utf-8"), u("ueoue").encode("utf-8")]
    zmqsock.recv_multipart = MagicMock(return_value=inp)
    first, second = socket.recv(decode=(0,))
    assert is_unicode(first)
    assert is_bytes(second)

def test_send_has_no_howlers():
    socket.send(u("test"))
    socket.send([u("test")])

class destroying(object):

    def __init__(self, thing):
        self.thing = thing

    def __enter__(self):
        return self.thing

    def __exit__(self, type_, value, traceback):
        self.thing.destroy()

def test_can_create_hubs():
    with destroying(Context()) as ctx:
        for hub_type in HUB_TYPES.values():
            hub_type(ctx)

def test_hubs_should_create_wrapped_sockets():
    with destroying(Context()) as ctx:
        for hub_type in HUB_TYPES.values():
            hub = hub_type(ctx)
            assert isinstance(hub.socket(), Socket)

url = "inproc://testing"

def test_pubsub_simple_message_passing():
    with destroying(Context()) as ctx:
        pub, sub = Pub(ctx), Sub(ctx)
        with pub.bound(url) as publisher:
            with sub.connected_subscriber(url, '') as subscriber:
                publisher.send("test")
                assert ["test"] == subscriber.recv(decode=True)
                publisher.send(["test", "test"])
                assert ["test", "test"] == subscriber.recv(decode=True)

def test_repreq_simple_message_passing():
    with destroying(Context()) as ctx:
        req, rep = Req(ctx), Rep(ctx)
        with rep.bound(url) as reply:
            with req.connected(url) as request:
                message = [u("Testing"), u("Testing")]
                request.send(message)
                got = reply.recv(decode=True)
                assert message == got
                reply.send(message)
                got = request.recv(decode=True)
                assert message == got

def test_sub_listen_for_howlers():
    with destroying(Context()) as ctx:
        sub = Sub(ctx)
        @sub.listen("inproc://test", bind=True)
        def foo():
            pass
        assert foo.__name__ in sub.handlers
        not_none = object()
        spawner = Mock(return_value=not_none)
        assert not_none in sub.start(spawner)

def test_rep_listen_for_howlers():
    with destroying(Context()) as ctx:
        rep = Rep(ctx)
        @rep.listen("inproc://test")
        def foo():
            pass
        assert foo.__name__ in rep.handlers
        not_none = object()
        spawner = Mock(return_value=not_none)
        assert not_none in rep.start(spawner)

def test_bind_random_port():
    with destroying(Context()) as ctx:
        rep = Rep(ctx)
        socket = rep.bound("tcp://*", True)
        assert socket.port is not None
        try:
            rep.bound("tcp://*:{0}".format(socket.port))
            assert 0, "Should have thrown"
        except ZMQError:
            pass # Expected

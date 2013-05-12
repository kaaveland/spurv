# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of nicezmq. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.
from nose import tools as test
from nicezmq import Socket, u, unicode_type, bytes_type
from mock import MagicMock, Mock

zmqsock = Mock()
socket = Socket(zmqsock)

def test_should_recv_list():
    inp = [u("hoaueoa")]
    zmqsock.recv_multipart = MagicMock(return_value=inp)
    out = socket.recv()
    test.eq_(inp, out)

def test_should_decode_items():
    inp = [u("åp.,åp").encode("utf-8"), u("å,.å,.").encode("utf-8")]
    zmqsock.recv_multipart = MagicMock(return_value=inp)
    out = socket.recv(decode=True)
    for output in out:
        test.assert_is_instance(output, unicode_type)

def test_should_decode_specific_items_if_asked_for():
    inp = [u("å,.å,").encode("utf-8"), u("ueoue").encode("utf-8")]
    zmqsock.recv_multipart = MagicMock(return_value=inp)
    first, second = socket.recv(decode=(0,))
    test.assert_is_instance(first, unicode_type)
    test.assert_is_instance(second, bytes_type)

def test_send_has_no_howlers():
    socket.send(u("test"))
    socket.send([u("test")])

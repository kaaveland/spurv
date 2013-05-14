# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of radzmq. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.
from radzmq import RadZMQ
from nose.tools import raises

def test_constructing_radmq_object():
    rzmq = RadZMQ()
    assert rzmq.context is not None
    assert rzmq.handlers is not None

def test_context_handling():
    with RadZMQ() as rzmq:
        assert rzmq.context is not None

@raises(KeyError)
def test_crashes_on_erronous_url():
    with RadZMQ() as rzmq:
        rzmq.url_to(test_context_handling)

def test_gets_url_to_registered_handler():
    with RadZMQ() as rzmq:
        addr = "inproc://testing"
        @rzmq.sub.listen(addr)
        def foo(msg):
            return msg
        @rzmq.rep.listen(addr)
        def bar(msg):
            return msg
        assert addr == rzmq.url_to(foo)
        assert addr == rzmq.url_to(bar)

# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of nicezmq. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

from nose import tools as test
from nicezmq import NiceZMQ

def test_constructing_nicemq_object():
    nzmq = NiceZMQ()
    test.assert_is_not_none(nzmq.context)
    test.assert_is_not_none(nzmq.handlers)

def test_context_handling():
    with NiceZMQ() as nzmq:
        test.assert_is_not_none(nzmq.context)

@test.raises(KeyError)
def test_crashes_on_erronous_endpoint():
    with NiceZMQ() as nzmq:
        nzmq.endpoint(test_context_handling)

def test_gets_address_for_registered_endpoint():
    with NiceZMQ() as nzmq:
        addr = "inproc://testing"
        @nzmq.sub.listen(addr)
        def foo(msg):
            return msg
        @nzmq.rep.listen(addr)
        def bar(msg):
            return msg
        test.eq_(addr, nzmq.endpoint(foo))
        test.eq_(addr, nzmq.endpoint(bar))

# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of spurv. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.
from .. import Spurv
from nose.tools import raises

def test_constructing_radmq_object():
    ctx = Spurv()
    assert ctx.context is not None

def test_context_handling():
    with Spurv() as spurv:
        assert spurv.context is not None

@raises(KeyError)
def test_crashes_on_erronous_url():
    with Spurv() as spurv:
        spurv.url_to(test_context_handling)

def test_gets_url_to_registered_handler():
    with Spurv() as spurv:
        addr = "inproc://testing"
        @spurv.sub.listen(addr)
        def foo(msg):
            return msg
        @spurv.rep.listen(addr)
        def bar(msg):
            return msg
        assert addr == spurv.url_to(foo)
        assert addr == spurv.url_to(bar)

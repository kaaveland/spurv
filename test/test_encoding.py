# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of radzmq. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.
from nose import tools as test
from radzmq import u, bytes_type, EncoderMixin

encoder = EncoderMixin()

def test_encodes_string():
    test.assert_is_instance(encoder.encode_items("føueå"), bytes_type)

def test_encodes_list_of_string():
    inp = [u("foo/øe"), u("blørg")]
    encoded = encoder.encode_items(inp)
    test.eq_(len(inp), len(encoded))
    for item in encoded:
        test.assert_is_instance(item, bytes_type)

@test.raises(Exception)
def test_throws_on_nonsense_input():
    encoder.encode(object())

def test_does_not_touch_bytes_input():
    inp = u("testinput").encode("ascii")
    test.assert_is_instance(inp, bytes_type)
    out = encoder.encode_items(inp)
    test.assert_is_instance(inp, bytes_type)
    test.eq_(inp, out)

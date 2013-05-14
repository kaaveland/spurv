# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of radzmq. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.
from nose.tools import raises
from radzmq import u, bytes_type, EncoderMixin

encoder = EncoderMixin()

def test_encodes_string():
    assert isinstance(encoder.encode_items("føueå"), bytes_type)

def test_encodes_list_of_string():
    inp = [u("foo/øe"), u("blørg")]
    encoded = encoder.encode_items(inp)
    assert len(inp) == len(encoded)
    for item in encoded:
        assert isinstance(item, bytes_type)

@raises(Exception)
def test_throws_on_nonsense_input():
    encoder.encode(object())

def test_does_not_touch_bytes_input():
    inp = u("testinput").encode("ascii")
    assert isinstance(inp, bytes_type)
    out = encoder.encode_items(inp)
    assert isinstance(inp, bytes_type)
    assert inp == out

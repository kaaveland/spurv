# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of radzmq. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.
"""
This module exists for encoding convenience and string-compatibility
with both py2 / py3.
"""

import sys

if sys.version_info[0] == 2:
    string_types = (unicode, str)
    unicode_type = unicode
    bytes_type = str
    def _decode(bs, encoding="utf-8"):
        return bs.decode(encoding)
else:
    string_types = (str, bytes)
    unicode_type = str
    bytes_type = bytes
    def _decode(bs, encoding="utf-8"):
        if isinstance(bs, unicode_type):
            return bs
        return str(bs, encoding)

u = _decode

def is_bytes(thing):
    return isinstance(thing, bytes_type)

def is_unicode(thing):
    return isinstance(thing, unicode_type)

def is_string(thing):
    return isinstance(thing, string_types)

class EncoderMixin(object):

    encoding = "utf-8"

    def encode_items(self, content):
        """Encode all unicode arguments. Argument may be an iterable
        of string-likes or a string-like itself. It is an error to pass
        an argument that is not either a string-like or an iterable of
        string-likes."""
        if is_string(content):
            if is_unicode(content):
                return content.encode(self.encoding)
            else:
                return content
        return [self.encode_items(item) for item in content]

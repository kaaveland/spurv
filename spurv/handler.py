# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of spurv. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.
"""
Registering and starting handlers on sockets.
"""

from .enc import is_string

def reply_forever(socket, handler, decode=True):
    with socket:
        while True:
            message = socket.recv(decode=decode)
            reply = handler(message)
            socket.send(reply)

def listen_forever(socket, handler, decode=True):
    with socket:
        while True:
            message = socket.recv(decode=decode)
            handler(message)

class Handler(object):

    def __init__(self, hub, addr, fn, bind, decode, subs=None):
        self.addr = addr
        self.hub = hub
        self.fn = fn
        self.bind = bind
        self.decode = decode
        self.subs = subs

    def socket(self):
        if self.bind:
            if self.subs is not None:
                return self.hub.bound(self.addr, self.subs)
            else:
                return self.hub.bound(self.addr)
        else:
            if self.subs is not None:
                return self.hub.connected(self.addr, self.subs)
            else:
                return self.hub.connected(self.addr)

class HandlerMixin(object):

    def __init__(self):
        self._handlers = []
        self._addr_mapping = {}
        self._name_mapping = {}

    @property
    def handlers(self):
        return self._handlers

    @property
    def name_mapping(self):
        return self._name_mapping

    @property
    def addr_mapping(self):
        return self._addr_mapping

    def handler_by_name(self, name):
        if is_string(name):
            return self.name_mapping[name]
        else:
            return self.name_mapping[name.__name__]

    def url_to(self, name):
        handler = self.handler_by_name(name)
        return handler.addr

    def _add_handler(self, addr, bind, decode, fn, subs=None):
        handler = Handler(self, addr, bind, decode, fn, subs)
        self.handlers.append(handler)
        self.addr_mapping[addr] = handler
        self.name_mapping[fn.__name__] = handler
        return fn

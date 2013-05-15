# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of radzmq. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

"""
Registering and starting handlers on sockets.
"""

def bound_first(handlers):
    return reversed(sorted(handlers, key=lambda handler: handler["bind"]))

class HandlerMixin(object):

    def _start_handler(self, spawn, spawnable, handler):
        bind, addr = handler["bind"], handler["endpoint"]
        fn = handler["handler"]
        decode, subs = handler["decode"], handler.get("subs", None)
        if bind:
            if subs is not None:
                sock = self.bound_subscriber(addr, subs)
            else:
                sock = self.bound(addr)
        else:
            if subs is not None:
                sock = self.connected_subscriber(addr, subs)
            else:
                sock = self.connected(addr)
        return spawn(spawnable, sock, fn, decode)

    def start_handling(self, spawn, spawnable):
        return [self._start_handler(spawn, spawnable, handler) for handler in
                bound_first(self.handlers.values())]

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

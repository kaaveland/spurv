# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of radzmq. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.

"""
Provides a few basic abstractions on top of pyzmq.

The idea here is to make it easier to use some very basic configurations
of zmq. The basic interface hides a lot of the gory details of pyzmq
to make it easier to get started with, but every instance has access
to the underlying pyzmq object to enable more advanced usage if
necessary.
"""

import sys
import zmq

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

class EncoderMixin(object):

    encoding = "utf-8"

    def encode_items(self, content):
        """Encode all unicode arguments. Argument may be an iterable
        of string-likes or a string-like itself. It is an error to pass
        an argument that is not either a string-like or an iterable of
        string-likes."""
        if isinstance(content, string_types):
            if isinstance(content, unicode_type):
                return content.encode(self.encoding)
            else:
                return content
        return [self.encode_items(item) for item in content]


class Socket(EncoderMixin):
    """An abstraction on a zmq socket to differentiate socket types.

    Not all methods of the underlying socket are exposed here. In
    particular, the methods that send or receive python objects or
    json objects are left out because they don't do anything sane
    when they fail. This is very apparent when using the REQ/REP
    socket pair - if something that isn't legal json is sent to
    a REP socket, it can come into a weird state where it has received
    a message but doesn't see that it needs to reply, causing the other
    end to hang on its recv().

    In general, consult zmq.core.socket.Socket for documentation on
    the various methods.

    The underlying zmq socket is available as the property zmqsock.
    """

    @property
    def zmqsock(self):
        return self._zmqsock

    @property
    def connected(self):
        return self._connected

    @property
    def port(self):
        """This is only valid for TCP sockets."""
        return self._port

    def __init__(self, zmqsock, encoding="utf-8", port=None):
        super(Socket, self).__init__()
        self._zmqsock = zmqsock
        self.encoding = encoding
        self._connected = False
        self._port = port

    def send(self, content, flags=0, copy=True, track=False):
        """This accepts unicode and will use the encoding set on this
        socket if it is necessary to encode.

        It will also accept iterables that are not string-types, if so
        they are sent as multipart messages."""

        encoded = self.encode_items(content)
        if isinstance(encoded, string_types):
            return self.zmqsock.send(encoded, flags, copy, track)
        else:
            return self.zmqsock.send_multipart(encoded, flags, copy, track)

    def recv(self, decode=False, flags=0, copy=True, track=False):
        """This receives using multipart reception, returning all parts of the
        message in a list.

        If decode is specified, it may be either an iterable specifying which
        parts of the message to decode or it may simply be True to decode all parts.
        """

        items = self.zmqsock.recv_multipart(flags, copy, track)
        if not decode:
            return items
        try:
            iter(decode)
        except TypeError:
            if decode:
                return [_decode(item, self.encoding) for item in items]
        else:
            return [_decode(item, self.encoding) if index in decode else item
                    for index, item in enumerate(items)]

    def close(self, linger=None):
        self.zmqsock.close(linger)
        self._connected = False

    def __exit__(self, type_, value, traceback):
        self.close()

    def __enter__(self):
        return self

    def connect(self, address):
        self.zmqsock.connect(address)
        self._update_port(address)
        self._connected = True

    def bind(self, address):
        self.zmqsock.bind(address)
        self._update_port(address)
        self._connected = True

    def _update_port(self, address):
        if address.startswith("tcp://"):
            port = address.split(":")[-1]
            try:
                self._port = int(port)
            except ValueError:
                pass # Fine, wasn't something numeric

    def bind_to_random_port(self, address, min_port=49152, max_port=65536, tries=100):
        port = self.zmqsock.bind_to_random_port(address, min_port, max_port, tries)
        self._connected = True
        self._port = port
        return port

class Hub(EncoderMixin):
    """For creating sockets of some type and registering them."""

    @property
    def context(self):
        return self.ctx

    @property
    def handlers(self):
        return self._handlers

    def __init__(self, ctx, socket_class=Socket, encoding="utf-8"):
        super(Hub, self).__init__()
        self.ctx = ctx
        self.encoding = encoding
        self.socket_class = socket_class
        self._handlers = {}

    def _wrap(self, socket):
        return self.socket_class(socket, encoding=self.encoding)

    def _socket(self, socktype):
        return self.context.socket(socktype)

    def socket(self):
        """Implemented by subclasses."""

    def _subscribe(self, sock, subs=None):
        if subs is None:
            return
        subs = self.encode_items(subs)
        if isinstance(subs, string_types):
            sock.zmqsock.setsockopt(zmq.SUBSCRIBE, subs)
        else:
            for sub in subs:
                sock.zmqsock.setsockopt(zmq.SUBSCRIBE, sub)

    def bound(self, address, random_port=False):
        """Ask this hub for a socket bound to an address."""
        socket = self.socket()
        if random_port:
            socket.bind_to_random_port(address)
        else:
            socket.bind(address)
        return socket

    def connected(self, address):
        """Ask this hub for a socket connected to an address."""
        socket = self.socket()
        socket.connect(address)
        return socket

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

class Sub(Hub, HandlerMixin):
    """Hub for creating sockets of the SUB type."""

    def socket(self):
        return self._wrap(self._socket(zmq.SUB))

    def connected_subscriber(self, address, subscriptions=''):
        socket = self.connected(address)
        self._subscribe(socket, subscriptions)
        return socket

    def bound_subscriber(self, address, subscriptions=''):
        socket = self.bound(address)
        self._subscribe(socket, subscriptions)
        return socket

    def listen(self, address, subs='', decode=True, bind=False):
        def listener(handler):
            self.handlers[handler.__name__] = {
                "bind": bind,
                "endpoint": address,
                "handler": handler,
                "decode": decode,
                "subs": subs
            }
            return handler
        return listener

    def start(self, spawn):
        return self.start_handling(spawn, listen_forever)

class Pub(Hub):
    """Hub for creating sockets of the PUB type."""

    def socket(self):
        return self._wrap(self._socket(zmq.PUB))

class Req(Hub):

    def socket(self):
        return self._wrap(self._socket(zmq.REQ))

class Rep(Hub, HandlerMixin):

    def socket(self):
        return self._wrap(self._socket(zmq.REP))

    def listen(self, address, decode=True, bind=True):
        def listener(handler):
            self.handlers[handler.__name__] = {
                "bind": bind,
                "decode": decode,
                "endpoint": address,
                "handler": handler
            }
            return handler
        return listener

    def start(self, spawn):
        return self.start_handling(spawn, reply_forever)

class Router(Hub):

    def socket(self):
        return self._wrap(self._socket(zmq.ROUTER))

class Dealer(Hub):

    def socket(self):
        return self._wrap(self._socket(zmq.DEALER))

class Pull(Hub):

    def socket(self):
        return self._wrap(self._socket(zmq.PULL))

class Push(Hub):

    def socket(self):
        return self._wrap(self._socket(zmq.PUSH))

class RadZMQ(EncoderMixin):
    """Abstraction over a pyzmq context.
    """

    sock_types = {"_sub": Sub, "_pub": Pub, "_req": Req, "_rep": Rep,
                  "_router": Router, "_dealer": Dealer, "_pull": Pull,
                  "_push": Push}

    def __init__(self, ctx=None, socket_class=Socket, encoding="utf-8"):
        """Initialize using the provided zeromq context.

        Arguments:
        - `ctx`: A zeromq context.
        """
        super(RadZMQ, self).__init__()
        if ctx is None:
            self.ctx = zmq.Context()
        else:
            self.ctx = ctx
        self.encoding = encoding
        for attr, cls in self.sock_types.items():
            setattr(self, attr,
                    cls(self.ctx, encoding=encoding, socket_class=socket_class))

    def destroy(self):
        self.ctx.destroy()

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.destroy()

    @property
    def context(self):
        return self.ctx

    @property
    def sub(self):
        """Hub for SUB sockets."""
        return self._sub

    @property
    def pub(self):
        """Hub for PUB sockets."""
        return self._pub

    @property
    def req(self):
        """Hub for REQ sockets."""
        return self._req

    @property
    def rep(self):
        """Hub for REP sockets."""
        return self._rep

    @property
    def router(self):
        return self._router

    @property
    def dealer(self):
        return self._dealer

    @property
    def pull(self):
        return self._pull

    @property
    def push(self):
        return self._push

    def start(self, spawn):
        """Run forever, using spawn to create listeners."""
        threads = self.sub.start(spawn)
        threads.extend(self.rep.start(spawn))
        return threads

    @property
    def handlers(self):
        handlers = {}
        handlers.update(self.sub.handlers)
        handlers.update(self.rep.handlers)
        return handlers

    def url_to(self, handler):
        if not isinstance(handler, string_types):
            handler = handler.__name__
        return self.handlers[handler]["endpoint"]

HUB_TYPES = [
    Sub,
    Pub,
    Router,
    Dealer,
    Req,
    Rep,
    Pull,
    Push
]

# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of nicezmq. It is distributed under the terms
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

    def __init__(self, zmqsock, encoding="utf-8"):
        super(Socket, self).__init__()
        self._zmqsock = zmqsock
        self.encoding = encoding
        self._connected = False

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
        self._connected = True

    def bind(self, address):
        self.zmqsock.bind(address)
        self._connected = True

class Hub(EncoderMixin):
    """For creating sockets of some type and registering them."""

    @property
    def context(self):
        return self.ctx

    def __init__(self, ctx, socket_class=Socket, encoding="utf-8"):
        super(Hub, self).__init__()
        self.ctx = ctx
        self.encoding = encoding
        self.socket_class = socket_class
        self._endpoints = {}
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

    def bound(self, address):
        """Ask this hub for a socket bound to an address."""
        socket = self.socket()
        socket.bind(address)
        return socket

    def connected(self, address):
        """Ask this hub for a socket connected to an address."""
        socket = self.socket()
        socket.connect(address)
        return socket

class Sub(Hub):
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

class Pub(Hub):
    """Hub for creating sockets of the PUB type."""

    def socket(self):
        return self._wrap(self._socket(zmq.PUB))

class Req(Hub):

    def socket(self):
        return self._wrap(self._socket(zmq.REQ))

class Rep(Hub):

    def socket(self):
        return self._wrap(self._socket(zmq.REP))

class NiceZMQ(EncoderMixin):
    """Abstraction over a pyzmq context.
    """

    sock_types = {"_sub": Sub, "_pub": Pub, "_req": Req, "_rep": Rep}

    def __init__(self, ctx=None, socket_class=Socket, encoding="utf-8"):
        """Initialize using the provided zeromq context.

        Arguments:
        - `ctx`: A zeromq context.
        """
        super(NiceZMQ, self).__init__()
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

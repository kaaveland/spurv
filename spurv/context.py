# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of spurv. It is distributed under the terms
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
import zmq
from . import hub, enc

class Spurv(enc.EncoderMixin):
    """Abstraction over a pyzmq context.
    """

    def __init__(self, ctx=None, socket_class=hub.Socket, encoding="utf-8"):
        """Initialize using the provided zeromq context.

        Arguments:
        - `ctx`: A zeromq context.
        """
        super(Spurv, self).__init__()
        if ctx is None:
            self.ctx = zmq.Context()
        else:
            self.ctx = ctx
        self.encoding = encoding
        self._hubs = []
        def make(hubcls):
            _hub = hubcls(self.ctx, socket_class, self.encoding)
            self._hubs.append(_hub)
            return _hub
        self.pub = make(hub.Pub)
        self.sub = make(hub.Sub)
        self.xpub = make(hub.XPub)
        self.xsub = make(hub.XSub)
        self.rep = make(hub.Rep)
        self.req = make(hub.Req)
        self.pull = make(hub.Pull)
        self.push = make(hub.Push)
        self.router = make(hub.Router)
        self.dealer = make(hub.Dealer)
        self.pair = make(hub.Pair)

    def destroy(self):
        self.ctx.destroy()

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.destroy()

    def start(self, spawn):
        """Run forever, using spawn to create listeners."""
        return list(self._start(spawn))

    def _start(self, spawn):
        for hub in self._hubs:
            for handler in hub.handlers:
                yield spawn(handler.start)

    @property
    def context(self):
        return self.ctx

    def url_to(self, handler):
        for container in self._hubs:
            try:
                return container.url_to(handler)
            except KeyError:
                pass
        raise KeyError("Handler not registered: {0}".format(repr(handler)))

    def handlers(self):
        for container in self._hubs:
            for handler in container.handlers:
                yield handler

    def __repr__(self):

        return repr(self.__dict__)

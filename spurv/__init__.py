# coding=utf-8
# Copyright (c) 2013 Robin Kåveland Hansen
#
# This file is a part of spurv. It is distributed under the terms
# of the modified BSD license. The full license is available in
# LICENSE, distributed as part of this software.
"""
Provides a few basic abstractions on top of pyzmq.

The idea here is to make it easier to use some very basic configurations
of zmq. The basic interface hides a lot of the 'gory' details of pyzmq
to make it easier to get started with, but every instance has access
to the underlying pyzmq object to enable more advanced usage if
necessary.
"""

from .context import Spurv

# spurv

Simpler usage of zeromq.

spurv aims to bring a higher level interface to the excellent pyzmq
library. The idea is to make python programs using zmq to look less
like they're interfacing with C and to provide an easy way to set up
sockets, listen on sockets and run applications which have many
different endpoints to post or listen to.

Check out tox.ini to see which pythons it supports.

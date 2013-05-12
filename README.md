# nicezmq

Simpler usage of zeromq.

nicezmq aims to bring a higher level interface to the excellent pyzmq
library. The idea is to make python programs using zmq to look less
like they're interfacing with C and to provide an easy way to set up
sockets, listen on sockets and run applications which have many
different endpoints to post or listen to.

There is a tradeoff here where the simpler interface does not provide
all the power of pyzmq but the underlying pyzmq objects are not hidden
and they can be used where simple is too simple.

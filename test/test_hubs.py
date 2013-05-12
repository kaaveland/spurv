from nose import tools as test
from nicezmq import Hub, Sub, Pub, Socket
from zmq import Context

class destroying(object):

    def __init__(self, thing):
        self.thing = thing

    def __enter__(self):
        return self.thing

    def __exit__(self, type_, value, traceback):
        self.thing.destroy()

def test_can_create_hubs():
    with destroying(Context()) as ctx:
        Hub(ctx)
        Sub(ctx)
        Pub(ctx)

def test_hubs_should_create_wrapped_sockets():
    with destroying(Context()) as ctx:
        pub, sub = Pub(ctx, Socket), Sub(ctx, Socket)
        with pub.socket() as sock:
            test.assert_is_instance(sock, Socket)
        with sub.socket() as sock:
            test.assert_is_instance(sock, Socket)

url = "inproc://testing"

def test_pubsub_message_passing():
    with destroying(Context()) as ctx:
        pub, sub = Pub(ctx), Sub(ctx)
        with pub.bound(url) as publisher, sub.connected(url, '') as subscriber:
            publisher.send("test")
            test.eq_(["test"], subscriber.recv())
            publisher.send(["test", "test"])
            test.eq_(["test", "test"], subscriber.recv())

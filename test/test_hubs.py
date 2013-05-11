from nose import tools as test
from nicezmq import Hub, Sub, Pub, Socket
from zmq import Context

ctx = Context()

def test_can_create_a_hub():
    Hub(ctx, Socket)

def test_can_create_a_sub():
    Sub(ctx, Socket)

def test_can_create_a_pub():
    Pub(ctx, Socket)

sub = Sub(ctx, Socket)
pub = Sub(ctx, Socket)

def test_hubs_should_create_wrapped_sockets():
    test.assert_is_instance(pub.socket(), Socket)
    test.assert_is_instance(sub.socket(), Socket)

def test_bound_pub_sub_connected():
    url = "tcp://127.0.0.1:30500"
    publisher = pub.bound(url)
    test.assert_is_not_none(publisher.zmqsock)
    subscriber = sub.connected(url)
    test.assert_is_not_none(subscriber.zmqsock)
    publisher.send("test")
    test.eq_(["test"], subscriber.recv())

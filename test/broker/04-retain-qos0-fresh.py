#!/usr/bin/env python3

# Test whether a retained PUBLISH to a topic with QoS 0 is sent with
# retain=false to an already subscribed client.

from mosq_test_helper import *

def do_test(start_broker, proto_ver):
    rc = 1
    mid = 16
    connect_packet = mosq_test.gen_connect("retain-qos0-fresh", proto_ver=proto_ver)
    connack_packet = mosq_test.gen_connack(rc=0, proto_ver=proto_ver)

    publish_packet = mosq_test.gen_publish("retain/qos0/fresh", qos=0, payload="retained message", retain=True, proto_ver=proto_ver)
    publish_fresh_packet = mosq_test.gen_publish("retain/qos0/fresh", qos=0, payload="retained message", proto_ver=proto_ver)
    subscribe_packet = mosq_test.gen_subscribe(mid, "retain/qos0/fresh", 0, proto_ver=proto_ver)
    suback_packet = mosq_test.gen_suback(mid, 0, proto_ver=proto_ver)

    publish_packet_clear = mosq_test.gen_publish("retain/qos0/fresh", qos=0, payload=None, retain=True, proto_ver=proto_ver)
    port = mosq_test.get_port()
    if start_broker:
        broker = mosq_test.start_broker(filename=os.path.basename(__file__), port=port)

    try:
        sock = mosq_test.do_client_connect(connect_packet, connack_packet, port=port)
        mosq_test.do_send_receive(sock, subscribe_packet, suback_packet, "suback")
        mosq_test.do_send_receive(sock, publish_packet, publish_fresh_packet, "publish")
        sock.send(publish_packet_clear)

        rc = 0

        sock.close()
    except mosq_test.TestError:
        pass
    finally:
        if start_broker:
            broker.terminate()
            broker.wait()
            (stdo, stde) = broker.communicate()
            if rc:
                print(stde.decode('utf-8'))
                print("proto_ver=%d" % (proto_ver))
                exit(rc)
        else:
            return rc


def all_tests(start_broker=False):
    rc = do_test(start_broker, proto_ver=4)
    if rc:
        return rc;
    rc = do_test(start_broker, proto_ver=5)
    if rc:
        return rc;
    return 0

if __name__ == '__main__':
    all_tests(True)

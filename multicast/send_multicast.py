#!/usr/bin/python3

import socket
import time

LOCAL_IP = '0.0.0.0'
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

MULTICAST_TTL = 10

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_MULTICAST_IF,
                socket.inet_aton(LOCAL_IP))

count = 0
while True:
    message = 'this is test:{0}'.format(count).encode('utf-8')
    print(message)
    sock.sendto(message, (MCAST_GRP, MCAST_PORT))
    count +=1
    time.sleep(1)


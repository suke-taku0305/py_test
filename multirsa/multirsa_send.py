#!/usr/bin/python3

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import socket
import time
import pickle

LOCAL_IP = '0.0.0.0'
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

MULTICAST_TTL = 10

data = "this is secret message".encode("utf-8")

block_size = AES.block_size
 
recipient_key1 = RSA.import_key(open("key/public1.pem").read())
recipient_key2 = RSA.import_key(open("key/public2.pem").read())
session_key = get_random_bytes(16)
print(recipient_key1)
print(recipient_key2)

multiplied = int(recipient_key1) * int(recipient_key2)
print("multiplied public key:", multiplied)
 
# encrypt session key with rsa
cipher_rsa = PKCS1_OAEP.new(recipient_key1)
enc_session_key = cipher_rsa.encrypt(session_key)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_MULTICAST_IF,
                socket.inet_aton(LOCAL_IP))

#initial parameter
print("prepair initial parameter")
param = {"session_key": enc_session_key}
param = pickle.dumps(param)
sock.sendto(param, (MCAST_GRP, MCAST_PORT))
time.sleep(1)

count = 0
while True:
    message = 'this is secret test: {0}'.format(count)

    print("sended message is:", message)

    message = message.encode('utf-8')

    message_padded = message + b'\0' * (block_size - len(message) % block_size)

    iv = get_random_bytes(16)

    cipher_aes = AES.new(session_key, AES.MODE_CBC, iv)

    ciphertext = cipher_aes.encrypt(message_padded)

    ciphertext = {"iv": iv, "ciphertext": ciphertext}
    data = pickle.dumps(ciphertext)
    sock.sendto(data, (MCAST_GRP, MCAST_PORT))
    count +=1
    time.sleep(2)

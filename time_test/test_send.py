#!/usr/bin/python3

# I try to make rsa by myself

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import socket
import time
import pickle


LOCAL_IP = '0.0.0.0'
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

MULTICAST_TTL = 10

#custom encryption
def rsa_encrypt(plaintext, e, n):
    return int(pow(int.from_bytes(plaintext, "big"), e, n))

data = "this is secret message".encode("utf-8")

block_size = AES.block_size

recipient_key1 = RSA.import_key(open("key/public1.pem").read())
recipient_key2 = RSA.import_key(open("key/public2.pem").read())

session_key = get_random_bytes(16)
custom_modulus = recipient_key1.n * recipient_key2.n

#simple rsa encryption
enc_session_key = rsa_encrypt(session_key, 65537, custom_modulus).to_bytes(512, "big")

cipherlength = len(enc_session_key)
print("cipher length:", cipherlength)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_MULTICAST_IF,
                socket.inet_aton(LOCAL_IP))

#initial parameter
print("prepair initial parameter")
param = {"session_key": enc_session_key}
param = pickle.dumps(param)
sock.sendto(param, (MCAST_GRP, MCAST_PORT))
print("send param time is:", time.time())
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
    print("send data time is:", time.time())
    count +=1
    time.sleep(2)

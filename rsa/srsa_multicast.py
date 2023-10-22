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
# file_out = open("encrypted_data.txt", "wb")
 
recipient_key = RSA.import_key(open("public.pem").read())
session_key = get_random_bytes(16)
 
# encrypt session key with rsa
cipher_rsa = PKCS1_OAEP.new(recipient_key)
enc_session_key = cipher_rsa.encrypt(session_key)
 
# encrypt data with AES session key
cipher_aes = AES.new(session_key, AES.MODE_EAX)
# ciphertext, tag = cipher_aes.encrypt_and_digest(data)
# [file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]
# file_out.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_MULTICAST_IF,
                socket.inet_aton(LOCAL_IP))

#initial parameter
param = {"session_key": enc_session_key, "nonce": cipher_aes.nonce}
print("prepair initial parameter")
print(param)
param = pickle.dumps(param)
sock.sendto(param, (MCAST_GRP, MCAST_PORT))
time.sleep(1)

count = 0
while True:
    # message = 'this is test:{0}'.format(count).encode('utf-8')
    # print(message)
    # sock.sendto(message, (MCAST_GRP, MCAST_PORT))
    message = 'this is secret test: {0}'.format(count).encode('utf-8')

    # this is tested but didn't work
    # if count == 0:
    #     ciphertext, tag = cipher_aes.encrypt_and_digest(message)
    #     data = {"tag": tag, "ciphertext": ciphertext }
    # else:
    #     ciphertext = cipher_aes.encrypt(message)
    #     data = {"ciphertext": ciphertext}

    ciphertext, tag = cipher_aes.encrypt_and_digest(message)
    data = {"tag": tag, "ciphertext": ciphertext }
    # cipher_aes.update(tag)

    # print(ciphertext)
    # sock.sendto(ciphertext, (MCAST_GRP, MCAST_PORT))
    # time.sleep(1)
    # data = {"tag": tag, "ciphertext": ciphertext }
    # print(data)
    data = pickle.dumps(data)
    sock.sendto(data, (MCAST_GRP, MCAST_PORT))
    count +=1
    time.sleep(2)

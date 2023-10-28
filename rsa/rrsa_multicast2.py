#!/usr/bin/python36

import socket
import struct
import pickle

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
LOCAL_IP = '0.0.0.0'
 
private_key = RSA.import_key(open("private.pem").read())

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((MCAST_GRP, MCAST_PORT))

sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_ADD_MEMBERSHIP,
                socket.inet_aton(MCAST_GRP) + socket.inet_aton(LOCAL_IP))

print("waiting sender...")

session_nonce = False
tag_text = False
text_only = False

while True:
  msg=sock.recv(10240)
  # print(msg.decode("utf-8"))
  data=pickle.loads(msg)
  if "session_key" in data and "nonce" in data:
    print("get session key and nonce")
    enc_session_key, nonce = data["session_key"], data["nonce"]
    session_nonce = True
  elif "tag" in data and "ciphertext" in data:
    print("get tag and ciphertext")
    tag, ciphertext = data["tag"], data["ciphertext"]
    tag_text = True
  elif "ciphertext" in data:
    print("get ciphertext")
    ciphertext = data["ciphertext"]
    text_only = True
  else:
    print("Incorrect message") 
  # print(data)

  # enc_session_key, nonce, tag, ciphertext = data["session_key"], data["nonce"], data["tag"], data["ciphertext"]
 
  if session_nonce and tag_text:
    # decrypt session key with rsa private key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)
 
    # decrypt data with aes session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    text = cipher_aes.decrypt_and_verify(ciphertext, tag)
    print(text.decode("utf-8"))
    # if tag_text:
    #   text = cipher_aes.decrypt_and_verify(ciphertext, tag)
    #   print(text.decode("utf-8"))
    # elif text_only:
    #   text = cipher_aes.decrypt(ciphertext)
    #   print(text.decode("utf-8"))
    # else:
    #   print("not text yet...")
  else:
    print("waiting parameter...")
  # msg_data=cipher_aes.decrypt_and_verify(msg, tag)
  # print(msg_data.decode("utf-8"))
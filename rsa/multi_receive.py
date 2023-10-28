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

is_session_key = False
iv_text = False

while True:
  msg=sock.recv(10240)
  # print(msg.decode("utf-8"))
  data=pickle.loads(msg)
  if "session_key" in data:
    print("get session key")
    enc_session_key = data["session_key"]
    is_session_key = True
  elif "iv" in data and "ciphertext" in data:
    print("get iv and ciphertext")
    iv, ciphertext = data["iv"], data["ciphertext"]
    iv_text = True
  else:
    print("Incorrect message")
 
  if is_session_key:
    # decrypt session key with rsa private key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)
    print("get session_key")
  else:
    print("waiting session_key...")

  if iv_text:
     # decrypt data with aes session key
    cipher_aes = AES.new(session_key, AES.MODE_CBC, iv)
    text = cipher_aes.decrypt(ciphertext)
    unpadded_message = text.rstrip(b'\0')
    print("Decrypt message:", unpadded_message.decode("utf-8"))
    iv_text = False
  else:
    print("waiting message...")
  # msg_data=cipher_aes.decrypt_and_verify(msg, tag)
  # print(msg_data.decode("utf-8"))
#!/usr/bin/python36

import socket
import pickle
import time
import glob

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
LOCAL_IP = '0.0.0.0'

#custom decryption
def rsa_decrypt(ciphertext, d, n):
  return pow(int.from_bytes(ciphertext, "big"), d, n)

private_files = glob.glob("../mykey/private*.pem")
private_file = private_files[0]
 
private_key = RSA.import_key(open(private_file).read())
print("privatekey length:", private_key.size_in_bytes())

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))

sock.setsockopt(socket.IPPROTO_IP,
                socket.IP_ADD_MEMBERSHIP,
                socket.inet_aton(MCAST_GRP) + socket.inet_aton(LOCAL_IP))

def receive_ciphertext():
  print("waiting sender...")
  sock.settimeout(10)
  is_session_key = False
  iv_text = False

  count = 0

  while True:
    msg, sender = sock.recvfrom(10240)
    data=pickle.loads(msg)
    if "session_key" in data:
      print("get session key time is:", time.time())
      enc_session_key = data["session_key"]
      is_session_key = True
    elif "iv" in data and "ciphertext" in data:
      print("get iv and ciphertext time is:", time.time())
      iv, ciphertext = data["iv"], data["ciphertext"]
      iv_text = True
    else:
      print("Incorrect message")
  
    if is_session_key and count == 0:
      session_key = rsa_decrypt(enc_session_key, private_key.d, private_key.n).to_bytes(16, "big")
      ack_session_key = f'session_key:{time.time()}'
      sock.sendto(bytes(ack_session_key, 'utf-8'), sender)
    elif not is_session_key:
      print("waiting session_key...")
    else:
      ()

    if iv_text:
      # decrypt data with aes session key
      cipher_aes = AES.new(session_key, AES.MODE_CBC, iv)
      text = cipher_aes.decrypt(ciphertext)
      unpadded_message = text.rstrip(b'\0')
      print("Decrypt message:", unpadded_message.decode("utf-8"))
      ack_decrypt = f'decrypt:{time.time()}'
      sock.sendto(bytes(ack_decrypt, 'utf-8'), sender)
      print("ack sended:", ack_decrypt)
      iv_text = False
    else:
      print("waiting message...")

      count += 1

if __name__ == "__main__":
  receive_ciphertext()
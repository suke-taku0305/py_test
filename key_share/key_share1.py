#!/usr/bin/python3

from Crypto.PublicKey import RSA
import socket
import pickle

def generate_key():
    # 秘密鍵の作成
    key = RSA.generate(2048)
    private_key = key.export_key()
    file_out = open("key/private1.pem", "wb")
    file_out.write(private_key)
    file_out.close()
    
    # 公開鍵の作成
    public_key = key.publickey().export_key()
    file_out = open("key/public1.pem", "wb")
    file_out.write(public_key)
    file_out.close()

    return public_key

def share_publickey(key):
    LOCAL_IP = '0.0.0.0'
    MCAST_GRP = '224.1.1.1'
    MCAST_PORT = 5007

    MULTICAST_TTL = 10

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    sock.setsockopt(socket.IPPROTO_IP,
                    socket.IP_MULTICAST_IF,
                    socket.inet_aton(LOCAL_IP))
    
    id_key = {"index":1,"key":key}
    message = pickle.dumps(id_key)
    sock.sendto(message, (MCAST_GRP, MCAST_PORT))

if __name__ == "__main__":
    publickey = generate_key()
    share_publickey(publickey)

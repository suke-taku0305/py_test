import asyncio
import socket

# マルチキャストグループ情報
MULTICAST_GROUP = '224.0.0.1'
MULTICAST_PORT = 9999

# マルチキャストメッセージを送信する関数
async def send_multicast_message():
    message = "Hello, Multicast World!"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.sendto(message.encode(), (MULTICAST_GROUP, MULTICAST_PORT))

# マルチキャストメッセージを受信する関数
async def receive_multicast_message():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.bind(('', MULTICAST_PORT))
    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode()
        print(f"Received: {message}")

async def main():
    await asyncio.gather(send_multicast_message(), receive_multicast_message())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

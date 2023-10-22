import socket

def request(req):
    # ソケットオブジェクトの生成
    # socket.AF_INET: IPv4の利用
    # socket.SOCK_STREAM: TCPの利用
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ホスト&ポートを指定
    sock.connect(('127.0.0.1', 1235))
    # 接続オプション
    # socket.SOL_SOCKET: ソケット通信
    # socket.SO_REUSEADDR: 待ち状態中のポートが存在してもbindする
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # リクエストする
    sock.send(req.encode("UTF-8"))
    # レスポンス内容を取得
    msg = sock.recv(1024)
    print(msg.decode("utf-8"))

if __name__ == '__main__':
    for i in range(10):
        request(f"request: {i}")
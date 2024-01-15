import socket

sock = socket.socket()

sock.bind(('localhost', 8080))
sock.listen(5)

while True:
    # 套接字，地址
    conn, addr = sock.accept() # 阻塞等待
    # 取1k数据
    data = conn.recv(1024)
    print(f"客户端发送：{data.decode('utf-8')}")
    conn.send(b'HTTP/1.1 200 OK\r\n\r\n')
    conn.send(b'<h1>Hello, World!</h1>')
    conn.close()
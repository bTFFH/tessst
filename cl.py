# import socket
# import threading
#
#
# def connection(host, port):
#     sock = socket.socket()
#     # sock.bind(('', 9090))
#     # sock.listen(1)
#
#     return sock.connect((host,port))
#     # conn,addr = sock.accept()
#
# def a(c):
#     print(c.recv(1024).decode())
#     threading.Thread(target=a, args=(c,)).start()
#
#
# if __name__ == "__main__":
#     host = input("Enter your host address (nothing for default) > ")
#
#     if host:
#         port = int(input("Enter your host's port > "))
#         sock = connection(host, port)
#     else:
#         sock = connection("95.165.143.1", 9090)
#
#     threading.Thread(target=a, args=(sock,)).start()
#
#     while True:
#         txt = input(">")
#         if txt == "stop":
#             break
#         sock.send(txt.encode())
#
#     sock.close()

import socket
import threading


sock=socket.socket()

#sock.bind(('',9090))
#sock.listen(1)

sock.connect(("95.165.143.1",9090))

#conn,addr=sock.accept()

def a(c):
    print(c.recv(1024).decode())
    threading.Thread(target=a,args=(c,)).start()

threading.Thread(target=a,args=(sock,)).start()

while True:
    txt=input(">")
    if txt=="stop":
        break
    sock.send(txt.encode())

sock.close()

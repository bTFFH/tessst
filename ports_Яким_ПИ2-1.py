# -*- coding: utf-8 -*-
import socket
import threading
import time


def scanning(host, start=0, end=65536):

    if __name__ == "__main__":
        global available_ports
    else:
        available_ports = list()

    for port in range(start, end):

        sock = socket.socket()

        try:
           # sock.bind(('127.0.0.1', port))
           sock.bind((host, port))

        except OSError:
           pass

        else:
           sock.close()
           # print("Port {} is avilable".format(port))
           available_ports.append(port)

    if __name__ != "__main__":
        return available_ports


            
if __name__=="__main__":

    available_ports = list()

    host = input("Enter the host's name/IP (nothing for self test) > ")
    step = int(input("Enter scanning step > "))

    if not host:
        host = "127.0.0.1"

    threads_list = []
    progress = 0

    for i in range(0, 65536, step):
        if i + step > 65535:
            threads_list.append(threading.Thread(target=scanning, args=(host, i)))
            threads_list[-1].start()
        else:
            threads_list.append(threading.Thread(target=scanning, args=(host, i, i + step)))
            threads_list[-1].start()

    for i in threads_list:
        i.join()
        progress += 100 / (65536 / step)
        print("Completed {:.2f} %".format(progress if progress < 100 else 100))

    print("\nScanning was successfully completed!\n")
    time.sleep(3)

    for i in set(available_ports):
        print("Port {} is available".format(i))
    # time.sleep(5)

    input("Press Enter to exit")

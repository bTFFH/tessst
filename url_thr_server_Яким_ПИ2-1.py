# -*- coding: utf-8 -*-
"""Служебные файлы: url_log.txt - хранит логи сервера
                    url_log_server.txt - хранит логи серверной части работыс ервера
                    url_data.txt - json formatted database"""
import socket
import json
import threading
import time
import os


class TheServer(object):
    """Basic threaded server"""
    log_file = open("url_log.txt", "wt")
    files_dict = {}

    def __init__(self, host="", port=53310):
        self.host = host
        self.port = port
        self.sock = socket.socket()
        self.sock.bind((self.host, self.port))
        type(self).log_file.write("\n$$$$$ Now server starts with port {} $$$$$\n\tVVV\n".format(self.port))
        type(self).log_file.write("Current users: {}\n".format(self.get_data()))
        type(self).log_file.flush()
        threading.Thread(target=self.refresh).start()
        self.listen()

    def refresh(self):
        """Refreshing list containing paths each 15 seconds"""
        type(self).files_dict = {i[0] + "\\" + file: file for i in os.walk(
            os.environ["HOMEDRIVE"] + os.environ["HOMEPATH"]) for file in i[2]}
        time.sleep(15)

    def write_log(self, string):
        """Log writing"""
        type(self).log_file.write("{} > {}".format(
            time.strftime("%d/%b/%Y %H:%M:%S -%Z", time.localtime(time.time())), string)
        )
        type(self).log_file.flush()

    @staticmethod
    def get_data():
        """
        Получение данных из файла с данными
        Формат csv файла: адрес - логин, разделитель \";\"
        """
        # sometimes called from main prog
        try:
            with open("url_data.txt", "rt") as data_file:
                data = json.load(data_file)
            return data

        except FileNotFoundError:
            return {}

    def upgrade_data(self, addr, username):
        """Перезапись данных"""
        data = self.get_data()

        # data[addr] = username  # если в базе хранится не только адрес, но и порт клиента
        data[addr[0]] = username

        with open("url_data.txt", "wt") as data_file:
            json.dump(data, data_file)

        self.write_log("Data was upgraded\n")

    def get_user(self, client, addr):
        """Проверка на наличие пользователя по адресу"""
        data = self.get_data()

        # if addr in data.keys():  # если в базе хранится не только адрес, но и порт клиента
        if addr[0] in data.keys():
            self.write_log("User '{}' was got from history\n".format(data[addr[0]]))
            return data[addr[0]]

        else:
            return self.add_user(client, addr)

    def add_user(self, client, addr):
        """Добавление пользователя"""
        client.send("EYU".encode())
        username = client.recv(512).decode()

        self.upgrade_data(addr, username)

        print("-New user '{}' added for {}-".format(username, addr))
        self.write_log("User '{}' was added : {}\n".format(username, addr))
        client.send("User {} created!".format(username).encode())

        return username

    def listen(self):
        """Listen port"""

        def helper():
            client, addr = self.sock.accept()
            print('Connected to {}'.format(addr))
            self.write_log("Connected to {}\n".format(addr))

            username = self.get_user(client, addr)
            # client.settimeout(3)
            client.send("Hello, {}".format(username).encode())

            self.write_log("Finally starting with {} : {}\n".format(username, addr))
            threading.Thread(target=self.working, args=(username, client, addr,)).start()

        self.sock.listen(5)
        print("Awaiting any connection to port {}".format(self.port))

        while True:
            helper()

    def working(self, username, client, addr):
        """Basic work with client"""
        while True:
            file = client.recv(512).decode()

            if file == "to server quit":
                client.send("---disconnect---".encode())
                break

            self.write_log("User {} requested {} file\n".format(username, file))

            if file in type(self).files_dict.values():  # os.listdir(os.environ["HOMEPATH"]):
                self.write_log("Found requested {}\n".format(file))

                for send_file, name in type(self).files_dict.items():
                    if name == file:
                        client.send("Sending file".encode())
                        time.sleep(0.3)

                        with open(send_file, "rb") as f:
                            client.send(f.read())
                            self.write_log("File {} was sent to {} for {}\n".format(send_file, addr, username))

                        time.sleep(0.2)

                client.send("Sent all founded files".encode())

            else:
                self.write_log("Did not find {} in {}\n".format(file, os.environ["HOMEPATH"]))
                client.send("!!!404!!!".encode())
                self.write_log("File {} was not sent to {} for {}".format(file, addr, username))

        client.close()
        print("Disconnected from {}".format(addr))
        self.write_log(">>>Disconnected from {}\n".format(addr))


def write_server_log(string):
    """Server side log writing"""
    server_log_file.write("{} {}".format(time.strftime("%d.%m.%y %H:%M:%S", time.localtime(time.time())), string))
    server_log_file.flush()


if __name__ == "__main__":

    comm_list = ["pause()", "get_logs()", "clean_logs()", "clean_id()", "get_id()",
                 "get_server_logs()", "get_message_history()", "get_online_users()",
                 "get_offline_message()"]  # , "get_timeout()", "set_timeout()"]
    server_log_file = open("log_server.txt", "at")

    PORT = input("Enter the server's port (for example, 9090) > ")

    if PORT:
        # TheServer('', int(PORT)).listen()
        threading.Thread(target=TheServer, args=('', int(PORT)), daemon=True).start()
        server_log_file.write(">>>Starting server with {} port\n".format(PORT))
    else:
        # TheServer().listen()
        threading.Thread(target=TheServer, daemon=True).start()
        server_log_file.write("\n$$$$$ Starting server with 53310 port $$$$$\n\n")
        server_log_file.flush()

    time.sleep(0.5)
    while True:
        print("'shutdown' - to shutdown the server\n"
              "'clean_logs' - to clear logfile\n"
              "'clean_id' - to clear identification file\n"
              "'get_logs' - to show logfile\n"
              "'get_server_logs' - to show server side logfile\n"
              "'get_id' - to show identification file")
        comm = input(">>>") + "()"
        write_server_log("Got '{}' command\n".format(comm))

        if comm == "shutdown()":
            server_log_file.write("Shutting down the server\n")
            server_log_file.close()
            break

        if comm in comm_list:
            exec(comm)
        else:
            print("\n!Command incorrect!\n")

    print("The server was successfully turned off")
    input("press q\n")

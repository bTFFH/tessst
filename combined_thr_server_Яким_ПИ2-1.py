# -*- coding: utf-8 -*-
# КОМБИНИРОВАННЫЙ ЧАТ-ФАЙЛ-СЕРВЕР
"""
Служебные файлы: log.txt - хранит логи сервера
                log_server.txt - хранит логи серверной части работыс ервера
                data.txt - json formatted database
                message_history.txt - хранит историю сообщений
                offline_message.txt - хранит собщения и файлы пользователям,
                                которые были офлайн в момент отправки сообщения
Логи: CONNECT: address - подключение клиента
    DISCONNECT: address - отключение клиента
    START: username: address - начало работы с лиентом после авторизации
    USER_GET: username: address - получение пользоватебя из базы
    USER_ADD: username: address - добавление пользователя в базу
    ERROR: username: error description - ошибка с ее кратким описанием в виде строки
    GET: username: 'message'/file_name - входящее сообщение от пользователя
    SEND: 'message'/file_name: sender[: getter] - отправление сообщения/файла пользователю,
                                        getter не указан, если пользователь запросил файл
    OFFLINE: sender: getter: 'message'/file_name - добавление сообщения в offline_message.txt
    EXTRACT: 'data'/'offline_messages' - извлечение информации из data.txt/offline_message.txt
    UPGRADE: 'data'/'offline_messages' - перезапись (с целью обновления информации) data.txt/offline_message.txt
    TO_SERVER: 'message'/file_name: username - 'общение' пользователя с сервером"""
import socket
import json
import threading
import time
import os
from collections import OrderedDict


class TheServer(object):
    """
    Сервер
    Принимает хост (default = '') и порт (default = 53310)
    """
    flag = False  # флаг для приостановки работы сервера
    log_file = open("log.txt", "at")  # файл лога работы сервера
    message_hist_file = open("message_history.txt", "at")  # история сообщений. формат "*from* : *to* : *message*"
    current_users = {}  # словарь, хранящий текущих подключенных пользователей. формат {user:connection}
    files_dict = {}  # словарь, хранящий названия и пути ко всем файлам в каком-либо каталоге
    
    def __init__(self, host='', port=53310):
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
        """Refreshing list containing paths each 30 seconds"""
        type(self).files_dict = {i[0] + "\\" + file: file for i in os.walk(
            os.environ["HOMEDRIVE"] + os.environ["HOMEPATH"]) for file in i[2]}
        time.sleep(30)

    def write_log(self, string):
        """Запись лога"""
        # partially in thread
        type(self).log_file.write("{} > {}".format(
            time.strftime("%d/%b/%Y %H:%M:%S -%Z", time.localtime(time.time())), string)
        )
        type(self).log_file.flush()

    def write_mes_hist(self, string):
        """Запись истории сообщений"""
        # part of thread
        type(self).message_hist_file.write("{} > {}".format(
            time.strftime("%d/%b/%Y %H:%M:%S -%Z", time.localtime(time.time())), string)
        )
        type(self).message_hist_file.flush()

    @staticmethod
    def get_data():
        """
        Получение данных из файла с данными
        Формат csv файла: адрес - логин, разделитель \";\"
        """
        # sometimes called from main prog
        try:
            with open("data.txt", "rt") as data_file:
                data = json.load(data_file)
            return data

        except FileNotFoundError:
            return {}

    @staticmethod
    def get_offline_message():
        """Получение данных из файла с оффлайн сообщениями"""
        # sometimes called from main prog
        try:
            with open("offline_message.txt", "rt") as mess_file:
                offline_data = json.load(mess_file)
            return offline_data

        except FileNotFoundError:
            return {}

    def get_user(self, client, addr):
        """Проверка на наличие пользователя по адресу"""
        data = self.get_data()

        # if addr in data.keys():  # если в базе хранится не только адрес, но и порт клиента
        if addr[0] in data.keys():
            self.write_log("USER_GET: {}: {}\n".format(data[addr[0]], addr))
            return data[addr[0]]

        else:
            return self.add_user(client, addr)

    def upgrade_data(self, addr, username):
        """Перезапись данных"""
        data = self.get_data()

        # data[addr] = username  # если в базе хранится не только адрес, но и порт клиента
        data[addr[0]] = username

        with open("data.txt", "wt") as data_file:
            json.dump(data, data_file)

        self.write_log("UPGRADE: data\n")

    def upgrade_offline_message(self, data):
        """Перезапись офлайн сообщений"""
        with open("offline_message.txt", "wt") as mess_file:
            json.dump(data, mess_file)

        self.write_log("UPGRADE: offline_messages\n")

    def add_user(self, client, addr):
        """Добавление пользователя"""
        client.send("EYU".encode())
        username = client.recv(512).decode()

        self.upgrade_data(addr, username)

        print("-New user '{}' added for {}-".format(username, addr))
        self.write_log("USER_ADD: {}: {}\n".format(username, addr))
        client.send("User '{}' created!".format(username).encode())

        return username

    def offline_checker(self, getter, client):
        """Отправкуа сообщений пользователю, полученных в его отсутствие"""
        history = self.get_offline_message()
        self.write_log("EXTRACT: offline_messages\n")

        if getter in history.keys():
            client.send("\nYou have received some messages while you where offline\n"
                        "\t\tsincerely, server\n\n".encode())
            for message in history[getter]:
                if not message.split(" ")[0] == "FILE":
                    self.send_message(message.split(" ", 2)[1], getter, message + "\n", offline=True)

                else:
                    self.send_file(getter, client, message.split(" ")[1])
            history.pop(getter)
            self.upgrade_offline_message(history)

        else:
            self.write_log("ERROR: {}: no offline messages\n".format(getter))

    def listen(self):
        """Подключение клиентов и их инициализация"""
        # client = connection; addr = (IP, port)

        def helper():
            client, addr = self.sock.accept()
            print('Connected to {}'.format(addr))
            self.write_log("CONNECT: {}\n".format(addr))

            username = self.get_user(client, addr)
            # client.settimeout(3)
            client.send("Hello, {}!".format(username).encode())
            type(self).current_users[username] = client

            self.write_log("START: {}: {}\n".format(username, addr))
            threading.Thread(target=self.offline_checker(username, client)).start()
            threading.Thread(target=self.working, args=(username, client, addr,)).start()

        self.sock.listen(5)
        # print("{} {}".format(socket.gethostbyaddr(socket.gethostbyname(socket.gethostname())),
        # socket.getfqdn(socket.gethostname())))
        print("The server's IP is {}".format(socket.gethostbyname(socket.gethostname())))
        print('Awaiting any connection to port {}\n'.format(self.port))

        while True:
            if not type(self).flag:
                helper()
            else:
                time.sleep(10)

    def working(self, username, client, addr):
        """Работа с клиентами"""
        # part of thread
        # client = connection, addr = (IP, port)]
        # variable client may be replaced with type(self).current_users[username]
        while True:
            message = self.get_message(username, client)

            if message[0] == "TO":
                self.write_log("GET: {}: message\n".format(username))

                # обработка отключения от сервера
                if message[2] == "quit":
                    client.send("---disconnect---".encode())
                    self.write_log("DISCONNECT: {}\n".format(username))
                    break

                self.send_message(username, message[1], message[2])

            elif message[0] == "GET":
                self.send_file(username, client, message[1])

            elif message[0] == "SEND":
                self.send_file(username, client, message[1], message[2].split(" ")[1])

        client.close()

        print("Disconnected from {}".format(
            addr, type(self).current_users.pop(username, "double client error")
        ))

    def send_file(self, username, client, file, getter=""):
        """Отправление файла/файлов клиенту при наличии"""
        if file in type(self).files_dict.values():
            self.write_log("Found requested file '{}'\n".format(file))

            if not getter:
                for send_file, name in type(self).files_dict.items():
                    if name == file:
                        client.send("Sending file".encode())
                        time.sleep(0.2)

                        with open(send_file, "rb") as f:
                            client.send(f.read())
                            self.write_mes_hist("{} : {} : {}\n".format(username, username, file))
                            self.write_log("SEND: {}: {}\n".format(send_file, username))

                        time.sleep(0.2)

                client.send("Sent all founded files".encode())

            elif getter == "server":
                client.send("I am not the Person to send files!\n"
                            "\t\tbest wishes, server".encode())
                self.write_mes_hist("{} : {} : {}\n".format(username, getter.capitalize(), file))
                self.write_log("TO_SERVER: {}: {}'\n".format(file, username))

            elif getter in type(self).current_users.keys():
                    for send_file, name in type(self).files_dict.items():
                        if name == file:
                            type(self).current_users[getter].send("Sending file".encode())
                            time.sleep(0.2)

                            with open(send_file, "rb") as f:
                                type(self).current_users[getter].send(f.read())
                                self.write_mes_hist("{} : {} : {}\n".format(username, getter, file))
                                self.write_log("SEND: {}: {}: {}\n".format(
                                    send_file, username, getter))

                            time.sleep(0.2)

                    type(self).current_users[getter].send("Sent all founded files".encode())
                    client.send("I have sent '{}' to '{}'\n"
                                "\t\twith love, server".format(file, getter).encode())

            else:
                client.send("Sorry, cannot find '{}' online".format(getter).encode())
                threading.Thread(target=self.send_offline_file,
                                 args=(username, getter, file), daemon=True).start()
                self.write_log("ERROR: {}: '{}' not online\n".format(username, getter))

        else:
            self.write_log("ERROR: {}: 404 - '{}' not found\n".format(username, file))
            client.send("Error 404: File not found\n\t\tI'm so sorry, server".encode())

    def send_offline_file(self, sender, getter, file):
        """Отправление файла/файлов клиенту оффлайн"""
        if getter in self.get_data().values():
            offline_data = self.get_offline_message()
            self.write_log("EXTRACT: offline_messages\n")

            if getter in offline_data.keys():
                offline_data[getter].append("FILE {}".format(file))
            else:
                offline_data[getter] = ["FILE {}".format(file)]

            self.write_log("OFFLINE: {}: {}: {}'\n".format(sender, getter, file))
            self.upgrade_offline_message(offline_data)

            type(self).current_users[sender].send("Your file will be delivered as '{}' will come online\n"
                                                  "\t\thope to see him soon, server".format(getter).encode())

        else:
            type(self).current_users[sender].send("Cannot find {} in database, "
                                                  "your file will not be sent\n"
                                                  "\t\tI'm so sorry, server".format(getter).encode())
            self.write_log("ERROR: {}: '{}' not found\n".format(sender, getter))

    def get_message(self, username, client):
        """Получение и обработка собщения от клиента"""
        # part of thread
        # формат получаемого сообщения:
        #                   "TO *username* *message*"
        #                   "GET *file_name*"
        #                   "SEND *file_name* TO *username*
        data = client.recv(4096).decode().split(" ", 2)
        if data[0] == "TO":
            self.write_log("GET: {}: message\n".format(username))
        else:
            self.write_log("GET: {}: {}\n".format(username, data[1]))
        return data

    def send_message(self, sender, getter, message, offline=False):
        """Отправление сообщение клиенту"""
        # part of thread
        # формат отправляемого сообщеия "from *username* *message*"
        if not message:
            message = "*empty message here, be sure you don't see that*"

        if offline:
            type(self).current_users[getter].send(message.encode())
            self.write_mes_hist("{} : {} : {}\n".format(sender, getter, message.split(" ", 2)[2]))
            self.write_log("SEND: message: {}: {}\n".format(sender, getter))

        elif getter == "all_users":
            for user_conn in type(self).current_users.values():
                user_conn.send("from {} {}".format(sender, message).encode())

            type(self).current_users[sender].send("I have sent your message, {}!\n"
                                                  "\t\tserver".format(sender).encode())
            self.write_mes_hist("{} : {} : {}\n".format(sender, "all_users", message))
            self.write_log("SEND: message: {}: All_users\n".format(sender))

        elif getter == "server":
            type(self).current_users[sender].send("I am not the Person to send messages!\n"
                                                  "\t\tbest wishes, server".encode())
            self.write_mes_hist("{} : {} : {}\n".format(sender, getter.capitalize(), message))
            self.write_log("TO_SERVER: message: {}'\n".format(sender))

        elif getter in type(self).current_users.keys():
            type(self).current_users[getter].send("from {} {}".format(sender, message).encode())
            type(self).current_users[sender].send("I have sent your message, {}!\n"
                                                  "\t\twith love, server".format(sender).encode())
            self.write_mes_hist("{} : {} : {}\n".format(sender, getter, message))
            self.write_log("SEND: message: {}: {}\n".format(sender, getter))

        else:
            type(self).current_users[sender].send("Sorry, cannot find '{}' online".format(getter).encode())
            threading.Thread(target=self.send_offline_message, args=(sender, getter, message)).start()
            self.write_log("ERROR: {}: '{}' not online\n".format(sender, getter))

    def send_offline_message(self, sender, getter, message):
        """Отправление сообщения оффлайн пользователю"""
        # offline message pattern: "from *username* *message*"
        # part of thread
        message = "from {} {}".format(sender, message)

        if getter in self.get_data().values():
            offline_data = self.get_offline_message()
            self.write_log("EXTRACT: offline_messages\n")

            if getter in offline_data.keys():
                offline_data[getter].append(message)
            else:
                offline_data[getter] = [message]

            self.upgrade_offline_message(offline_data)

            type(self).current_users[sender].send("Your message will be delivered as '{}' will come online\n"
                                                  "\t\thope to see him soon, server".format(getter).encode())
            self.write_log("OFFLINE: {}: {}: message\n".format(sender, getter))

        else:
            type(self).current_users[sender].send("Cannot find {} in database, "
                                                  "your message will be deleted\n"
                                                  "\t\tI'm so sorry, server".format(getter).encode())
            self.write_log("ERROR: {}: '{}' not found\n".format(sender, getter))

    @classmethod
    def pause(cls):
        """
        Pause the server
        Use it outside the class
        """
        # always from main prog
        cls.flag = True

    @classmethod
    def unpause(cls):
        """
        Resume the server
        Use it outside the class
        """
        # always from main prog
        cls.flag = False

    @classmethod
    def drop_log(cls):
        """
        Clean logfile
        Use it outside the class
        """
        # always from main prog
        cls.log_file.close()
        os.remove(cls.log_file.name)
        cls.log_file = open(cls.log_file.name, "at")

    # @classmethod
    # def current_users_online(cls):
    #     """Returning current online users"""
    #     return [i for i in cls.current_users.keys()]


def write_server_log(string):
    """Запись серверной части лога"""
    server_log_file.write("{} > {}".format(
        time.strftime("%d/%b/%Y %H:%M:%S -%Z", time.localtime(time.time())), string)
    )
    server_log_file.flush()


def get_logs():
    """Logs printing getter"""
    with open("log.txt", "rt") as log_file:
        log_data = log_file.readlines()

    write_server_log("Printing logs\n")

    if log_data:
        print("\n-----------------")
        for i in log_data:
            print(i, end="")
        print("-----------------\n")
        log_data.clear()

    else:
        print("\nLog data was refreshed and nobody connected yet\n")


def get_server_logs():
    """Printing server side server work"""
    with open("log_server.txt", "rt") as log_file:
        log_data = log_file.readlines()

    write_server_log("Printing server side logs\n")

    print("\n-----------------")
    for i in log_data:
        print(i, end="")
    print("-----------------\n")
    log_data.clear()


def pause():
    """Pauses the server accepting any new connection"""
    if TheServer.flag:
        TheServer.unpause()
        print("\n---Server was resumed---\n")
        write_server_log("---Resume the server\n")

    else:
        TheServer.pause()
        print("\n---Server was paused---\n")
        write_server_log("---Pause the server\n")


def clean_logs():
    """Logs cleaning cleaner"""
    TheServer.drop_log()
    print("\nLogfile was refreshed\n")
    write_server_log("Refreshing log\n")


def clean_id():
    """Identification file cleaner"""
    try:
        os.remove("data.txt")
        print("\nDatabase was refreshed\n")

    except FileNotFoundError:
        print("\nFile already removed\n")
    write_server_log("Refreshing data\n")


def get_id():
    """Identification file getter"""
    data = TheServer.get_data()

    if data:
        print("\nCurrent database: ", end="")
        print(data, "\n")
    else:
        print("\nWe do not have any user database yet\n")

    write_server_log("Printing identification file\n")


def get_message_history():
    """Printing messages history"""
    with open("message_history.txt", "rt") as message_file:
        message_data = message_file.readlines()

    write_server_log("Printing messages history\n")

    if message_data:
        print("\n-----------------")
        for i in message_data:
            print(i)
        print("-----------------\n")
        message_data.clear()

    else:
        print("\nWe do not have any messages in offline\n")


def get_offline_message():
    """Printing offline messages to send"""
    offline_message_data = TheServer.get_offline_message()

    write_server_log("Printing offline messages to send\n")

    if offline_message_data:
        print("\n-----------------")
        for i in offline_message_data:
            print("to {} {}".format(i, offline_message_data[i]))
        print("-----------------\n")
        offline_message_data.clear()

    else:
        print("\nWe do not have any offline messages to send\n")


def get_online_users():
    """Printing current online users"""
    write_server_log("Printing users online\n")
    users = [i for i in TheServer.current_users.keys()]
    if users:
        print("\nCurrent online users: {}\n".format(users))
    else:
        print("\nNobody online \\('),(')/\n")


if __name__ == "__main__":

    # each server side command must be stored in comm_dict as '*command_name*()'
    comm_dict = OrderedDict({"pause()": "to pause the server", "clean_logs()": "to clear logfile",
                             "clean_id()": "to clear identification file", "get_logs()": "to show logfile",
                             "get_server_logs()": "to show server side logfile",
                             "get_id()": "to show identification file", "get_online_users()": "to show users online",
                             "get_message_history()": "to show messages history",
                             "get_offline_message()": "to show offline messages to send"})
    server_log_file = open("test_log_server.txt", "at")

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
        print("'shutdown' - to shutdown the server")
        for cd in comm_dict.keys():
            print("'{}' - {}".format(cd.rstrip("()"), comm_dict[cd]))

        comm = input(">>>") + "()"
        write_server_log("Got '{}' command\n".format(comm))

        if comm == "shutdown()":
            server_log_file.write("{} > Shutting down the server\n".format(
                time.strftime("%d/%b/%Y %H:%M:%S -%Z", time.localtime(time.time()))
            ))
            server_log_file.close()
            break

        if comm in comm_dict.keys():
            exec(comm)
        else:
            print("\n!Command incorrect!\n")

    print("The server was successfully turned off")
    input("press q\n")

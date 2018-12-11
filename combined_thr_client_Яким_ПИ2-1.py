# -*- coding: utf-8 -*-
import socket
import threading
from re import fullmatch
from time import sleep


class TheClient(object):
    """
    Клиент
    Принимает адрес (default = 127.0.0.1) и порт (default = 53310) сервера
    """

    def __init__(self, host='127.0.0.1', port=53310):
        self.host = host
        self.port = port
        self.sock = socket.socket()

    @staticmethod
    def info():
        """Немного инфы о формате сообщений и тп"""
        info = ["Type 'TO server quit' to disconnect from server.",
                "Messages to users should be like this pattern: \"TO *username* *message*\"\n"
                "\t\twhere *username* - name of any user online, server (only to disconnect) "
                "or \"all_users\" to send message to all users online",
                "You will receive messages from user like this pattern: \"from *user_name* *message*\".",
                "Messages to download files should be like this pattern: \"GET *file_name*.*format*\".",
                "You will receive files in binary mode and they will be printed immediately (sorry).",
                "Messages to send files to other user should be like this pattern: "
                "\"SEND *file_name* TO *user_name*\"",
                "All other users will also receive files in binary mode and they will be "
                "printed immediately (sorry).",
                "Any message you send can be just one-line message.",
                "You have 0.7 seconds message sending timeout."]

        for ind, string in enumerate(info):
            print("{}. {}".format(ind + 1, string))

    def connect(self):
        """Коннект к клиенту"""
        try:
            self.sock.connect((self.host, self.port))
        except ConnectionRefusedError:
            print("The server is offline or you do not have connection to the server.\n",
                  "Please, check your connection or connect later.")
            input("Press \"Enter\" to exit")
        else:
            print("Connected to {}".format(self.host))
            self.start()
            input("Press \"Enter\" to exit")

    def get_file(self):
        """Получение файлов"""
        while True:
            data = self.sock.recv(65536)

            if data == "Sending file".encode():
                print("\nAnd another file here\n")
                continue

            if data == "Sent all founded files".encode():
                print("\nGot all founded files\n\t\twith love, server\n>>>", end="")
                break

            print(data)

    def get_small_data(self):
        """Получение небольшого объема данных"""
        return self.sock.recv(512).decode()

    def get_data(self):
        """Получение данных"""
        # getting thread
        while True:
            data = self.sock.recv(4096).decode()

            if data == "---disconnect---":
                self.sock.close()
                print("Wish to see you late\n\t\tyour lovely server\nDisconnected")
                break

            if data == "Sending file":
                print("Receiving file\n")
                self.get_file()
                continue

            if not data:
                print("The server was turned off")
                break

            print(data)

    def get_username(self):
        """Ввод и обработка имени пользователя"""
        username = input("\nThat's it!\n"
                         "> Your username must be from 3 to 10 characters length\n"
                         "> And should contain only letters and numbers\n"
                         "> Enter your username >>> ")

        if not 2 < len(username) <= 10:
            print("Your username is too short!\nTry again..")
            return self.get_username()

        elif not username.isalnum():
            print("You have entered an invalid character\nTry again..")
            return self.get_username()

        else:
            print("\nWell done!")
            return username

    def small_send(self, data):
        """Отправка небольшого объема данных"""
        self.sock.send(data.encode())
        return "'{}' was sent to {}".format(data, self.host)

    def send_data(self):
        """Отправка данных"""
        # sending thread
        while True:
            sleep(0.7)
            data = input(">>>")
            if fullmatch("TO (.){3,10} (.)*", data):
                self.sock.send(data.encode())

            elif fullmatch("GET (.)+\.(.)+", data):
                self.sock.send(data.encode())

            elif fullmatch("SEND (.)+\.(.)+ TO (.){3,10}", data):
                if not "all_users" == data.split(" ")[3]:
                    self.sock.send(data.encode())

                else:
                    print("Due to preventing spam you are not allowed to"
                          "send any files to all users together\n\t\tgood luck, server")

            else:
                print("Wrong format, it won't be send")

    def working(self):
        """
        Работа клиента
        В данном методе осуществляется манипуляция потоками
        """
        self.info()
        getter = threading.Thread(target=self.get_data, daemon=True)
        getter.start()
        threading.Thread(target=self.send_data, daemon=True).start()
        getter.join()

    def start(self):
        """Инициализация клиента и начало работы"""
        data = self.get_small_data()
        if data == "EYU":
            username = self.get_username()
            self.small_send(username)
            print("\n{}".format(self.get_small_data()))
            print("\n{}\n".format(self.get_small_data()))
        else:
            print("\n{}\n".format(data))

        self.working()


if __name__ == "__main__":
    HOST = input("Enter the server's IP > ")
    if HOST:
        PORT = int(input("Enter the server's port > "))
        TheClient(HOST, PORT).connect()
    else:
        TheClient().connect()

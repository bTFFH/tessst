# -*- coding: utf-8 -*-
import socket
import threading
from time import sleep
from re import fullmatch


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
        print("\n1. Type 'to server quit' to disconnect from server.\n"
              "2. All messages should be like this pattern: \"to *username* *message*\"\n"
              "\t\twhere *username* - name of any user online, server (only to disconnect) "
              "or \"all_users\" to send message to all users online\n"
              "3. You will receive messages from user like this pattern: \"from *user_name* *message*\"\n"
              "4. Any message you send can be just one-line message\n"
              "5. You have 0.7 seconds message sending limit\n")

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

    def get_small_data(self):
        """Получение небольшого объема данных"""
        return self.sock.recv(512).decode()

    def get_file(self):
        """Получение файлов"""
        while True:
            data = self.sock.recv(65536)

            if data == "Sending file".encode():
                print("\nAnd another file here\n")
                continue

            if data == "Sent all founded files".encode():
                print("\nGot all founded files\n>>>", end="")
                break

            print(data)

    def get_data(self):
        """Получение данных"""
        # getting thread
        while True:
            data = self.sock.recv(4096).decode()

            if data == "---disconnect---":
                self.sock.close()
                print("Disconnected")
                break

            if data == "Sending file":
                print("Receiving file")
                self.get_file()
                continue

            if data == "!!!404!!!":
                print("Error 404: File not found")
                continue

            if not data:
                print("The server was turned off")
                break

            print(data)

    def get_username(self):
        """Ввод и обработка имени пользователя"""
        username = input("\nThat's it!\n"
                         "Your username must be from 3 to 10 characters length\n"
                         "And should contain only letters and numbers\n"
                         "Enter your username > ")

        if not 2 < len(username) <= 10:
            print("Your username is too short!\nTry again..")
            return self.get_username()

        elif not username.isalnum():
            print("You have entered an invalid character\nTry again..")
            return self.get_username()

        else:
            print("Well done!")
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
            if fullmatch("to (.){3,10} (.)*", data):
                self.sock.send(data.encode())

            elif fullmatch("GET (.)+\.(.)+", data):
                self.sock.send(data.split(" ")[1].encode())

            else:
                print("Wrong format, it won't be send")

    def working(self):
        """
        Работа клиента
        В данном методе осуществляется манипуляция потоками
        """
        # self.info()
        # add GET request
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
            print(self.get_small_data())
        else:
            print(data)

        self.working()


if __name__ == "__main__":
    HOST = input("Enter the server's IP > ")
    if HOST:
        PORT = int(input("Enter the server's port > "))
        TheClient(HOST, PORT).connect()
    else:
        TheClient().connect()

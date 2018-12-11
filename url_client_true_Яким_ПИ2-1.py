# -*- coding: utf-8 -*-
import urllib3
import threading
import time
from certifi import where

and mistake
over and over and over again

def get_url():
    """Получение URL от пользователя"""
    print("You need to enter ONLY domain name")
    url = r"http://" + input("Enter your http url or type 'S' for entering https url ") + r"/"

    if url == r"http://S/":
        url = r"https://" + input("Enter your https url ") + r"/"
        manager = urllib3.PoolManager(num_pools=1, cert_reqs='CERT_REQUIRED', ca_certs=where())
    else:
        manager = urllib3.PoolManager(num_pools=1)
    
    return url, manager


def get_connection(url, manager):
    """Запрос по URL"""
    try:
        req = manager.request("GET", url)
    
    except urllib3.exceptions.SSLError:
        print("Got SSL error")
        exit()
    
    except urllib3.exceptions.MaxRetryError:
        # default retries = 3
        print("Unable to connect to the server after 3 retries\n"
              "Are you sure in correct url?")
        return start()
    
    except urllib3.exceptions.BodyNotHttplibCompatible:
        print("You have entered url address in a wrong way\n"
              "Try again")
        return start()
    
    else:
        print("Got answer: ", req.headers)
        return req


def downloading(req, file_name):
    """Загрузка страницы"""
    time.sleep(5)
    # в случае с сайтом fa.ru метод decode() вызовет ошибку
    data = req.data  # .decode()
    # print(data)
    # with open(file_name, "wt") as file:
    with open(file_name, "wb") as file:
        file.write(data)
    print("Completed!")


def start():
    """
    Управляющий метод
    Существует для избежания ошибок при некорректном вводе URL
    """
    url, manager = get_url()
    return get_connection(url, manager)


if __name__ == "__main__":
    urllib3.disable_warnings()  # игнорирование бесполезных предупреждений
    req = start()
    download = input("Wanna download? (y/n) ")

    if download == "y":
        file_name = input("Enter file name ") + ".html"
        print("You have only 5 secs to cancel downloading")
        threading.Thread(target=downloading, args=(req, file_name), daemon=True).start()

    input("press q\n")

import time
import re
import json
import os

print(time.strftime("%d.%m.%y %H:%M:%S", time.gmtime(time.time())))
print(time.strftime("%d.%m.%y %H:%M:%S", time.localtime(time.time())))
print(time.strftime("%d/%b/%Y %H:%M:%S -%Z", time.localtime(time.time())))
print(time.asctime())

print("aa bb cc dd ee ff".split(" ", 2))

with open("combined_thr_server_Яким_ПИ2-1.py", "rt", encoding="utf-8") as file:
    f = open("xt.txt", "wt")
    lines = file.readlines()
    print(lines)
    for ind, line in enumerate(lines):
        if re.match("[ ]*type\(self\)\.log_file[0-9a-zA-Z.]*", line) or re.match("[ ]*self\.write_log[0-9a-zA-Z.()]*", line):
            print(re.sub("[ ]{4}", "", line))
            f.write(str(ind + 1) + " > " + re.sub("[ ]{4}", "", line) + "\n")
    f.close()


# print("enter stop to stop")
#
# while True:
#     data = input(">>>")
#     if re.fullmatch("to (.){3,10} (.)*", data):
#         print(True)
#     else:
#         print(False)
#     if data == "stop":
#         break

# data = {"server":["one", "two"], "mee":["127.0.0.1"]}
#
# with open("test_data.txt", "wt") as data_file:
#     json.dump(data, data_file)
#
# try:
#     with open("test_data.txt", "rt") as data_file:
#         data = json.load(data_file)
#
#     print(data)
#     print(data["server"])
#     # data["server"] = data["server"].append("three")
#     data["server"].append("three")
#
#     with open("test_data.txt", "wt") as data_file:
#         json.dump(data, data_file)
#
#     with open("test_data.txt", "rt") as data_file:
#         data = json.load(data_file)
#
#     print(data)
#
# except FileNotFoundError:
#     print({})

# for key, val in os.environ.items():
#     print("{} --- {}".format(key, val))
#
# print("\n^^^___^^^\n")
#
# file_list = []
# file_set = set()
#
# for i in os.walk(os.environ["HOMEDRIVE"] + os.environ["HOMEPATH"]):
#     # print(i[2])
#     for file in i[2]:
#         file_list.append(file)
#         file_set.add(file)
#
# print(len(file_list))
# print(len(file_set))
#
# for dr, drs, fls in os.walk(os.environ["HOMEDRIVE"] + os.environ["HOMEPATH"], topdown=True):
#     print(f"{dr} --- {drs} ___ {fls}")

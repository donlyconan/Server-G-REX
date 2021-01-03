import socket

from texttable import Texttable

CONFIG = "D:\Resource-LTM\MyWorld\myworld_client\module\.config"

def show_json_table(header, data, att, mul=False):
    tb = Texttable()
    list = getJSONArray(data, att)
    tb.add_rows(list)
    tb.header(header)
    tb.set_max_width(220)
    print(tb.draw())


def getJSONArray(data, att):
    list = [[x for x in range(0, len(att))]]
    for x in data:
        row = []
        for m in att:
            row.append(x[m])
        list.append(row)
    return list


def show_table(header, data, mutiline=False):
    tb = Texttable()
    if mutiline:
        tb.add_rows(data)
    else:
        tb.add_row(data)
    tb.header(header)
    tb.set_max_width(150)
    print(tb.draw())


def show_control():
    list, dict, tb = [], {}, []
    file = open(CONFIG, "rb")
    for x in file.readlines():
        x = x.decode('utf-8')
        if '=' in x:
            x = x.replace("=", "/")
            lines = x.split("/")
            list.append(lines)

            if len(lines) == 3 and "None" not in lines[2]:
                dict[lines[0].rstrip(" ")] = lines[1].rstrip(" ")
    i = 0
    while i < len(list) - 1:
        tb.append(list[i] + ["\t"] + list[i + 1])
        i += 2
    sorted(tb, key=lambda k: k[0][0])
    file.close()
    show_table(["Mã lệnh", "Số hiệu", "Ghi chú", "\t", "Mã lệnh", "Số hiệu", "Ghi chú"], tb, True)
    return dict


def show_words(header, words):
    tb = Texttable()
    tb.header(header)
    tb.add_row(words)
    tb.set_max_width(1000)
    print(tb.draw())



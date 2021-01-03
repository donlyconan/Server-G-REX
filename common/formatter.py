import base64
import json
import os
from collections import namedtuple

from common.build import *

Lenght_Header = 10
Lenght_Footer = 10

FORMAT_VIDEO = 1
FORMAT_AUDIO = 2

UTF_16_LE = "utf-16-le"
Partition = '<!xml>'


def convert_array_tojson(atts, arrays):
    if len(arrays) == 0 or len(arrays[0]) > len(atts):
        raise Exception("Data None!")
    js = [{atts[i]: str(x[i]) for i in range(len(atts))} for x in arrays]
    return js


def create_data_transfer(header=PRINT_SCREEN, type=TYPE_STRING, data='', end=0):
    fm = DataTransfer()
    try:
        fm.header = int(header)
        fm.type = type
        fm.data = data
        fm.end = end
        return fm
    except Exception as e:
        raise Exception("Lỗi create format! {}".format(e))


# Kieu format header/type/data/endarray
def get_data_transfer_from_str(str):
    data = DataTransfer()
    try:
        str = str.split(Partition)
        data.header = int(str[0])
        data.type = int(str[1])
        data.data = str[2]
        str[3].rstrip('\x00')
        data.end = int(str[3])
    except Exception as e:
        raise Exception('[error]: Lỗi format!')
    return data


def get_data_transfer(bytes, utf='utf8'):
    data = DataTransfer()
    try:
        str = bytes.decode(utf)
        str = str.split(Partition)
        data.header = int(str[0])
        data.type = int(str[1])
        data.data = str[2]
        data.end = int(str[3].rstrip('\x00'))
    except Exception as e:
        raise Exception('[error]: Lỗi format! {}'.format(e))
    return data


# dinh dang chu yeu utf-8
# moi phan cach nhau boi chuoi ky tu regex
# ky tu ngan cach de phan chia cac phan byte
# uu diem
# chua duoc nhieu thong tin
# do tuy chinh du lieu cao, linh hoat
# thong tin truyen di day du chinh xac(vi 1 goi tin thieu du lieu se loi)
class DataTransfer:
    def __init__(self):
        # Ma lenh tuong ung yeu cau nguoi dung
        self.header = PRINT_SCREEN

        # kieu du lieu truyen di
        self.type = TYPE_STRING

        # du lieu duoc truyen di
        self.data = ""

        # danh dau phan du lieu
        self.end = 0

    # lay data theo dinh dang du lieu
    def get_data(self):
        if self.type == TYPE_JSON:
            return json.loads(self.data)
        if self.type == TYPE_STRING:
            return self.data
        if self.type == TYPE_INT:
            return int(self.data)
        if self.type == TYPE_FLOAT:
            return float(self.data)
        if self.type == TYPE_BINARY_ENCODE64:
            return base64.b64decode(self.data)

    # lay data theo dinh dang object (duy nhat voi Json)
    def get_object(self):
        if self.type == TYPE_JSON:
            return json.loads(self.data, object_hook=lambda d: namedtuple('Object', d.keys())(*d.values()))

    def str(self):
        return str(self.header) + Partition + str(self.type) + Partition + self.data + Partition + str(self.end)

    def tobytes(self, utf='utf-8'):
        return self.str().encode(utf)


def format_size(path):
    size = os.path.getsize(path)
    units, i = ['Byte', 'KB', 'MB', 'GB'], 0
    while size > 1024:
        size /= 1024
        i += 1
    return str(round(size, 2)) + ' ' + units[i]


"""___________________________________________Format Quick Data____________________________________________"""


# Tao bytes header
def create_headerbytes(x, lenght=10):
    x = str(x).encode()
    x += b'\00' * (lenght - len(x))
    return x


# lay byte header
def get_headerbytes(x):
    x = x.rstrip(b"\00")
    x = x.decode()
    return int(x)


def get_body(bytes_root):
    data = bytes_root[Lenght_Header + Lenght_Footer:]
    return data


# Dinh dang Utf-16-le
# su dung nhanh cho van chuyen file bang udp
def get_quick_data(bytes):
    bytes_header = bytes[:Lenght_Header]
    bytes_footer = bytes[Lenght_Header:(Lenght_Header + Lenght_Footer)]
    bytes_body = bytes[Lenght_Header + Lenght_Footer:]

    header = get_headerbytes(bytes_header)
    footer = get_headerbytes(bytes_footer)
    body = bytes_body
    return QuickData(header, body, footer)


def create_quick_data(header, body, footer=FORMAT_AUDIO):
    return QuickData(header, body, footer)


# n byte dau danh cho header
# n byte cuoi danh cho footer
# so byte nam trong khoang [n:-n] la body phan du lieu
# uu diem:
# phan cach du lieu se nhan hon
# dong bo hoa du lieu
class QuickData:

    def __init__(self, header, body, footer):
        # phan dau du lieu ma lenh hanh dong
        self.header = header;

        # du lieu duoc truyen di
        self.body = body

        # danh dau kieu du lieu hoac ho tro muc dich cua du lieu
        self.footer = footer

    def tobytes(self, utf=UTF_16_LE):
        bytes_header = create_headerbytes(self.header)
        bytes_footer = create_headerbytes(self.footer)
        return bytes_header + bytes_footer + self.body

    def __repr__(self):
        return "{header=%s, body=%s, footer=%s}" % (self.header, self.body, self.footer)

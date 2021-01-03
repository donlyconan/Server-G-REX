
EDE = None
END_CONNECT = 10
SHOW_MY_STORANGE = 97

# GET
GET_PERSONAL_FILE = 98
UPLOAD_FILE = 99
GET_FILENAME = 100
DOWNLOAD_FILE = 101
GET_DIEM_SV = 102
GET_LOGIN = 103
GET_CLASS_NO = 104
GET_SEARCH = 105
GET_SOLUONG_SV = 106

# POST
POST_LOGIN = 110
POST_INSERT_SINHVIEN = 112

# PUT
PUT_UPDATE_SINHVIEN = 113
PUT_PASSWORD = 120
PUT_DIEM = 121

GET_CURRENT_WEATHER = 122
GET_USERINFO = 123
UPDATE_USER = 124
SEARCH_HISTORY = 125


# Room
CHAT_SERVICE = range(200,250)
OPEN_CHAT = 200
ACT_SEND = 201
ACT_RECV = 202

EXIT_ROOM = 203
BREAK_ROOM = 204
RM_STT_START = 205
RM_STT_RUNNING = 206
RM_STT_FINISH = 207
RM_STT_RESULT = 215

RM_ACT_REGISTER = 208
RM_ACT_DISCONNECT = 209

GET_LIST_FRIEND = 210
GET_LIST_MESSAGE = 211
SAW_MESSAGE = 212
FRIEND_ONLINE = 213

# Màn hình
PRINT_SCREEN = 800
CLEAR_SCREEN = 500
NOT_FOUND = 400
SHOW_CONTROL = 0

# Kieu du lieu
TYPE_STRING = 1
TYPE_INT = 2
TYPE_FLOAT = 3
TYPE_DOUBLE = 4
TYPE_JSON = 5
TYPE_BINARY_ENCODE64 = 6

# end
SIZE_KB = 1024
SIZE_MB = SIZE_KB ** 2
SIZE_GB = SIZE_MB ** 2

TEST_CONNECTION = 9999

MAX_CLIENT = 100
HOST = 'localhost'
TCP_PORT = 9050
UDP_PORT = 4040
TCP_BUFFER_SIZE = 4 * SIZE_KB
UDP_BUFFER_SIZE = 5 * SIZE_KB

# address
UDPSERVER_ADDRESS = ('localhost', UDP_PORT)


def recvbytes(socket):
    tmp = ''.encode('utf-8')
    data = None
    while not data:
        d = socket.recv(TCP_BUFFER_SIZE)
        if not d: raise ConnectionError("Lỗi nhận dữ liệu!")
        if d[-1:] == b'0':
            data = tmp + d
        else:
            tmp += d
    return data


def sendbytes(socket, data):
    data += b'0'
    socket.sendall(data)


# def printf(message):
    # date_time = now.strftime("%d/%m/%Y - %H:%M:%S")
    # print(date_time + ': ' + str(message))


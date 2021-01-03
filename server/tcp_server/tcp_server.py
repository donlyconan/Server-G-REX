import socket
import threading
from queue import Queue, Empty
import select
import server.tcp_server.service as hd
from common import formatter as fm
from common.build import *
from common.manager import Manager
import selectors


selector = selectors.DefaultSelector()
manager = Manager({},{})
demap_cmd = {}  # chuỗi lệnh
selector = selectors.DefaultSelector()


# dam nhan chuc nang doc va xu ly du lieu
def listen_read(key, mask):
    sk = key.fileobj
    recv = recvbytes(sk)

    if recv:
        data = fm.get_data_transfer(recv)
        request_response('Request', sk , data.header, data.type, len(recv))

        if data.header in CHAT_SERVICE:
            hdata = hd.chat_service(key)
        else:
            hdata = hd.task_service(key)
        # printf("handle data = {}".format(hdata))
        if hdata:
            # day lu lieu vao queue va them vao danh sach bo ghi
            queue = key.data
            queue[sk].put_nowait(hdata)
            # them vao bo ghi
            selector.modify(sk, selectors.EVENT_WRITE, queue)
    else:
        listen_close(key, mask, 'readable')


# dam nhan chuc nang ghi du lieu
def listen_write(key, mask):
    sk = key.fileobj
    queue = key.data

    try:
        data = queue[sk].get_nowait()
    except Empty as e:
        printf("TCP-error: {}".format(e))
    else:
        arrdata = data.tobytes()
        sendbytes(sk, arrdata)
        request_response('Response', sk, data.header, data.type, len(arrdata))



# dam nhan chuc nang dong ket noi
def listen_close(sk, inp, out, queue, lis='_x_'):
    # xoa khoi bo doc
    inp.remove(sk)
    # xoa khoi bo ghi
    if sk in out:
        out.remove(sk)
    # xoa hang cho du lieu
    del queue[sk]
    manager.clear_socket(sk)
    printf(f"Close socket {sk.getsockname()} \t :\t from {lis}")
    sk.close()


# dam nhan chuc nang lang nghe su kien
def listen_accept(key, mask):
    sk = key.fileobj
    con, addr = sk.accept()

    printf(f"Chấp nhận kết nối remote: {addr}, total address: {len(selector.get_map().keys())}")

    con.setblocking(False)
    selector.register(con, selectors.EVENT_READ, Queue())



def create_ServerTcp(maxclient=1000):
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.bind((HOST, TCP_PORT))
    tcp_server.listen(maxclient)
    tcp_server.setblocking(False)
    return tcp_server


def request_response(action, sk, header, type, len):
    try:
         user = manager.get_user_id(sk)
         if not user: user = "anonymouse"
         message = f'{action}: Username: {user} > Header: {demap_cmd[header]} > Datatype: {demap_cmd[type]} > Len: {len}'
         printf(message)
    except:
        pass


def read_config(path="D:\Resource-LTM\MyWorld\common\.config"):
    map = {}
    file = open(path, mode='rb')
    for line in file.readlines():
        line = line.decode('utf-8')
        if '=' in line and 'EDE' not in line:
            line = line.replace('=', '/')
            lines = line.split('/')
            if 'range' not in lines[1]:
                map[int(lines[1])] = lines[0]
    file.close()
    return map


# bo select
def server_running():
    # Tao server
    tcp_server = create_ServerTcp()

    selector.register(tcp_server, selectors.EVENT_READ, None)
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    selector.register(tcp_server, selectors.EVENT_READ, listen_accept)

    # thong so ky thuat
    printf(f"Hostname: {hostname}")
    printf(f"IP: {ip}")
    printf('Run Server Non blocking.')

    demap_cmd = read_config()

    while True:
        # Bộ selector timeout = 10s
        events = selector.select()

        for key, mask in events:
            try:
                # Bộ đọc
                if key.fileobj is tcp_server:
                    # lang nghe ket noi tu server
                    listen_accept(key, mask)

                elif mask == selectors.EVENT_READ:
                    # lang nghe su kien tu client
                    listen_read(key, mask)

                elif mask == selectors.EVENT_WRITE:
                    listen_write(key, mask)

                elif mask == ~selectors.EVENT_READ:
                    listen_close(key, mask)



            except Exception as e:
                listen_close(key, mask)
                printf('TCP-Lỗi: {}'.format(e))


def t_running():
    threading.Thread(target=server_running()).start()

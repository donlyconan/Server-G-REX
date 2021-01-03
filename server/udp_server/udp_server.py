import socket
import threading

from common import formatter as fm
from common.build import *

channels = {1111: set()}
running = False


def create_ServerUdp():
    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server.bind((HOST, UDP_PORT))
    return udp_server


def sendto(server, id, myaddr, data):
    if len(channels[id]) <= 1:
        del channels[id]
        printf(f"[UDP] Remove channel {id}")

    elif id in channels:
        for addr in channels[id]:
            try:
                if addr == myaddr: continue
                server.sendto(data, addr)
            except:
                channels[id].remove(addr)


def check_room(idroom):
    global channels
    if idroom not in channels:
        channels[idroom] = set()
    return channels[idroom]


# bo select
def listen():
    # Tao server
    udp_server = create_ServerUdp()

    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    # thong so ky thuat
    printf(f"Hostname: {hostname}")
    printf(f"IP: {ip}")
    printf(f'Server Address: {UDPSERVER_ADDRESS}')
    printf('Run UDP Server.')

    while running:
        try:
            # nhan du lieu
            data, addr = udp_server.recvfrom(UDP_BUFFER_SIZE)

            # lay du lieu
            bf = fm.get_quick_data(data)

            # lay ma phong
            id = bf.footer

            # dang ky dich vu goi thoai
            # moi thanh vien khi tham gia phong chat deu phai dang ky dich vu goi thoai
            if bf.header == RM_ACT_REGISTER:
                result = 'tốt'.encode('utf-8')
                udp_server.sendto(result, addr)

                # neu phong chat chua ton tai thi tao moi con neu da ton tai thi them vao
                check_room(id)
                channels[id].add(addr)

                printf(f'UDP Request[Register]: số phòng: {id} > tổng thành viên: {len(channels[id])} > thành viên mới: {addr}')

            # huy dang ky voi phong chat
            elif bf.header == RM_ACT_DISCONNECT and id in channels:
                channels[id].remove(addr)
                printf( f'UDP Request[Disconnect]: số phòng: {id} > tổng thành viên: {len(channels[id])} > Xoá thành viên: {addr}')

            elif bf.header == RM_STT_RUNNING:
                sendto(udp_server, id, addr, data)

        except Exception as e:
            printf('UDP-Lỗi: {}'.format(e))


def t_running():
    global running
    running = True
    threading.Thread(target=listen).start()


def stop():
    global running
    running = False


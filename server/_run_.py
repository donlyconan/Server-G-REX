import time
from server.tcp_server import tcp_server
from server.udp_server import udp_server

# ngay khoi tao 03/05/2020
# tao thread run


if __name__ == '__main__':
    # chay udp server
    udp_server.t_running()

    time.sleep(0.1)

    # chay tcp_server
    tcp_server.t_running()

    time.sleep(0.1)

    print('─' * 200)

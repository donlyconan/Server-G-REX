import json
import common.mysqldb as db
from common import formatter as fm
from common.build import *
from server.tcp_server import weather

# xu ly phong chat
def chat_service(data, sk, inp, out, queue, manager):
    printf(f"Data: {data.str()}")
    printf(f"Manager: {manager}")

    """Truyen 1 header, data co chua: sender_id, receiver_id, message"""
    if data.header == ACT_SEND:
        recv = data.get_object()
        fr_sk = manager.get_socket(int(recv.receiver_id))
        if fr_sk:
            data.header = ACT_RECV
            queue[fr_sk].put_nowait(data)
            if fr_sk not in out: out.add(fr_sk)
        db.insert_message(data.get_data())
        # Giu thanh cong
        return fm.create_data_transfer(PRINT_SCREEN, TYPE_JSON, json.dumps({"result": 1}))

    """Lay danh sach tin nhan va ban be"""
    if data.header == GET_LIST_FRIEND:
        data.data = db.get_list_friend(data.data)
        return data


    """lay danh sach tin nhan tu 1 nguoi ban"""
    if data.header == GET_LIST_MESSAGE:
        recv = data.get_object()
        data.data = db.get_list_message(recv.myid, recv.friend_id, recv.from_, recv.to)
        return data


    if data.header == SAW_MESSAGE:
        recv = data.get_object()
        db.saw_message(recv.myid, recv.friend_id)
        return None

    if data.header == RM_STT_START:
        recv = data.get_object()
        fr_sk = manager.get_socket(int(recv.friend_id))
        if fr_sk:
            queue[fr_sk].put_nowait(data)
            out.add(fr_sk)
            return fm.create_data_transfer(PRINT_SCREEN, TYPE_STRING, "Đang chuyển hướng cuộc gọi.")
        else:
            return fm.create_data_transfer(RM_STT_RESULT, TYPE_JSON,
                                           json.dumps({"result": 0, "status": f"{recv.friend_id} không trực tuyến."}))
    if data.header == RM_STT_RESULT:
        recv = data.get_object()
        fr_sk = manager.get_socket(int(recv.channel_id))
        if fr_sk:
            queue[fr_sk].put_nowait(data)
            out.add(fr_sk)
        return fm.create_data_transfer(PRINT_SCREEN, TYPE_JSON, json.dumps({"result":1}))

    if data.header == RM_STT_FINISH:
        recv = data.get_object()
        fr_sk = manager.get_socket(int(recv.friend_id))
        if fr_sk:
            queue[fr_sk].put_nowait(data)
            out.add(fr_sk)
        return fm.create_data_transfer(PRINT_SCREEN, TYPE_JSON, json.dumps({"result":1}))

    if data.header == FRIEND_ONLINE:
        ids = data.get_data()
        js = []

        for x in ids:
            if x in manager.mapuser.keys(): res = True
            else: res = False
            js.append({"friend_id":x , "online": res})
        return  fm.create_data_transfer(FRIEND_ONLINE, TYPE_JSON, json.dumps(js))


    # if data.header in (RM_STT_START, RM_STT_FINISH):
    #     recv = data.get_object()
    #
    #     message = f"{recv.hoten} đang thực hiện cuộc gọi!"
    #
    #     if data.header == RM_STT_FINISH:
    #         message = f"{recv.hoten} đã kết thúc cuộc gọi!"
    #
    #     js = fm.create_data_transfer(data.header, TYPE_JSON,
    #                                  json.dumps({"result": message}))
    #
    #     if data.header == RM_STT_FINISH:
    #         db.insert_message(recv.masv, recv.maphong, message)
    #
    #     for x in rooms[recv.maphong]:
    #         if x != sk: sendbytes(x, js.tobytes())
    #
    #     return js
    #
    # if data.header == CONNECT_ROOM:
    #     recv = data.get_object()
    #
    #     # neu khong ton tai phong chat
    #     if not db.contain_idroom(recv.maphong):
    #         return  fm.create_data_transfer(NOT_FOUND, TYPE_JSON,
    #                                         json.dumps({'result': 0, 'message': f'Không tìm thấy phòng {recv.maphong}.'}))
    #
    #     if recv.maphong not in rooms:
    #         rooms[recv.maphong] = []
    #     rooms[recv.maphong].append(sk)
    #
    #     js = fm.create_data_transfer(CONNECT_ROOM, TYPE_JSON,
    #                                  json.dumps({"result": f"{recv.hoten} đã tham gia phòng chat!"}))
    #     for x in rooms[recv.maphong]:
    #         if x != sk: sendbytes(x, js.tobytes())
    #
    #     printf("Số phòng: %s \t tổng thành viên: %s." % (recv.maphong, len(rooms[recv.maphong])))
    #     js = db.get_top10message(recv.maphong)
    #
    #     # xu ly khi khong co phong chat
    #     if '\"result\": 1' in js:
    #         return fm.create_data_transfer(NOT_FOUND, TYPE_JSON, )
    #
    #     return fm.create_data_transfer(CONNECT_ROOM, TYPE_JSON, js)
    #
    #
    # elif data.header == EXIT_ROOM:
    #     rev = data.get_object()
    #     rooms[rev.maphong].remove(sk)
    #     js = fm.create_data_transfer(CONNECT_ROOM, TYPE_JSON,
    #                                  json.dumps({"result": "%s đã rời phòng chat!" % (rev.hoten)}))
    #     for x in rooms[rev.maphong]:
    #         sendbytes(x, js.tobytes())
    #
    #     return js
    #
    # elif data.header == SEND_ROOM:
    #     revc = data.get_object()
    #     data.header = RECV_ROOM
    #
    #     for x in rooms[revc.maphong]:
    #         if x != sk:
    #             queue[x].put_nowait(data)
    #             out.add(x)
    #
    #     db.insert_message(revc.masv, revc.maphong, revc.noidung)
    #     return fm.create_data_transfer(PRINT_SCREEN, data='Đã giử thành công.')
    #
    # elif data.header == END_CONNECT:
    #     recv = data.get_object()
    #
    #     # xoa socket thanh vien
    #     if sk in rooms[recv.maphong]:
    #         rooms[recv.maphong].remove(sk)
    #
    #     data = fm.create_data_transfer(CONNECT_ROOM, TYPE_JSON, json.dumps({"result": "Đã rời phòng chat!"}))
    #
    #     # giu thong bao cho team
    #     for x in rooms[recv.maphong]:
    #         sendbytes(x, data.tobytes())
    #
    #     # tra ve ket qua
    #     return data


# xu ly tac vu ca nhan tu client
def task_service(data, sk, con, manager):
    try:
        if data.header == END_CONNECT:
            con.append(sk)
            return None

        elif data.header == GET_CURRENT_WEATHER:
            recv = data.get_object()
            json_arr = weather.read_html_from_website(recv.diadiem)
            db.insert_content_search(recv.masv, json_arr ,recv.diadiem)
            return fm.create_data_transfer(GET_CURRENT_WEATHER, TYPE_JSON, json_arr)

        elif data.header == SEARCH_HISTORY:
            recv = data.get_object()
            res = db.search_history(recv.masv, recv.thoigian, recv.diadiem)
            return fm.create_data_transfer(SEARCH_HISTORY, TYPE_JSON, res)

        elif data.header == UPDATE_USER:
            js = db.update_user(data.get_data())
            return fm.create_data_transfer(PRINT_SCREEN, TYPE_JSON, js)

        # Dang nhap
        elif data.header == POST_LOGIN:
            recv = data.get_object()
            data = db.login(recv.masv, recv.password)

            if json.loads(data)["result"] == 1:
                manager.add(int(recv.masv), sk)
            printf(f"Danh sách kết nối: " + str(manager.mapuser.keys()))
            return fm.create_data_transfer(POST_LOGIN, TYPE_JSON, data)

        # Thay doi mat khau
        elif data.header == PUT_PASSWORD:
            data = data.get_object()
            data = db.change_password(data.masv, data.oldpass, data.newpass)
            return fm.create_data_transfer(PRINT_SCREEN, data=data)

        # Cap nhat mat khau
        elif data.header == PUT_UPDATE_SINHVIEN:
            data = data.get_data()
            data = db.update_sinhvien(data["masv"], data)
            return fm.create_data_transfer(PRINT_SCREEN, data=data)

        # Them sinh vien
        elif data.header == POST_INSERT_SINHVIEN:
            data = data.get_data()
            data = db.insert_sinhvien(data["masv"], data)
            return fm.create_data_transfer(PRINT_SCREEN, TYPE_STRING, data=data)

        # Cap nhat diem
        elif data.header == PUT_DIEM:
            data = data.get_object()
            data = db.update_tablediem(data.masv, data.mamh, data.lanthi, data.diemtp, data.diemthi)
            return fm.create_data_transfer(PRINT_SCREEN, data=data)

        elif data.header == GET_CLASS_NO:
            data = data.get_object()
            data = db.get_class_NO(data.malop)
            return fm.create_data_transfer(GET_CLASS_NO, TYPE_JSON, data)

        elif data.header == GET_DIEM_SV:
            data = data.get_object()
            data = db.get_diem(data.masv)
            return fm.create_data_transfer(GET_DIEM_SV, TYPE_JSON, data)

        elif data.header == GET_SEARCH:
            data = data.get_object()
            data = db.get_search(data.keyword)
            return fm.create_data_transfer(GET_SEARCH, TYPE_JSON, data)

        elif data.header == GET_SOLUONG_SV:
            data = db.get_soluong_sinhvien()
            return fm.create_data_transfer(GET_SOLUONG_SV, TYPE_JSON, data)

        else:
            error = 'Không tìm thấy lệnh [{}].'.format(data.header)
            return fm.create_data_transfer(PRINT_SCREEN, TYPE_STRING, error)

    except Exception as e:
        return fm.create_data_transfer(data="Lỗi dữ liệu! {}".format(e))

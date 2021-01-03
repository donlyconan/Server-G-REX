import datetime
import json

from mysql import connector
from win32com.test.testPersist import now

from common import formatter as fm
from common import support_database as sp

DATABASE_NAME = 'quanlyhs'

con = connector.connect(host='localhost', database=DATABASE_NAME, user='root', password="")


def opendb():
    if con == None or con.is_connected() == False:
        connector.connect(host='localhost', database=DATABASE_NAME, user='root', password="")
    if (con.is_connected()):
        print('Ket noi thanh cong %s!', con.user)
    return con


def close():
    if (con != None and con.is_connected()):
        con.close()


def contain_masv(masv):
    sql = f'Select masv from tbsinhvien where masv={masv}'
    cur = con.cursor()
    cur.execute(sql)
    index = len(cur.fetchall())
    cur.close()
    if index > 0:
        return True
    else:
        raise Exception("Mã sinh viên %s không tồn tại" % masv)


""" ____________________________________xu ly thong tin sinh vien__________________________________________"""
def get_user_info(masv):
    sql = f"SELECT masv ,hoten, url_avatar , malop, gioitinh, sdt, email, diachi FROM tbsinhvien WHERE masv = {masv}"
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()[0]
    cur.close()
    js = {
        'masv': rows[0],
        'hoten': rows[1],
        'url_avatar': rows[2],
        'malop': rows[3],
        'gioitinh': rows[4],
        'sdt': rows[5],
        'email': rows[6],
        'diachi': rows[7]
    }
    return json.dumps(js)


def login(masv, password):
    cursor = con.cursor()
    cursor.execute("select masv,hoten from tbsinhvien where masv=%s and matkhau=%s", (masv, password))
    rows = cursor.fetchall()
    cursor.close()
    if len(rows) > 0:
        row = rows[0]
        masv, hoten = row[0], row[1]
        return json.dumps({"login": "Đăng nhập thành công.", "result": 1, "masv": masv, "hoten": hoten,
                           "userinfo": json.loads(get_user_info(masv))})
    else:
        return json.dumps({"login": "Tài khoản hoặc mật khẩu không chính xác.", "result": -1})


"""______________________________________Xu ly tin nhan______________________________-"""
def get_list_message(masv, friend_id, _from=0, to=15):
    sql = f"""SELECT id ,sender_id, receiver_id, content, url_file, create_at, seen
        FROM `tbtinnhan` 
        WHERE {masv} in (sender_id,receiver_id) and {friend_id} in (sender_id, receiver_id)
        ORDER BY id DESC
        LIMIT {_from},{to}
    """
    print(f'SQL: {sql}')

    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    rows = list(rows)
    rows.reverse()
    cur.close()
    header = ['id', 'sender_id', 'reciever_id', 'content', 'url_file', 'create_at', 'seen']
    js = fm.convert_array_tojson(header, rows)
    return json.dumps(js)


def insert_message(data):
    data["create_at"] = str(now)
    sql = sp._insert_("tbtinnhan", data)
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    cur.close()
    return json.dumps({'result': 1})


def saw_message(sender_id, receiver_id):
    sql = f"Update tbtinnhan set seen = 1 where {sender_id} in (sender_id, receiver_id) and {receiver_id} in (sender_id, receiver_id) "
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    cur.close()
    return json.dumps({'result': 1})

def update_user(data):
    sql = sp._update_("tbsinhvien", data, {"masv":data["masv"]})
    print(sql)
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    cur.close()
    return json.dumps({'result': 1})


"""____________________________________Xu ly bạn bè_____________________________________________"""


def get_list_friend(masv):
    sql = f"""
        SELECT tb.id, tb.friend_id, tn.sender_id , sv.url_avatar, sv.hoten, content , tn.url_file, tn.create_at, tn.seen
        FROM tbtinnhan as tn, 
        (
            SELECT MAX(id) as id, CASE WHEN sender_id={masv} THEN receiver_id ELSE sender_id END friend_id
            FROM tbtinnhan WHERE {masv} in (sender_id,receiver_id) 
            GROUP BY CASE WHEN sender_id={masv} 
            THEN receiver_id ELSE sender_id END
        ) as tb, tbsinhvien as sv
        WHERE tb.id = tn.id and sv.masv = tb.friend_id
    """
    print("Get List Friend: " + sql)
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    header = ['id', 'friend_id', "sender_id", 'url_avatar', 'hoten', 'content', 'url_file', 'createAt', 'seen']
    js = fm.convert_array_tojson(header, rows)
    return json.dumps(js)

def get_last_message(masv, friend_id):
    sql = f"""SELECT * FROM `tbtinnhan` 
    WHERE sender_id={masv} and reciever_id = {friend_id} or sender_id={friend_id} and reciever_id={masv} 
    ORDER by date DESC LIMIT 1"""
    print(f'Sql: {sql}')
    cur = con.cursor()
    cur.execute(sql)
    row = cur.fetchall()[0]
    cur.close()
    return row


"""______________________________________Xu ly thong tin lien quan den sinh vien_______________________"""


def get_diem(masv):
    sql = """SELECT 
                tbsinhvien.masv,hoten, malop,tbmonhoc.tenmh,stc,diemtp, diemthi, (diemtp * 0.3 + diemthi * 0.7)as diem 
            FROM 
                tbdiem INNER JOIN tbsinhvien on tbdiem.masv = tbsinhvien.masv INNER JOIN tbmonhoc ON tbmonhoc.mamh = tbdiem.mamh
            WHERE 
                tbsinhvien.masv = %s""" % (masv)

    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    if contain_masv(masv):
        row = rows[0]
        js = {"masv": row[0], "hoten": row[1], "malop": row[2], "diem": []}

        for x in rows:
            z = {"tenmh": x[3], "stc": x[4], "diemtp": x[5], "diemthi": x[6], "diem": x[7]}
            js["diem"].append(z)
    return json.dumps(js)


def get_soluong_sinhvien():
    sql = """SELECT 
                tblop.malop, tenlop, COUNT(tblop.malop) as soluong 
            FROM 
                tbsinhvien INNER JOIN tblop on tbsinhvien.malop = tblop.malop 
            GROUP BY 
                tblop.malop
            """
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()

    if len(rows) == 0:
        raise Exception("Không có sinh viên nào trong lớp hoặp lớp không tồn tại");
    cur.close()
    js = fm.convert_array_tojson(["malop", "tenlop", "soluong"], rows)
    return json.dumps(js)


def get_gioitinh(i):
    if int(i) == 0:
        return "Nam"
    else:
        return "Nữ"


def get_search(keyword):
    sql = "SELECT masv, hoten, malop, gioitinh,sdt,email,diachi FROM tbsinhvien WHERE masv LIKE '%{}%' or hoten LIKE '%{}%'".format(
        keyword, keyword)
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()

    if len(rows) == 0:
        raise Exception('Không tìm được kết quả!')
    row = rows[0]
    js = []

    for x in rows:
        js.append(
            {"masv": x[0], "hoten": x[1], "malop": x[2], "gioitinh": get_gioitinh(x[3]), "sdt": "+{}".format(x[4]),
             "email": x[5], "diachi": x[6]})
    return json.dumps(js)


def get_class_NO(malop):
    sql = """SELECT tenlop,masv,hoten,gioitinh,sdt,email 
            FROM tblop INNER JOIN tbsinhvien on tblop.malop = tbsinhvien.malop
            WHERE tblop.malop = \"%s\"""" % (malop)
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    js = {"malop": malop, "sv": []}

    if len(rows) == 0:
        raise Exception("Lớp không tồn tại.")
    else:
        row = rows[0]
        js["tenlop"] = row[0]

        for x in rows:
            z = {"masv": x[1], "hoten": x[2], "gioitinh": get_gioitinh(x[3]), "sdt": x[4], "email": x[5]}
            js["sv"].append(z)
    return json.dumps(js)


def get_list_class():
    sql = "SELECT malop,tenlop FROM tblop"
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    listtr = ''
    for m, t in rows:
        listtr += f'{m}:{t},'
    return listtr[:-1]


def change_password(masv, oldpass, newpass):
    sql = "SELECT masv FROM tbsinhvien WHERE masv=%s AND matkhau=%s"
    cur = con.cursor()
    cur.execute(sql, (masv, oldpass))

    if len(cur.fetchall()) == 0:
        raise Exception("Tài khoản hoặc mật khẩu không tồn tại")
    else:
        sql = "UPDATE tbsinhvien SET matkhau = %s WHERE masv = %s and matkhau = %s"
        cur.execute(sql, (newpass, masv, oldpass))
        con.commit()
        return "Cập nhật mật khẩu thành công"


def update_tablediem(masv, mamh, lanthi, diemtp, diemthi):
    sql = "UPDATE tbdiem SET diemtp = %s, diemthi=%s WHERE masv=%s and lanthi=%s AND mamh = %s"
    if contain_masv(masv):
        cur = con.cursor()
        cur.execute(sql, (diemtp, diemthi, masv, lanthi, mamh))
        con.commit()
        cur.close()
        return "Cập nhật điểm thành công"


def insert_sinhvien(masv, files):
    sql = sp._insert_("tbsinhvien", files)
    try:
        contain_masv(masv)
    except:
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        cur.close()
        return "Cập nhật thành công"
    else:
        return "Thêm sinh viên thất bại có thể do mã sinh viên đã tồn tại"


def update_sinhvien(masv, dict):
    if contain_masv(masv):
        sql = sp._update_("tbsinhvien", dict, {"masv": masv})
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        cur.close()
    return "Cập nhật thành công!"


def get_allroom():
    sql = """SELECT tbphong.maphong, tenphong, admin, thoigian, COUNT(masv) as thanhvien
            FROM tbphong INNER JOIN tbmessage ON tbmessage.maphong = tbphong.maphong
            GROUP by tbphong.maphong"""
    cursor = con.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    js = fm.convert_array_tojson(["maphong", "tenphong", "admin", "ngaytao", "thanhvien"], rows)
    return json.dumps(js)


def get_top10message(maphong, start=0, end=10, sort="DESC"):
    sql = """SELECT tbsinhvien.masv,hoten ,`noidung`, `thoigian`
            FROM `tbmessage` INNER JOIN tbsinhvien ON tbmessage.masv = tbsinhvien.masv 
            WHERE maphong = %s
            ORDER BY thoigian %s
            LIMIT %s,%s""" % (maphong, sort, start, end)
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()

    if len(rows) <= 0:
        return json.dumps({'result': 1})

    js = fm.convert_array_tojson(["masv", "hoten", "noidung", "thoigian"], rows)
    return json.dumps(js)



def contain_idroom(idroom):
    sql = "Select maphong From tbphong where maphong=%s" % idroom
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    con.commit()
    cur.close()
    return len(rows) > 0

"""__________________________________________________________________________________"""


def insert_content_search(masv, ketqua, timkiem):
    ketqua = json.dumps(ketqua)[1:-1]
    sql = f"INSERT INTO `tblichsutimkiem`(`userid`, `thoigian`, `ketqua`, `timkiem`) " \
          f"VALUES ({masv},\"{datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')}\",\"{ketqua}\", \"{timkiem}\")"
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    cur.close()

def search_history(masv ,thoigian, diadiem):
    sql = f"""SELECT id, thoigian ,ketqua , DATE_FORMAT(thoigian, '%d/%m/%Y') 
    FROM `tblichsutimkiem` 
    WHERE userid={masv} AND DATE_FORMAT(thoigian, '%d/%m/%Y') LIKE '{thoigian}' AND timkiem = '{diadiem}' ORDER BY id DESC LIMIT 1"""
    cur = con.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()

    if len(rows) == 0:
        return json.dumps({"result": 0})
    else:
        row = rows[0]
        return json.dumps({
            'result': 1, 'id':row[0], 'thoigian': row[1].strftime("%d/%m/%Y %H:%M:%S"), 'ketqua':json.loads(row[2])
        })



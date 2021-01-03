class Manager:
    current_index = 1000

    """
        dung 2 map de luu tru user & socket
        1: co the kiem tra danh tinh socket la 1 id user
        2: co the tu user dinh vi socket ket noi la gi
    """

    def __init__(self, mapuser, mapsocket):
        self.mapuser = mapuser
        self.mapsocket = mapsocket

    def add(self, masv, socket):
        self.mapuser[masv] = socket
        self.mapsocket[socket] = masv

    def get_socket(self, masv):
        if masv in self.mapuser:
            return self.mapuser[masv]

    def get_user_id(self, socket):
        if socket in self.mapsocket:
            return self.mapsocket[socket]

    def has_user_id(self, user_id):
        return user_id in self.mapuser

    def clear_socket(self, socket):
        if socket in self.mapsocket:
            masv = self.mapsocket[socket]
            del self.mapsocket[socket]

            if masv in self.mapuser:
                del self.mapuser[masv]

    def __repr__(self):
        return str([f"{x}:{self.mapuser[x].getsockname()}" for x in self.mapuser])
        + " <-> " + str([f"{x.getsockname()}:{self.mapsocket[x]}" for x in self.mapsocket])



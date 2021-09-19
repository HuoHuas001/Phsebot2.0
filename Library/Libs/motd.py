import socket
import time


class Server:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.__msglist = [0x00, 0xFF, 0xFF, 0x00, 0xFE, 0xFE, 0xFE, 0xFE, 0xFD, 0xFD, 0xFD, 0xFD, 0x12, 0x34, 0x56, 0x78]

    def motd(self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = socket.getaddrinfo(self.ip, "https")[0][4][0]
        if self.ip == "localhost":
            ip = "127.0.0.1"
        serverAddress = (ip, self.port)
        clientSocket.connect(serverAddress)
        ts = time.time()

        i = 0

        while i < 8:
            self.__msglist.insert(0, str(ts).encode()[i])
            i += 1

        self.__msglist.insert(0, 0x01)

        clientSocket.sendto(bytes(self.__msglist), serverAddress)

        while True:
            try:
                receiveData = clientSocket.recv(10240)
                receiveList = receiveData.decode('UTF-8', errors='ignore').split(";")
                returnDict = {
                "status":'online',
                "ip": self.ip,
                "port": self.port,
                "name": receiveList[1],
                "protocol": receiveList[2],
                "version": receiveList[3],
                "online": receiveList[4],
                "upperLimit": receiveList[5],
                "save": receiveList[7],
                "gamemode": receiveList[8],
                "difficulty": receiveList[9],
                "port_ipv6": receiveList[11],
                "delay": int((time.time() - ts) * 1000)
            }
                clientSocket.close()
                return returnDict
            except:
                return {'status':'offline'}


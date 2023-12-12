import socket
import threading
import time
import pygame
from fff.Server.GameState import GameState, UpdateGameState
from fff.Server.player import *
from fff.Server.lvl import BlockTeleport, Platform, BlockDie


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.Clients = []
        self.level = []
        self.entities = pygame.sprite.Group()
        self.animatedEntities = pygame.sprite.Group()
        self.platforms = []
        self.loadLevel()
        self.PreviousGS = []
        self.UnprocessedInput = []
        self.ProcessedInput = []
        print(f"UDP Echo Server listening on {self.host}:{self.port}")
        self.hero1 = Player(100,100)
        self.hero2 = Player(100,100)
        self.entities.add(self.hero1)
        self.entities.add(self.hero2)
        import time
        self.LastCheck = time.time()
        self.RequestChecker1 = {}
        self.RequestChecker2 = {}
        self.gs = GameState(self.LastCheck, self.level, self.hero1, self.hero2)
        self.PreviousGS.append(GameState(self.LastCheck, self.level, self.hero1, self.hero2))

        x = y = 0
        for row in self.level:
            for col in row:
                if col == "-":
                    pf = Platform(x, y)
                    self.entities.add(pf)
                    self.platforms.append(pf)
                if col == "*":
                    bd = BlockDie(x, y)
                    self.entities.add(bd)
                    self.platforms.append(bd)
                x += 64
            y += 64
            x = 0

    def UpdateServer(self):
        while len(self.UnprocessedInput) > 0:
            import time
            t = time.time()
            self.gs = UpdateGameState(self.platforms, self.PreviousGS[-1], t, self.UnprocessedInput[-1])
            self.ProcessedInput.append(self.UnprocessedInput.pop())
        self.PreviousGS.append(self.gs)
        for i in range(len(self.Clients)):
            clietn_ip = (self.Clients[i].IP, self.Clients[i].Port)
            self.server_socket.sendto(f"{self.Clients[i].Number} {self.gs.getGameState()}".encode('utf-8'), clietn_ip)

    def SERVERWORK(self):
        while True:
            data, client_address = self.server_socket.recvfrom(1024)
            ReceiveMessageHandler(self, data.decode('utf-8'), client_address[0], client_address[1])
            import time
            if time.time() - self.LastCheck >= 0.2:
                self.UpdateServer()
                self.LastCheck = time.time()

    def AddClient(self, IP, Port):
        Have = False
        for i in range(len(self.Clients)):
            if self.Clients[i].IP == IP and self.Clients[i].Port == Port:
                Have = True
        if not Have:
            with threading.Lock():
                Cl = Client(IP, Port)
                Cl.SetNumber(len(self.Clients))
                self.Clients.append(Cl)

    def FindClient(self, Client):
        for i in range(len(self.Clients)):
            if self.Clients[i].IP == Client.IP and self.Clients[i].Port == Client.Port:
                return i

    def loadLevel(self):
        tp = BlockTeleport(162, 1038, 144, 1230)
        self.entities.add(tp)
        self.platforms.append(tp)
        self.animatedEntities.add(tp)
        global playerX, playerY
        levelFile = open("fff/Server/levels/lvl1.txt")
        line = " "
        commands = []
        while line[0] != "/":
            line = levelFile.readline()
            if line[0] == "[":
                while line[0] != "]":
                    line = levelFile.readline()
                    if line[0] != "]":
                        endLine = line.find("|")
                        self.level.append(line[0: endLine])
            if line[0] != "":
                commands = line.split()
                if len(commands) > 1:
                    if commands[0] == "player":
                        playerX = int(commands[1])
                        playerY = int(commands[2])
                    if commands[0] == "portal":
                        tp = BlockTeleport(int(commands[1]), int(commands[2]), int(commands[3]), int(commands[4]))
                        self.entities.add(tp)
                        self.platforms.append(tp)


class Client:
    def __init__(self, IP, Port):
        self.IP = IP
        self.Port = Port
        self.Number = None

    def SetNumber(self, number):
        self.Number = number


class ReceiveMessageHandler:
    def __init__(self, Server, message, IP, Port):
        self.IP = IP
        self.Server = Server
        self.Port = Port
        self.locker = threading.Lock()
        thread = threading.Thread(target=self.LogicFunc, args=(message,))
        thread.start()

    def LogicFunc(self, Message):
        self.locker.acquire()
        self.Server.AddClient(self.IP,self.Port)
        if(Message == 'connect' and len(self.Server.Clients) == 1):
            clietn_ip = self.IP, self.Port
            self.Server.server_socket.sendto('cat'.encode('utf-8'), clietn_ip)
        i = self.Server.FindClient(Client(self.IP, self.Port))
        PlInp = PlayerInput(Message,i)
        if PlInp.request in self.Server.RequestChecker1 and i == 0:
            return
        if PlInp.request in self.Server.RequestChecker1 == False and i == 0:
            self.Server.RequestChecker1[PlInp.request] = True
        if PlInp.request in self.Server.RequestChecker2 and i == 1:
            return
        if PlInp.request in self.Server.RequestChecker2 == False and i == 1:
            self.Server.RequestChecker2[PlInp.request] = True
        self.Server.UnprocessedInput.append(PlInp)

        self.locker.release()


class PlayerInput:
    def __init__(self, message, number):
        Words = message.split()
        self.request =Words[5]
        self.ts = Words[0]
        self.InputString = Words[1]+" "+Words[2]+" "+Words[3]+" "+Words[4]
        self.Number = number
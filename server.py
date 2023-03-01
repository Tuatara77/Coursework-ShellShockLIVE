import wsgiserver

import threading
from time import sleep


class Server:
    def __init__(self, port:int=8000):
        self.sep = "/"
        self.paths = wsgiserver.WSGIPathInfoDispatcher({
            "/": self._main,
            "/sendPlayerData": self._sendPlayerData,
            "/getPlayerData": self._getPlayerData,
            "/addPlayer": self._addPlayer,
            "/addProjectile": self._addProjectile,
            "/getProjectileData": self._getProjectileData,
        })
        self.server = wsgiserver.WSGIServer(self.paths, port=port)
        self.players = {}
        self.projectiles = []

        printThread = threading.Thread(target=self.printDict, daemon=True)
        # printThread.start()

        # players dictionary format:
        # self.players = {
        #              "name": {
        #                       0: xcoord,
        #                       1: ycoord,
        #                       2: barrel angle,
        #                       3: barrel power,
        #                       4: health,
        #                       }
        #            }

        # projectiles list format:
        # self.projectiles = [(xcoord, ycoord, radius, angle, power)]

    def start(self):
        """Starts the server"""
        self.server.start()

    def stop(self):
        """Stops the server"""
        self.server.stop()

    def addPlayer(self, name, data):
        """Adds a player to the server (host only)"""
        self.players[name] = {index:item for index, item in enumerate(data)}
    
    def sendPlayerData(self, name, data):
        """Sends data to the server (host only)"""
        self.players[name] = {index:item for index, item in enumerate(data)}
    
    def getPlayerData(self):
        """Receives data from the server (host only)"""
        return self.players

    def addProjectile(self, data):
        """Adds a projectile to the server (host only)"""
        self.projectiles.append(list(data))
    
    def getProjectileData(self):
        """Receives data from the server (host only)"""
        return self.projectiles

    def _main(self, environ, start_response):
        """Main page, appears as a gateway error to prevent external manipulation"""
        start_response("503", [('Content-type','text/plain')])
        yield b""
    
    def _sendPlayerData(self, environ, start_response):
        """Server is RECEIVING external data"""
        data = environ["PATH_INFO"][1:].split("/")
        if data: self.players[data[0]] = {index:int(item) if item.isnumeric() else item for index, item in enumerate(data[1:])}
        start_response("503", [('Content-type','text/plain')])
        yield b""

    def _getPlayerData(self, environ, start_response):
        """Server is SENDING data externally"""
        start_response("503", [("Content-type", "text/plain")])
        body = bytes(str(self.players), "utf-8")
        yield body
    
    def _addPlayer(self, environ, start_response):
        """Adds a player to the server"""
        data = environ["PATH_INFO"][1:].split("/")
        if data: self.players[data[0]] = {index:int(item) if item.isnumeric() else item for index, item in enumerate(data[1:])}
        start_response("503", [('Content-type','text/plain')])
        yield b""
    
    def _addProjectile(self, environ, start_response):
        """Adds a projectile to the server"""
        data = environ["PATH_INFO"][1:].split("/")
        if data: self.projectiles.append([int(item) if item.isnumeric() else item for item in data])
        start_response("503", [('Content-type','text/plain')])
        yield b""
    
    def _getProjectileData(self, environ, start_response):
        """Gets the projectile data from the server"""
        start_response("503", [("Content-type", "text/plain")])
        body = bytes(str(self.projectiles), "utf-8")
        yield body
    
    def printDict(self):
        while True:
            print("{")
            for index in self.players:
                print(f"\t{index}: {'{'}")
                for item in self.players[index]:
                    print(f"\t\t{item}: {self.players[index][item]}")
                print("\t}")
            print("}")
            print(self.projectiles)
            sleep(1)
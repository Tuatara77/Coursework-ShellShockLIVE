from http.client import HTTPConnection

class Client:
    def __init__(self, server_ip:str, server_port:int=8000):
        self.ip = server_ip
        self.port = server_port
        # self.conn = HTTPConnection(f"{server_ip}:{server_port}", timeout=10)

    def getPlayerData(self):
        """Retrieves data from the server"""
        conn = HTTPConnection(f"{self.ip}:{self.port}", timeout=10)
        conn.request("GET","/getPlayerData")
        # self.conn.request("GET",path)
        # r1 = self.conn.getresponse()
        r1 = conn.getresponse()
        content = r1.read()
        conn.close()
        return str(content, "utf-8")

    def sendPlayerData(self, *data):
        """Sends data to the server"""
        conn = HTTPConnection(f"{self.ip}:{self.port}", timeout=10)
        path = "/sendPlayerData/" + "/".join([str(item) for item in data])
        # self.conn.request("POST", path)
        conn.request("POST", path)
        conn.close()
    
    def addPlayer(self, *data):
        """Adds a player to the server"""
        conn = HTTPConnection(f"{self.ip}:{self.port}", timeout=10)
        path = "/addPlayer/" + "/".join([str(item) for item in data])
        # self.conn.request("POST", path)
        conn.request("POST", path)
        conn.close()
    
    def addProjectile(self, *data):
        """Adds a projectile to the server"""
        conn = HTTPConnection(f"{self.ip}:{self.port}", timeout=10)
        path = "/addProjectile/" + "/".join([str(item) for item in data])
        # self.conn.request("POST", path)
        conn.request("POST", path)
        conn.close()
    
    def getProjectileData(self):
        """Retrieves data from the server"""
        conn = HTTPConnection(f"{self.ip}:{self.port}", timeout=10)
        conn.request("GET","/getProjectileData")
        # self.conn.request("GET",path)
        # r1 = self.conn.getresponse()
        r1 = conn.getresponse()
        content = r1.read()
        conn.close()
        return str(content, "utf-8")

    # def stop(self): self.conn.close()
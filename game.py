# import everything relevant
import json
import random
import pygame
import images
import threading
import numpy as np
from time import sleep
from client import Client
from server import Server
from colours import black, white, light_blue, orange
from math import sin, cos, atan, log, radians, degrees, pi
from pygame.locals import QUIT, KEYDOWN, KEYUP, K_ESCAPE, K_F1

# store constant variables as a dictionary in a json file
with open("constants.json", "r") as constants: const = json.load(constants)

# https://blog.finxter.com/python-dunder-methods-cheat-sheet/


def clamp(value, min=0, max=1000):
    """Clamps a value between a minimum and maximum value"""
    if value < min: return min
    elif value > max: return max
    else: return value


projectiles = []
class Projectile:
    def __init__(self, x, y, radius, angle, power, damage:int=30):
        """Initialises the projectile with the required parameters"""
        self.x = x
        self.y = y
        self.radius = radius
        self.angle = angle
        self.power = power
        self.damage = damage
        self.rect = pygame.Rect(x-radius, y-radius, 2*radius, 2*radius)

        self.xvel = (cos(radians(angle))*power)/4 # initial x and y velocities (scaled down by 4 to
        self.yvel = (sin(radians(angle))*power)/4 # make the projectile travel at a reasonable speed)
        projectiles.append(self)

    def getData(self): return self.x, self.y, self.radius, self.angle, self.power, self.damage
    def getDamage(self): return self.damage
    def getRect(self): return self.rect
    def draw(self, surface): 
        """Draws the projectile on the given surface"""
        self.rect = pygame.draw.circle(surface, white, (round(self.x), round(self.y)), self.radius)
    
    def update(self, ground, tanks):
        """Relevant updates to the projectile"""
        self.move()  
        self.collide(ground, tanks)

    def collide(self, ground, tanks):
        """Checks if the projectile is within the screen
        or has collided with the ground, removing its existence if so"""
        if self.x <= 0 or self.x >= const["screenwidth"]:
            projectiles.remove(self)
            del self
            return

        if self.y >= ground.getHeightAtPoint(round(self.x)): # if the projectile has collided with the ground
            ground.destroyAtPoint((round(self.x), round(self.y)), 3*self.radius) # destroy the ground at the point of impact
            Explosion(round(self.x), ground.getHeightAtPoint(round(self.x)), 3*self.radius)
            for tank in tanks:
                if tank.getRect().colliderect(self.rect): # if the projectile has collided with a tank
                    tank.damage(self.damage)   # damage the tank
            projectiles.remove(self)
            del self

    def move(self):
        """Updates the projectile's position"""
        self.x += self.xvel # update the x and y coordinates
        self.y += self.yvel
        self.yvel += const["gravity"] # simplified v = u + at, where a = gravity to update the y velocity

        if self.y > const["screenheight"]: # if the projectile is below (off of) the screen
            projectiles.remove(self)  # remove its existence from the game
            del self


explosions = []
class Explosion:
    def __init__(self, x, y, maxRadius):
        self.x = x   # assign relevant variables
        self.y = y
        self.maxRadius = maxRadius
        self.radius = 1
        self.drdt = 0.1
        explosions.append(self)
    
    def draw(self, surface): # draw the explosion
        pygame.draw.circle(surface, orange, (round(self.x), round(self.y)), round(self.radius))

    def decay(self, ticks):
        """Decays the explosion circle over time"""
        self.radius += self.drdt*ticks    # change explosion radius
        if self.radius >= self.maxRadius: # if maximum radius is reached
            self.drdt *= -1               # reverse rate of change of radius

        if self.radius <= 0:        # if the radius is at it's minimum
            self.radius = 0         # prevent a zero-radius error (a bit of a cheap way of doing it)
            explosions.remove(self) # remove the explosion from drawable explosions
            del self                # delete the explosion from memory


class Barrel:
    def __init__(self, image, angle, power):
        self.angle = angle # random starting values
        self.power = power
        self.originalimage = pygame.transform.scale(image, (round(const["screenheight"]/26), round(const["screenheight"]/500)))
    
        self.image = self.originalimage
        self.rotate(0) # rotate the barrel to the starting angle
        
    def rotate(self, angle):
        self.angle += angle # update the angle
        self.angle %= 360 # make sure the angle is between 0 and 360
        self.image = pygame.transform.rotate(self.originalimage, -self.angle) # rotate the barrel image
    
    def changepower(self, increment):
        # update the power, ensuring it is between 0 and 100
        self.power = clamp(self.power + increment, max=100)


tankg = [] # this is a list
class Tank: # Tank class that inherits from Centre referencepoint class
    def __init__(self, x, y, angle=random.randint(0,359), power=random.randint(0,100), baseHealth:int=200, enemy:bool=False, name="Player"): # constructor
        if enemy: 
            image = images.enemy_tank          # selection between usage of enemy or friendly tank images
            barrel = images.enemy_tank_barrel
        else:
            image = images.friendly_tank
            barrel = images.friendly_tank_barrel

        self.health = baseHealth # the tank's initial health
        self.alive = True # whether the tank is alive or not
        self.name = name # the player's username

        # initialise the tank's image, barrel and rect (collision box)
        self.originalImage = pygame.transform.scale(image, (round((const["screenheight"]/70)*2.2), round(const["screenheight"]/70)))
        self.image = self.originalImage
        self.rect = self.image.get_rect(center=(x,y+self.image.get_height()//2))
        self.barrel = Barrel(barrel, angle, power)
        self.height = self.rect.height
        self.font = pygame.font.SysFont("ebrima", 10, bold=True)
        self.friendly = not enemy

        tankg.append(self) # add tank to list of tanks in game

    def draw(self, surface: pygame.Surface):
        if 0 <= self.barrel.angle <= 90: angle = -self.barrel.angle   # finnicky maths to make the angle display correctly
        elif 90 < self.barrel.angle <= 270: angle = self.barrel.angle-180
        elif 270 < self.barrel.angle <= 359: angle = 360-self.barrel.angle
        surface.blit(*render(self.font, f"{self.barrel.power}, {angle}", (self.rect.left+2, self.rect.centery+20))) # display power and angle
        surface.blit(*render(self.font, f"{self.name}: {self.health}", (self.rect.left-7, self.rect.centery-30))) # display health
        surface.blit(self.barrel.image, self.barrel.image.get_rect(center=self.rect.center))
        surface.blit(self.image, self.rect) # draw the tank to a surface

    def getRect(self): return self.rect
    def isAlive(self): return self.alive
    def getName(self): return self.name
    def getData(self): return self.rect.centerx, self.rect.centery, self.barrel.angle, self.barrel.power
    def setData(self, data): 
        self.rect.centerx, self.rect.centery, self.barrel.angle, self.barrel.power = data
        self.barrel.rotate(0)
    def shoot(self): # shoot a projectile. this might expand if requried
        return Projectile(self.rect.centerx, self.rect.centery, 5, self.barrel.angle, self.barrel.power)
    
    def collide(self, ground):
        height = ground.getHeightAtPoint(self.rect.centerx) # get ground y-coordinate at tank's collision reference point
        if self.rect.bottom != height: self.rect.centery = height-self.height//2

    def update(self, ground): 
        """do relevant updates to the tank. this will probably expand"""
        angle = degrees(atan(ground.getHeightAtPoint(self.rect.centerx)-ground.getHeightAtPoint(self.rect.centerx-1)))
        self.image = pygame.transform.rotate(self.originalImage, -angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.collide(ground)

    def damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            Explosion(self.rect.centerx, self.rect.centery, 50)
            tankg.remove(self)
            del self

    def move(self, dx, ground):
        # if the gradient of the ground is less than 4, the tank can move
        gradient = (ground.getHeightAtPoint(self.rect.centerx+dx) - ground.getHeightAtPoint(self.rect.centerx))/dx
        if -4 <= gradient <= 4:
            self.rect.x += dx
            if   self.rect.left < 0: self.rect.left = 0  # check that the tank is within the screen borders
            elif self.rect.right > const["screenwidth"]: self.rect.right = const["screenwidth"]


class Ground: # class for the ground
    def __init__(self, pointslist): # constructor defining the coordinates of the ground
        self.xcoords = np.array([point[0] for point in pointslist]) # list of x coordinates of the ground
        self.ycoords = np.array([point[1] for point in pointslist]) # list of y coordinates of the ground

    def draw(self, surface): 
        pygame.draw.polygon(surface, light_blue,  # draws the ground to a surface, adding extra points to close the polygon
                            [[xcoord, ycoord] for xcoord, ycoord in zip(self.xcoords, self.ycoords)]+
                            [[const["screenwidth"], const["screenheight"]], [0, const["screenheight"]]])

    def getHeightAtPoint(self, point): # get the ground height at a point
        try: return self.ycoords[np.where(self.xcoords == point)[0][0]] # if the point is in the list of points, return the y coordinate
        except IndexError: return False # if the point is not in the list of points, return False
    
    def destroyAtPoint(self, centre:tuple, radius:int):
        """Destroys the ground at a particular point in a circular radius"""
        for xcoord, ycoord in zip(self.xcoords, self.ycoords):
            if ycoord <= centre[1] and centre[0]-radius < xcoord < centre[0]+radius:
                # get the angle from the vertical (dx/dy) to the ground point from the explosion centre, avoiding division by 0
                angle = atan((xcoord-centre[0])/(ycoord-centre[1])) if ycoord-centre[1] != 0 else pi/2
                index = np.where(self.xcoords == xcoord)[0][0]

                self.ycoords[index] = ycoord+radius*(cos(angle)) # crater the ground

                if self.ycoords[index] > const["screenheight"]-64:
                    self.ycoords[index] = const["screenheight"]-64
        
        self.smooth()
    
    def smooth(self):
        """Smooths the ground surrounding an x coordinate by averaging the y coordinate 
            of each point with the y coordinate of the point above and below it"""
        # self.ycoords = self.smoothChaikin(self.xcoords, self.ycoords, 3)
        self.smoothChaikin(3)

    def smoothChaikin(self, refinements:int=1):
        """Smooths the ground using a modified version of Chaikin's corner-cutting algorithm"""
        for _ in range(refinements):
            for i in range(len(self.xcoords)-1):
                ay = self.ycoords[i]  # get the y coordinates of the current point and the next point
                by = self.ycoords[i+1]
                self.ycoords[i] = ay*0.75+by*0.25   # replace the current and next points with a
                self.ycoords[i+1] = ay*0.25+by*0.75 # reasonably weighted average of the two points


def generate_ground(groundheight:int, shape:str="longFunc"):
    if shape == "sine": # finnicky sine wave for ground points
        return Ground([[x, sin(radians(x))*80+const["screenheight"]-2*groundheight] for x in range(const["screenwidth"]+1)])
    elif shape == "flat": # constant y coordinate for ground points
        return Ground([[x, const["screenheight"]-groundheight] for x in range(const["screenwidth"]+1)])    
    elif shape == "longFunc":
        return Ground([[x-1, 10*(log((x/100)**2)*sin(x/100)+log((x/100)**4)*sin(x/50)-cos(x/100))+const["screenheight"]-2*groundheight] 
                        for x in range(1,const["screenwidth"]+2)])


def printDict(dic):
    print("{")
    for index in dic:
        print(f"\t{index}: {'{'}")
        for item in dic[index]:
            print(f"\t\t{item}: {dic[index][item]}    {type(dic[index][item])}")
        print("\t}")
    print("}")


class LANGame:
    def requestInfo(self):
        self.prevProjectileInfo = []
        while True:
            # get the player and projectile data from the server
            if self.host:
                self.playerInfo = self.server.getPlayerData()
                self.projectileInfo = self.server.getProjectileData()
            else:
                self.playerInfo = eval(self.client.getPlayerData())
                self.projectileInfo = eval(self.client.getProjectileData())
            
            # if the dictionary of players has changed, add the new players to the game
            if len(self.playerInfo) > len(self.prevPlayerInfo):
                prevPlayerInfoKeys = list(self.prevPlayerInfo.keys())
                playerInfoKeys = list(self.playerInfo.keys())
                for key in playerInfoKeys:
                    if key not in prevPlayerInfoKeys:
                        Tank(*list(self.playerInfo[key].values()), enemy=True, name=key)
                self.prevPlayerInfo = self.playerInfo.copy() # .copy() to make an actual copy as opposed to a reference

            # if the list of projectiles has changed, add the new projectiles to the game
            if len(self.projectileInfo) > len(self.prevProjectileInfo):
                newProjectileData = self.projectileInfo[len(self.prevProjectileInfo):]
                for projectile in newProjectileData:
                    Projectile(*projectile)
                self.prevProjectileInfo = self.projectileInfo.copy()
            sleep(0.1) # wait 0.1 seconds before requesting data again to not overload the server

    def __init__(self, screen: pygame.Surface, controls, data):
        username, self.ip, self.host = data
        DEBUG_INFO = False
        SHOW_HITBOXES = False

        if self.host:
            # if host, start the server
            self.server = Server(8000)
            serverThread = threading.Thread(target=self.server.start, daemon=True)
            serverThread.start()  # start server in a separate thread to prevent hanging
        else: self.client = Client(self.ip, 8000) # if not host, start the client

        font = pygame.font.SysFont("ebrima", 15, True)
        clock = pygame.time.Clock()
        groundheight = const["screenheight"]//6
        ground = generate_ground(groundheight, "longFunc")

        player1 = Tank(random.randrange(50, const["screenwidth"]-50), 
                       const["screenheight"]-groundheight, enemy=False, name=username)
        p1movingleft = False
        p1movingright = False
        p1rotateleft = False
        p1rotateright = False
        p1powerup = False
        p1powerdown = False

        # add yourself to the server
        if self.host: self.server.addPlayer(username, player1.getData())
        else: self.client.addPlayer(username, *player1.getData())

        self.playerInfo = {}
        self.projectileInfo = []
        # establish initial dictionary of previous users to compare to "downloaded" dictionary of users
        self.prevPlayerInfo = {username: {index:value for index,value in enumerate(player1.getData())}}
        self.prevProjectileInfo = []

        self.dataThread = threading.Thread(target=self.requestInfo, daemon=True)
        self.dataThread.start()

        running = True
        while running:
            # framerate limiter
            ticks = clock.tick_busy_loop(const["fps"])

            # get events which have occurred in a given frame
            for event in pygame.event.get():
                if   event.type == QUIT: running = False # red X button pressed
                elif event.type == KEYDOWN:
                    # if a key is pressed down, do the corresponding action to the player
                    if   event.key == K_ESCAPE: running = False
                    elif event.key == K_F1: DEBUG_INFO = not DEBUG_INFO
                    elif event.key == controls["p1powerup"]:       p1powerup = True
                    elif event.key == controls["p1powerdown"]:     p1powerdown = True
                    elif event.key == controls["p1anticlockwise"]: p1rotateleft = True
                    elif event.key == controls["p1clockwise"]:     p1rotateright = True
                    elif event.key == controls["p1left"]:          p1movingleft  = True
                    elif event.key == controls["p1right"]:         p1movingright = True
                    elif event.key == controls["p1shoot"] and player1.isAlive(): 
                        projectile = player1.shoot()
                        # add the projectile to the server
                        if self.host: self.server.addProjectile(projectile.getData())
                        else: self.client.addProjectile(*projectile.getData())
                        # appending the projectile data prevents the projectile being initialised twice on client computers
                        self.prevProjectileInfo.append(projectile.getData())
                elif event.type == KEYUP:
                    # if a key is released, stop doing the corresponding action to the player
                    if   event.key == controls["p1powerup"]:       p1powerup = False
                    elif event.key == controls["p1powerdown"]:     p1powerdown = False
                    elif event.key == controls["p1anticlockwise"]: p1rotateleft = False
                    elif event.key == controls["p1clockwise"]:     p1rotateright = False
                    elif event.key == controls["p1left"]:          p1movingleft  = False
                    elif event.key == controls["p1right"]:         p1movingright = False
            
            # execute relevant actions to the player
            if p1movingleft:  player1.move(-const["vel"], ground)
            if p1movingright: player1.move(const["vel"], ground)
            if p1rotateleft:  player1.barrel.rotate(-1)
            if p1rotateright: player1.barrel.rotate(1)
            if p1powerup:     player1.barrel.changepower(1)
            if p1powerdown:   player1.barrel.changepower(-1)

            # send new/updated player data to the server
            if self.host: self.server.sendPlayerData(username, player1.getData())
            else:    self.client.sendPlayerData(username, *player1.getData())

            screen.fill(black)

            # update and draw projectiles
            for projectile in projectiles: 
                projectile.update(ground, tankg)
                projectile.draw(screen)
            
            ground.draw(screen)

            # update and draw tanks
            for tank in tankg: 
                if tank != player1:
                    tank.setData(list(self.playerInfo[tank.getName()].values()))
                tank.update(ground)
                if SHOW_HITBOXES: pygame.draw.polygon(screen, (255,255,255), (tank.rect.topleft, tank.rect.topright, tank.rect.bottomright, tank.rect.bottomleft), 1)
                tank.draw(screen)

            # update and draw explosions
            for explosion in explosions:
                explosion.decay(ticks)
                explosion.draw(screen)

            if DEBUG_INFO:
                screen.blit(*render(font, f"FPS: {clock.get_fps()}", (0,0)))
                # screen.blit(*render(font, f"Angle: {player1.barrel.angle}", (0,15)))
                # screen.blit(*render(font, f"Power: {player1.barrel.power}", (0,30)))

            pygame.display.flip()
        tankg.clear()


def game(screen: pygame.Surface, controls, localMultiplayer=False, lanMultiplayer=False):

    DEBUG_INFO = False
    SHOW_HITBOXES = False

    font = pygame.font.SysFont("ebrima", 15, True)
    clock = pygame.time.Clock()

    groundheight = const["screenheight"]//6

    player1 = Tank(const["screenwidth"]//4, const["screenheight"]-groundheight, enemy=False)
    if localMultiplayer:
        player2 = Tank(3*(const["screenwidth"]//4), const["screenheight"]-groundheight, enemy=True)
    
    p1movingleft = False
    p1movingright = False
    p1rotateleft = False
    p1rotateright = False
    p1powerup = False
    p1powerdown = False

    p2movingleft = False
    p2movingright = False
    p2rotateleft = False
    p2rotateright = False
    p2powerup = False
    p2powerdown = False

    ground = generate_ground(groundheight, "longFunc")

    running = True
    while running:
        ticks = clock.tick_busy_loop(const["fps"])

        for event in pygame.event.get():
            if   event.type == QUIT: running = False
            elif event.type == KEYDOWN:
                if   event.key == K_ESCAPE: running = False
                elif event.key == K_F1: DEBUG_INFO = not DEBUG_INFO
                elif event.key == controls["p1powerup"]:       p1powerup = True
                elif event.key == controls["p1powerdown"]:     p1powerdown = True
                elif event.key == controls["p1anticlockwise"]: p1rotateleft = True
                elif event.key == controls["p1clockwise"]:     p1rotateright = True
                elif event.key == controls["p1left"]:          p1movingleft  = True
                elif event.key == controls["p1right"]:         p1movingright = True
                elif event.key == controls["p1shoot"] and player1.isAlive(): player1.shoot()
                if localMultiplayer:
                    if   event.key == controls["p2powerup"]:       p2powerup = True
                    elif event.key == controls["p2powerdown"]:     p2powerdown = True
                    elif event.key == controls["p2anticlockwise"]: p2rotateleft = True
                    elif event.key == controls["p2clockwise"]:     p2rotateright = True
                    elif event.key == controls["p2left"]:          p2movingleft  = True
                    elif event.key == controls["p2right"]:         p2movingright = True
                    elif event.key == controls["p2shoot"] and player2.isAlive(): player2.shoot()
            elif event.type == KEYUP:
                if   event.key == controls["p1powerup"]:       p1powerup = False
                elif event.key == controls["p1powerdown"]:     p1powerdown = False
                elif event.key == controls["p1anticlockwise"]: p1rotateleft = False
                elif event.key == controls["p1clockwise"]:     p1rotateright = False
                elif event.key == controls["p1left"]:          p1movingleft  = False
                elif event.key == controls["p1right"]:         p1movingright = False
                if localMultiplayer:
                    if   event.key == controls["p2powerup"]:       p2powerup = False
                    elif event.key == controls["p2powerdown"]:     p2powerdown = False
                    elif event.key == controls["p2anticlockwise"]: p2rotateleft = False
                    elif event.key == controls["p2clockwise"]:     p2rotateright = False
                    elif event.key == controls["p2left"]:          p2movingleft  = False
                    elif event.key == controls["p2right"]:         p2movingright = False
        
        if p1movingleft:  player1.move(-const["vel"], ground)
        if p1movingright: player1.move(const["vel"], ground)
        if p1rotateleft:  player1.barrel.rotate(-1)
        if p1rotateright: player1.barrel.rotate(1)
        if p1powerup:     player1.barrel.changepower(1)
        if p1powerdown:   player1.barrel.changepower(-1)

        if p2movingleft:  player2.move(-const["vel"], ground)
        if p2movingright: player2.move(const["vel"], ground)
        if p2rotateleft:  player2.barrel.rotate(-1)
        if p2rotateright: player2.barrel.rotate(1)
        if p2powerup:     player2.barrel.changepower(1)
        if p2powerdown:   player2.barrel.changepower(-1)

        screen.fill(black)
        for projectile in projectiles: 
            projectile.update(ground, tankg)
            projectile.draw(screen)
        
        ground.draw(screen)

        for tank in tankg: 
            tank.update(ground)
            if SHOW_HITBOXES: pygame.draw.polygon(screen, (255,255,255), (tank.rect.topleft, tank.rect.topright, tank.rect.bottomright, tank.rect.bottomleft), 1)
            tank.draw(screen)

        for explosion in explosions:
            explosion.decay(ticks)
            explosion.draw(screen)

        if DEBUG_INFO:
            screen.blit(*render(font, f"FPS: {clock.get_fps()}", (0,0)))
            # screen.blit(*render(font, f"Angle: {tank.barrel.angle}", (0,15)))
            # screen.blit(*render(font, f"Power: {tank.barrel.power}", (0,30)))

        pygame.display.flip()
    tankg.clear()


def render(font, text: str, loc: tuple):
    """Renders text to a surface and returns the text surface and text rect
    Usage: screen.blit(*render(font, "Hello World!", (0,0)))"""
    textsurf = font.render(text, True, white)
    textrect = textsurf.get_rect(topleft=loc)
    return textsurf, textrect


# def LANgame(screen: pygame.Surface, controls, data):
#     username, ip, host = data
#     DEBUG_INFO = False
#     SHOW_HITBOXES = False

#     playerInfo = {}
#     if host:
#         # if host, start the server
#         server = Server(8000)
#         serverThread = threading.Thread(target=server.start, daemon=True)
#         serverThread.start()  # start server in a separate thread to prevent hanging
#     else: client = Client(ip, 8000) # if not host, start the client

#     font = pygame.font.SysFont("ebrima", 15, True)
#     clock = pygame.time.Clock()
#     groundheight = const["screenheight"]//6
#     ground = generate_ground(groundheight, "longFunc")

#     player1 = Tank(random.randrange(50, const["screenwidth"]-50), const["screenheight"]-groundheight, enemy=False, name=username)
#     p1movingleft = False
#     p1movingright = False
#     p1rotateleft = False
#     p1rotateright = False
#     p1powerup = False
#     p1powerdown = False

#     # add yourself to the server
#     if host: server.addPlayer(username, player1.getData())
#     else: client.addPlayer(username, *player1.getData())

#     # establish initial dictionary of previous users to compare to "downloaded" dictionary of users
#     prevPlayerInfo = {username: {index:value for index,value in enumerate(player1.getData())}}
#     prevProjectileInfo = []

#     running = True
#     while running:
#         # framerate limiter
#         ticks = clock.tick_busy_loop(const["fps"])
        
#         # get the new dictionary of players from the server
#         if host: 
#             playerInfo = server.getPlayerData()
#             projectileInfo = server.getProjectileData()
#         else: 
#             playerInfo = eval(client.getPlayerData())
#             projectileInfo = eval(client.getProjectileData()) # possibly integrate this into the playerInfo funcs to be all in one

#         # if the dictionary of players has changed, add the new players to the game
#         if len(playerInfo) > len(prevPlayerInfo):
#             prevPlayerInfoKeys = list(prevPlayerInfo.keys())
#             playerInfoKeys = list(playerInfo.keys())
#             for key in playerInfoKeys:
#                 if key not in prevPlayerInfoKeys:
#                     Tank(*list(playerInfo[key].values()), enemy=True, name=key)
#             prevPlayerInfo = playerInfo
        
#         # if the list of projectiles has changed, add the new projectiles to the game
#         if len(projectileInfo) > len(prevProjectileInfo):
#             newProjectileData = projectileInfo[len(prevProjectileInfo):]
#             for projectile in newProjectileData:
#                 Projectile(*projectile)
#             prevProjectileInfo = projectileInfo

#         # get events which have occurred in a given frame
#         for event in pygame.event.get():
#             if   event.type == QUIT: running = False # red X button pressed
#             elif event.type == KEYDOWN:
#                 # if a key is pressed down, do the corresponding action to the player
#                 if   event.key == K_ESCAPE: running = False
#                 elif event.key == K_F1: DEBUG_INFO = not DEBUG_INFO
#                 elif event.key == controls["p1powerup"]:       p1powerup = True
#                 elif event.key == controls["p1powerdown"]:     p1powerdown = True
#                 elif event.key == controls["p1anticlockwise"]: p1rotateleft = True
#                 elif event.key == controls["p1clockwise"]:     p1rotateright = True
#                 elif event.key == controls["p1left"]:          p1movingleft  = True
#                 elif event.key == controls["p1right"]:         p1movingright = True
#                 elif event.key == controls["p1shoot"] and player1.isAlive(): 
#                     projectile = player1.shoot()
#                     # add the projectile to the server
#                     if host: server.addProjectile(projectile.getData())
#                     else: 
#                         client.addProjectile(*projectile.getData())
#                         # appending the projectile data prevents the projectile being initialised twice on client computers
#                         projectileInfo.append(projectile.getData())
#             elif event.type == KEYUP:
#                 # if a key is released, stop doing the corresponding action to the player
#                 if   event.key == controls["p1powerup"]:       p1powerup = False
#                 elif event.key == controls["p1powerdown"]:     p1powerdown = False
#                 elif event.key == controls["p1anticlockwise"]: p1rotateleft = False
#                 elif event.key == controls["p1clockwise"]:     p1rotateright = False
#                 elif event.key == controls["p1left"]:          p1movingleft  = False
#                 elif event.key == controls["p1right"]:         p1movingright = False
        
#         # execute relevant actions to the player
#         if p1movingleft:  player1.move(-const["vel"], ground)
#         if p1movingright: player1.move(const["vel"], ground)
#         if p1rotateleft:  player1.barrel.rotate(-1)
#         if p1rotateright: player1.barrel.rotate(1)
#         if p1powerup:     player1.barrel.changepower(1)
#         if p1powerdown:   player1.barrel.changepower(-1)

#         # send new/updated player data to the server
#         if host: server.sendPlayerData(username, player1.getData())
#         else:    client.sendPlayerData(username, *player1.getData())

#         screen.fill(black)

#         # update and draw projectiles
#         for projectile in projectiles: 
#             projectile.update(ground, tankg)
#             projectile.draw(screen)
        
#         ground.draw(screen)

#         # update and draw tanks
#         for tank in tankg: 
#             if tank != player1:
#                 tank.setData(list(playerInfo[tank.getName()].values()))
#             tank.update(ground)
#             if SHOW_HITBOXES: pygame.draw.polygon(screen, (255,255,255), (tank.rect.topleft, tank.rect.topright, tank.rect.bottomright, tank.rect.bottomleft), 1)
#             tank.draw(screen)

#         # update and draw explosions
#         for explosion in explosions:
#             explosion.decay(ticks)
#             explosion.draw(screen)

#         if DEBUG_INFO:
#             screen.blit(*render(font, f"FPS: {clock.get_fps()}", (0,0)))
#             # screen.blit(*render(font, f"Angle: {player1.barrel.angle}", (0,15)))
#             # screen.blit(*render(font, f"Power: {player1.barrel.power}", (0,30)))

#         pygame.display.flip()
#     tankg.clear()
#     # if host: server.stop()
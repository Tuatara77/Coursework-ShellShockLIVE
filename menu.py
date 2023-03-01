import json
import controls
from colours import *
from keychars import *
from client import Client
from server import Server
from types import FunctionType
from pygame.locals import QUIT, K_ESCAPE, KEYDOWN, KEYUP, MOUSEMOTION, MOUSEBUTTONDOWN, K_LSHIFT, K_RSHIFT, K_CAPSLOCK
with open("constants.json", "r") as constants: const = json.load(constants)

from game import game, LANGame


class MenuComponent(pygame.Surface): # inheriting from pygame.Surface, which is inherently better than pygame.sprite.Sprite for this use case
    def __init__(self, x:int, y:int, width:int, height:int, group:list, bgcolour:tuple=white, text:str="", 
                 textsize:int=15, textcolour:tuple=black, referencePoint:str="centre", font:str="ebrima"):
        super().__init__((width, height)) # initialising the component surface
        group.append(self)       # add component to list of components

        self.type = None               # the base class has no type
        self.bgcolour = bgcolour       # the background colour of the component
        self.normalbgcolour = bgcolour # the normal background colour of the component
        self.text = text               # the text contained within the component
        self.textsize = textsize       # the size of the text
        self.textcolour = textcolour   # the colour of the text

        if font[-4:] == ".ttf": self.font = pygame.font.Font(font, textsize); self.font.set_bold(True)
        else: self.font = pygame.font.SysFont(font, textsize, bold=True) # initialise text font
        self.fill(self.bgcolour) # fill the background of the component
        self.textRender() # render the text onto the component surface
        
        self.rect = self.get_rect()
        reference = { # dictionary to set the coordinates of the component according to the reference point
                "centre": self.centre,
                "topleft": self.topleft,
                "topright": self.topright,
                "bottomleft": self.bottomleft,
                "bottomright": self.bottomright,
                "centretop": self.centretop,
                "midtop": self.centretop,
                "centrebottom": self.centrebottom,
                "midbottom": self.centrebottom,
                "centreleft": self.centreleft,
                "midleft": self.centreleft,
                "centreright": self.centreright,
                "midright": self.centreright
        }
        reference[referencePoint](x,y) # set the rect coordinates of the component according to the reference point
    
    # these functions do what you'd expect
    def centre(self,x,y): self.rect.center = (x,y)           # sets the centre of the component to the coordinates
    def topleft(self,x,y): self.rect.topleft = (x,y)         # sets the top left of the component to the coordinates
    def topright(self,x,y): self.rect.topright = (x,y)       # sets the top right of the component to the coordinates
    def bottomleft(self,x,y): self.rect.bottomleft = (x,y)   # sets the bottom left of the component to the coordinates
    def bottomright(self,x,y): self.rect.bottomright = (x,y) # sets the bottom right of the component to the coordinates
    def centretop(self,x,y): self.rect.midtop = (x,y)        # sets the top centre of the component to the coordinates
    def centrebottom(self,x,y): self.rect.midbottom = (x,y)  # sets the bottom centre of the component to the coordinates
    def centreleft(self,x,y): self.rect.midleft = (x,y)      # sets the left centre of the component to the coordinates
    def centreright(self,x,y): self.rect.midright = (x,y)    # sets the right centre of the component to the coordinates

    def getType(self): return self.type # returns the component's type
    def getRect(self): return self.rect # returns the component's rect

    def textRender(self): # this renders the text onto the component's surface in an editable 
        self.fill(self.bgcolour) # fill the background of the component
        componentSize = self.get_size() # gets the dimensions of the component surface
        textsurf = self.font.render(self.text, True, self.textcolour) # creates a surface of the text
        self.blit(textsurf, # draws the text surface onto the component surface
                  textsurf.get_rect(center=((componentSize[0]//2)-1, 
                                            (componentSize[1]//2)-1) # -1 to centre it. it seems to work for all sizes...
                                    ))


class Text(MenuComponent):   # self explanatory - a text component
    def __init__(self, x:int, y:int, width:int, height:int, group:list, text:str, bgcolour:tuple=black,
                 textsize:int=15, textcolour:tuple=white, referencePoint:str="centre", font:str="ebrima"):
        super().__init__(x,y,width,height,group,bgcolour,text,textsize,textcolour,referencePoint,font)
        self.type = "text"


class Button(MenuComponent):
    def __init__(self, x:int, y:int, width:int, height:int, group:list, reactiveGroup:list, 
                 bgcolour:tuple=white, hoverbgcolour:tuple=light_grey, text:str="", textsize:int=15, 
                 textcolour:tuple=black, referencePoint:str="centre", font:str="ebrima"):
        super().__init__(x,y,width,height,group,bgcolour,text,  # initialises the component
                         textsize,textcolour,referencePoint,font)
        self.hoverbgcolour = hoverbgcolour # the component background colour when hovered over by the mouse
        self.type = "button"
        self.isHover = False
        self.function = lambda: None # if bind function is not called, the default function is None (does nothing)
        reactiveGroup.append(self) # add the button to the list of reactive components
    
    def hover(self, val): 
        if not val == self.isHover:  # if the hover state is different to the previous frame
            self.isHover = not not val # not not is the same as bool() but faster. ensures variable is either True or False
            if self.isHover: self.bgcolour = self.hoverbgcolour # if being hovered over, darken background colour
            else: self.bgcolour = self.normalbgcolour # if not being hovered, lighten background colour
            super().textRender() # re-render the text onto the button
    
    def bind(self, function, *args): # binds a function to be run when the button is pressed
        self.function = function
        self.args = args  # the arguments may be declared in the bind function if they are known and accessible at the time of binding

    def click(self, *args): # runs the function bound to the button
        if args and not self.args: self.function(*args) # if self.args has a value and *args does not, *args is used
        else: self.function(*self.args) # otherwise use the args declared in the bind function


class Entry(MenuComponent):
    def __init__(self, x:int, y:int, width:int, height:int, group:list, reactiveGroup:list, 
                 entryGroup:list, checkFunction=lambda _param:True, maxTextLength:int=None, 
                 bgcolour:tuple=red, focuscolour:tuple=dark_red, textsize:int=15, 
                 textcolour:tuple=black, referencePoint="centre", font="ebrima"):
                 # the checkFunction default parameter is a function which always returns True
        self.text = ""
        super().__init__(x,y,width,height,group,bgcolour,self.text,textsize,textcolour,referencePoint,font)
        self.type = "entry"
        self.focusbgcolour = focuscolour # extra attributes unspecified by the MenuComponent class
        self.maxTextLength = maxTextLength
        self.checkFunction = checkFunction
        self.isFocus = False
        self.isClicked = False
        self.data = None
        reactiveGroup.append(self)
        entryGroup.append(self)

    def getData(self): return self.text
    def getFocus(self): return self.isFocus    
    def getValid(self): return self.checkFunction(self.text)             
    def getClicked(self): return self.isClicked         
    def setClicked(self, val): 
        self.isClicked = not not val
        if not self.isClicked:
            if self.text and self.checkFunction(self.text): # and the input is valid...
                self.focus(False)
                self.bgcolour = light_green       # make background colour of the entry green
                # self.normalbgcolour = light_green # to indicate a valid input
                self.focusbgcolour = grass_green
            else:                      # if the input is invalid...
                self.bgcolour = red           # make the background colour of the entry red
                # self.normalbgcolour = red     # to indicate an invalid input
                self.focusbgcolour = dark_red

    def focus(self, val):
        if val != self.isFocus: # changing background colour if hovered or focused on
            self.isFocus = not not val
            if self.isFocus: self.bgcolour = self.focusbgcolour
            else:
                if self.text and self.checkFunction(self.text): # and the input is valid...
                    self.focus(False)
                    self.bgcolour = light_green      # make background colour of the entry green
                    self.focusbgcolour = grass_green # to indicate a valid input
                else:                      # if the input is invalid...
                    self.bgcolour = red           # make the background colour of the entry red
                    self.focusbgcolour = dark_red # to indicate an invalid input
            super().textRender() # re-render the text onto the entry

    def addLetter(self, char): # add character to the box
        if self.isClicked:
            if   char == "BSPCE": self.text = self.text[:-1] # if backspace, remove last character
            elif char == "RETURN": # if Enter is pressed...
                if self.checkFunction(self.text): # and the input is valid...
                    self.isClicked = False
                    self.focus(False)
                    self.bgcolour = light_green       # make background colour of the entry green
                    self.normalbgcolour = light_green # to indicate a valid input
                    self.focusbgcolour = grass_green
                else:                      # if the input is invalid...
                    self.bgcolour = red           # make the background colour of the entry red
                    self.normalbgcolour = red     # to indicate an invalid input
                    self.focusbgcolour = dark_red
            else: 
                # if the input is longer than the maximum length, do not add the character
                if self.maxTextLength != None and len(self.text) >= self.maxTextLength: return
                self.text += char # otherwise, add the character
            super().textRender() # re-render the text onto the entry


def validIP(ip:str):
    if ip.count(".") != 3: return False
    for i in ip.split("."): # for each number in the ip address
        if not i.isdigit(): return False # if the number is not a digit, return False
        if int(i) < 0 or int(i) > 255: return False # if the number is not between 0 and 255, return False
    return True


def entriesValid(function:FunctionType, params:tuple, entries:tuple[Entry], extraData=[]):
    entryData = []
    for entry in entries:
        if not entry.getValid(): return
        entryData.append(entry.getData())
    entryData.extend(extraData)
    function(*params, entryData)


def notImplemented(parentSurface, componentGroup, text=""):
    hsw = parentSurface.get_width()//2
    hsh = parentSurface.get_height()//2
    Text(10, 3*hsh/2, hsw//3, hsh//5, componentGroup, text, referencePoint="topleft")


def getDataFromEntries(entries:tuple[Entry], extraData:list=[]):
    for entry in entries:
        extraData.insert(0,entry.getData())
    return extraData


controlsMenuComponents = []
controlsMenuReactiveComponents = []
class ControlsMenu:
    def __init__(self, surface: pygame.Surface, extraData=[]):
        halfscreenwidth = surface.get_width()//2   # half-values to reduce function calls
        halfscreenheight = surface.get_height()//2 # and improve readibility

        controlsMenuComponents.clear()         # clear the lists of components
        controlsMenuReactiveComponents.clear()

        backButton = Button(halfscreenwidth,
                            13*(halfscreenheight//8),
                            halfscreenwidth//3,
                            halfscreenheight//10,
                            controlsMenuComponents,
                            controlsMenuReactiveComponents,
                            text="Back",
                            textsize = halfscreenheight//16)

        Text(halfscreenwidth,
             2*(halfscreenheight//15),
             halfscreenwidth,
             halfscreenheight//10,
             controlsMenuComponents,
             text="Controls",
             textsize=halfscreenheight//10)
        
        # Singleplayer/LAN Multiplayer controls
        
        Text(halfscreenwidth//2,
             5*(halfscreenheight//15),
             halfscreenwidth,
             halfscreenheight//10,
             controlsMenuComponents,
             text="Singleplayer / LAN Multiplayer:",
             textsize=halfscreenheight//18)

        Text(halfscreenwidth//2,
             7*(halfscreenheight//15),
             halfscreenwidth,
             halfscreenheight//10,
             controlsMenuComponents,
             text="   Left / Right                 -       A / D             ")
        
        Text(halfscreenwidth//2,
             8*(halfscreenheight//15),
             halfscreenwidth,
             halfscreenheight//10,
             controlsMenuComponents,
             text="   Increase / Decrease power     -    Up / Down arrow-keys")
        
        Text(halfscreenwidth//2,
             9*(halfscreenheight//15),
             halfscreenwidth,
             halfscreenheight//10,
             controlsMenuComponents,
             text="Rotate barrel anti / clockwise  -  Left / Right arrow-keys")
        
        Text(halfscreenwidth//2,
             10*(halfscreenheight//15),
             halfscreenwidth,
             halfscreenheight//10,
             controlsMenuComponents,
             text="Shoot                      -       Space     ")

        # Local Multiplayer controls

        Text(3*(halfscreenwidth//2),
             5*(halfscreenheight//15),
             halfscreenwidth,
             halfscreenheight//10,
             controlsMenuComponents,
             text="Local Multiplayer:",
             textsize=halfscreenheight//18)

        Text(3*(halfscreenwidth//2),
             7*(halfscreenheight//15),
             halfscreenwidth,
             halfscreenheight//10,
             controlsMenuComponents,
             text="           Left/Right                    -     Player 1: A / D  |  Player 2: J / L")
        
        Text(3*(halfscreenwidth//2),
             8*(halfscreenheight//15),
             halfscreenwidth,
             halfscreenheight//10,
             controlsMenuComponents,
             text="Increase/Decrease power      -     Player 1: W / S  |  Player 2: I / K")
        
        Text(3*(halfscreenwidth//2),
             9*(halfscreenheight//15),
             halfscreenwidth,
             halfscreenheight//10,
             controlsMenuComponents,
             text="Rotate barrel anti/clockwise   -     Player 1: Q / E   |  Player 2: U / O")
        
        Text(3*(halfscreenwidth//2),
             10*(halfscreenheight//15),
             halfscreenwidth,
             halfscreenheight//10,
             controlsMenuComponents,
             text="             Shoot                         -     Player 1:    X      |  Player 2:   M")

        backButton.bind(mainMenu, surface) # TODO: fix to make running = False



userInfoMenuComponents = []
userInfoMenuReactiveComponents = []
userInfoMenuEntries = []
class UserInfoMenu:
    def __init__(self, surface: pygame.Surface, extraData=[]):
        halfscreenwidth = surface.get_width()//2
        halfscreenheight = surface.get_height()//2

        userInfoMenuComponents.clear()
        userInfoMenuReactiveComponents.clear()
        userInfoMenuEntries.clear()

        Text(halfscreenwidth,
             2*(halfscreenheight//5),
             halfscreenwidth,
             halfscreenheight//5,
             userInfoMenuComponents,
             text="Input a username",
             textsize=halfscreenheight//16)
        
        usernameEntry = Entry(halfscreenwidth,
                                   9*halfscreenheight//16,
                                   halfscreenwidth,
                                   halfscreenheight//10,
                                   userInfoMenuComponents,
                                   userInfoMenuReactiveComponents,
                                   userInfoMenuEntries,
                                   maxTextLength=32)

        continueButton = Button(halfscreenwidth,
                                12*(halfscreenheight//8),
                                halfscreenwidth//3,
                                halfscreenheight//10,
                                userInfoMenuComponents,
                                userInfoMenuReactiveComponents,
                                text="Continue",
                                textsize = halfscreenheight//16)
        
        backButton = Button(halfscreenwidth,
                            13*(halfscreenheight//8),
                            halfscreenwidth//3,
                            halfscreenheight//10,
                            userInfoMenuComponents,
                            userInfoMenuReactiveComponents,
                            text="Back",
                            textsize = halfscreenheight//16)

        continueButton.bind(entriesValid,
                            LANGame,
                            (surface,
                             controls.singlePlayerControls),
                            userInfoMenuEntries,
                            extraData)
        backButton.bind(mainMenu, surface)


getIPMenuComponents = []
getIPMenuReactiveComponents = []
getIPMenuEntries = []
class GetIPMenu:
    def __init__(self, surface: pygame.Surface, extraData=[]):
        halfscreenwidth = surface.get_width()//2
        halfscreenheight = surface.get_height()//2

        getIPMenuComponents.clear()
        getIPMenuReactiveComponents.clear()
        getIPMenuEntries.clear()

        Text(halfscreenwidth,
             halfscreenheight,
             halfscreenwidth,
             halfscreenheight//5,
             getIPMenuComponents,
             text="Input the host's IP address",
             textsize=halfscreenheight//16)
        
        ipEntry = Entry(halfscreenwidth,
                             9*(halfscreenheight//8),
                             halfscreenwidth,
                             halfscreenheight//10,
                             getIPMenuComponents,
                             getIPMenuReactiveComponents,
                             getIPMenuEntries,
                             checkFunction=validIP,
                             maxTextLength=16)
        
        continueButton = Button(halfscreenwidth,
                                12*(halfscreenheight//8),
                                halfscreenwidth//3,
                                halfscreenheight//10,
                                getIPMenuComponents,
                                getIPMenuReactiveComponents,
                                text="Continue",
                                textsize = halfscreenheight//16)
        
        backButton = Button(halfscreenwidth,
                            13*(halfscreenheight//8),
                            halfscreenwidth//3,
                            halfscreenheight//10,
                            getIPMenuComponents,
                            getIPMenuReactiveComponents,
                            text="Back",
                            textsize = halfscreenheight//16)

        continueButton.bind(entriesValid,
                            menu,
                            [surface,
                             UserInfoMenu,
                             userInfoMenuComponents,
                             userInfoMenuReactiveComponents,
                             userInfoMenuEntries],
                            getIPMenuEntries,
                            extraData)
        backButton.bind(mainMenu, surface)


hostDecisionMenuComponents = []
hostDecisionMenuReactiveComponents = []
class HostDecisionMenu:
    def __init__(self, surface: pygame.Surface, extraData=[]):
        halfscreenwidth = surface.get_width()//2
        halfscreenheight = surface.get_height()//2

        hostDecisionMenuComponents.clear()
        hostDecisionMenuReactiveComponents.clear()

        Text(halfscreenwidth,
                2*(halfscreenheight//5),
                2*halfscreenwidth,
                halfscreenheight//5,
                hostDecisionMenuComponents,
                text="Host or join a game?",
                textsize=halfscreenheight//10)
        
        hostButton = Button(3*(halfscreenwidth//4),
                            halfscreenheight,
                            halfscreenwidth//4,
                            halfscreenheight//8,
                            hostDecisionMenuComponents,
                            hostDecisionMenuReactiveComponents,
                            text="Host")
        
        joinButton = Button(5*(halfscreenwidth//4),
                            halfscreenheight,
                            halfscreenwidth//4,
                            halfscreenheight//8,
                            hostDecisionMenuComponents,
                            hostDecisionMenuReactiveComponents,
                            text="Join")
        
        backButton = Button(halfscreenwidth,
                            13*(halfscreenheight//8),
                            halfscreenwidth//3,
                            halfscreenheight//10,
                            hostDecisionMenuComponents,
                            hostDecisionMenuReactiveComponents,
                            text="Back")
        
        hostButton.bind(menu, surface,
                        UserInfoMenu,
                        userInfoMenuComponents,
                        userInfoMenuReactiveComponents,
                        userInfoMenuEntries,
                        ["127.0.0.1", True])
        joinButton.bind(menu, surface,
                        GetIPMenu,
                        getIPMenuComponents,
                        getIPMenuReactiveComponents,
                        getIPMenuEntries,
                        [False])
        backButton.bind(mainMenu, surface)


multiplayerDecisionMenuComponents = []
multiplayerDecisionMenuReactiveComponents = []
class MultiplayerDecisionMenu:
    def __init__(self, surface: pygame.Surface, extraData=[]):
        halfscreenwidth = surface.get_width()//2
        halfscreenheight = surface.get_height()//2

        multiplayerDecisionMenuComponents.clear()
        multiplayerDecisionMenuReactiveComponents.clear()

        Text(halfscreenwidth,
             2*(halfscreenheight//5),
             2*halfscreenwidth,
             halfscreenheight//5,
             multiplayerDecisionMenuComponents,
             text="Choose a multiplayer mode",
             textsize=halfscreenheight//10)
        
        localMultiplayerButton = Button(3*(halfscreenwidth//4),
                                        halfscreenheight,
                                        halfscreenwidth//4,
                                        halfscreenheight//8,
                                        multiplayerDecisionMenuComponents,
                                        multiplayerDecisionMenuReactiveComponents,
                                        text="Local Multiplayer")
        
        lanMultiplayerButton = Button(5*(halfscreenwidth//4),
                                      halfscreenheight,
                                      halfscreenwidth//4,
                                      halfscreenheight//8,
                                      multiplayerDecisionMenuComponents,
                                      multiplayerDecisionMenuReactiveComponents,
                                      text="LAN Multiplayer")

        backButton = Button(halfscreenwidth,
                            13*(halfscreenheight//8),
                            halfscreenwidth//3,
                            halfscreenheight//10,
                            multiplayerDecisionMenuComponents,
                            multiplayerDecisionMenuReactiveComponents,
                            text="Back")
        
        localMultiplayerButton.bind(game, surface, controls.multiPlayerControls, True) # True = local multiplayer
        lanMultiplayerButton.bind(menu, surface,
                                  HostDecisionMenu,
                                  hostDecisionMenuComponents,
                                  hostDecisionMenuReactiveComponents)
        backButton.bind(mainMenu, surface)


mainMenuComponents = [] 
mainMenuReactiveComponents = []
class MainMenu:
    def __init__(self, surface: pygame.Surface, extraData=[]):
        halfscreenwidth = surface.get_width()//2   # declare variables for half the screen width and height
        halfscreenheight = surface.get_height()//2 # to reduce function calls

        mainMenuComponents.clear()          # clear the lists of components
        mainMenuReactiveComponents.clear()

        Text(halfscreenwidth,     # Title text
             halfscreenheight//5,
             halfscreenwidth,
             halfscreenheight//5,
             mainMenuComponents,
             text="ShellShock",
             textsize=halfscreenheight//5)
        
        singlePlayerButton = Button(halfscreenwidth,          # initialise the singleplayer button
                                    halfscreenheight-halfscreenheight//4,
                                    halfscreenwidth//3,
                                    halfscreenheight//8,
                                    mainMenuComponents,
                                    mainMenuReactiveComponents,
                                    text="SinglePlayer",
                                    textsize = halfscreenheight//20)

        multiPlayerButton = Button(halfscreenwidth,           # initialise the multiplayer button
                                   halfscreenheight,
                                   halfscreenwidth//3,
                                   halfscreenheight//8,
                                   mainMenuComponents,
                                   mainMenuReactiveComponents,
                                   text="MultiPlayer",
                                   textsize = halfscreenheight//20)

        controlsButton = Button(halfscreenwidth,              # initialise the settings button
                                halfscreenheight+halfscreenheight//4,
                                halfscreenwidth//3,
                                halfscreenheight//8,
                                mainMenuComponents,
                                mainMenuReactiveComponents,
                                text="Controls",
                                textsize = halfscreenheight//20)
        
        exitButton = Button(halfscreenwidth,                  # initialise the exit button
                            3*(halfscreenheight//2),
                            halfscreenwidth//3,
                            halfscreenheight//8,
                            mainMenuComponents,
                            mainMenuReactiveComponents,
                            text="Exit",
                            textsize = halfscreenheight//20)

        singlePlayerButton.bind(game, surface, controls.singlePlayerControls)
        multiPlayerButton.bind(menu, surface, 
                               MultiplayerDecisionMenu, 
                               multiplayerDecisionMenuComponents,
                               multiplayerDecisionMenuReactiveComponents)
        controlsButton.bind(menu, surface,
                            ControlsMenu,
                            controlsMenuComponents,
                            controlsMenuReactiveComponents)
        exitButton.bind(exit)


def menu(screen:pygame.Surface, MenuClass, allComponents, reactiveComponents, entryComponents=[], extraData=[]):
    clock = pygame.time.Clock()
    MenuClass(screen, extraData)

    shift = False
    capslock = False

    running = True
    while running:
        clock.tick(const["fps"])

        for event in pygame.event.get():
            if   event.type == QUIT: running = False
            elif event.type == KEYDOWN:
                if   event.key == K_ESCAPE: running = False
                elif event.key == K_LSHIFT or event.key == K_RSHIFT: shift = True
                elif event.key == K_CAPSLOCK: capslock = not capslock

                if shift and not capslock or not shift and capslock: # XOR between shift and capslock to match reality
                    if event.key in uppercase:
                        for entry in entryComponents:
                            entry.addLetter(uppercase[event.key])
                else:
                    if event.key in lowercase:
                        for entry in entryComponents:
                            entry.addLetter(lowercase[event.key])
            
            elif event.type == KEYUP:
                if event.key == K_LSHIFT or event.key == K_RSHIFT: shift = False
            
            elif event.type == MOUSEMOTION:    # check for hover on reactive components
                for item in reactiveComponents:
                    if item.getRect().collidepoint(pygame.mouse.get_pos()):
                        if item.getType() == "button": item.hover(True)
                        elif item.getType() == "entry": item.focus(True)
                    else:
                        if item.getType() == "button": item.hover(False)
                        elif item.getType() == "entry":
                            if not item.getClicked(): item.focus(False)

            elif event.type == MOUSEBUTTONDOWN:  # check for clicks on reactive components
                for item in reactiveComponents:
                    if item.getRect().collidepoint(pygame.mouse.get_pos()):
                        if item.getType() == "button": 
                            item.click()
                            break
                        elif item.getType() == "entry": 
                            item.focus(True)
                            item.setClicked(True)
                    else:
                        if item.getType() == "entry": 
                            item.focus(False)
                            item.setClicked(False)
        
        screen.fill(black)
        for component in allComponents: screen.blit(component, component.getRect())
        pygame.display.flip()


def mainMenu(screen: pygame.Surface):
    clock = pygame.time.Clock()
    MainMenu(screen)

    running = True
    while running: 
        clock.tick(const["fps"])

        for event in pygame.event.get():
            if event.type == QUIT: running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE: running = False
            
            elif event.type == MOUSEMOTION:    # check for hover on reactive components
                for item in mainMenuReactiveComponents:
                    if item.getRect().collidepoint(pygame.mouse.get_pos()):
                        if item.getType() == "button": item.hover(True)
                        elif item.getType() == "entry": item.focus(True)
                    else:
                        if item.getType() == "button": item.hover(False)
                        elif item.getType() == "entry":
                            if not item.getClicked(): item.focus(False)
            
            elif event.type == MOUSEBUTTONDOWN:  # check for clicks on reactive components
                for item in mainMenuReactiveComponents:
                    if item.getRect().collidepoint(pygame.mouse.get_pos()):
                        if item.getType() == "button": 
                            item.click()
                            break
                        elif item.getType() == "entry": 
                            item.focus(True)
                            item.setClicked(True)
                    else:
                        if item.getType() == "entry": 
                            item.focus(False)
                            item.setClicked(False)

        screen.fill(black)
        for component in mainMenuComponents: screen.blit(component, component.getRect())
        pygame.display.flip()







# lanLobbyMenuComponents = []
# lanLobbyMenuReactiveComponents = []
# class LANLobbyMenu:
#     def __init__(self, surface: pygame.Surface, extraData=[]):
#         halfscreenwidth = surface.get_width()//2
#         halfscreenheight = surface.get_height()//2

#         lanLobbyMenuComponents.clear()
#         lanLobbyMenuReactiveComponents.clear()

#         Text(halfscreenwidth,
#              2*(halfscreenheight//5),
#              halfscreenwidth,
#              halfscreenheight//5,
#              lanLobbyMenuComponents,
#              text="Waiting for other players",
#              textsize=halfscreenheight//16)
        
#         backButton = Button(halfscreenwidth,
#                             13*(halfscreenheight//8),
#                             halfscreenwidth//3,
#                             halfscreenheight//10,
#                             lanLobbyMenuComponents,
#                             lanLobbyMenuReactiveComponents,
#                             text="Back",
#                             textsize = halfscreenheight//16)

#         backButton.bind(mainMenu, surface)


# def controlsMenu(screen: pygame.Surface):
#     clock = pygame.time.Clock()
#     ControlsMenu(screen)

#     running = True
#     while running: 
#         clock.tick(const["fps"])

#         for event in pygame.event.get():
#             if   event.type == QUIT: running = False
#             elif event.type == KEYDOWN:
#                 if   event.key == K_ESCAPE: running = False
            
#             elif event.type == KEYUP:
#                 if event.key == K_LSHIFT or event.key == K_RSHIFT: shift = False
            
#             elif event.type == MOUSEMOTION:    # check for hover on reactive components
#                 for item in controlsMenuReactiveComponents:
#                     if item.getRect().collidepoint(pygame.mouse.get_pos()):
#                         if item.getType() == "button": item.hover(True)
#                     else:
#                         if item.getType() == "button": item.hover(False)

#             elif event.type == MOUSEBUTTONDOWN:  # check for clicks on reactive components
#                 for item in controlsMenuReactiveComponents:
#                     if item.getRect().collidepoint(pygame.mouse.get_pos()):
#                         if item.getType() == "button": 
#                             item.click()
#                             break

#         screen.fill(black)
#         for component in controlsMenuComponents: screen.blit(component, component.getRect())
#         pygame.display.flip()


# def multiplayerDecisionMenu(screen: pygame.Surface):
#     clock = pygame.time.Clock()
#     MultiplayerDecisionMenu(screen)

#     running = True
#     while running: 
#         clock.tick(const["fps"])

#         for event in pygame.event.get():
#             if   event.type == QUIT: running = False
#             elif event.type == KEYDOWN:
#                 if   event.key == K_ESCAPE: running = False
            
#             elif event.type == KEYUP:
#                 if event.key == K_LSHIFT or event.key == K_RSHIFT: shift = False
            
#             elif event.type == MOUSEMOTION:    # check for hover on reactive components
#                 for item in multiplayerDecisionMenuReactiveComponents:
#                     if item.getRect().collidepoint(pygame.mouse.get_pos()):
#                         if item.getType() == "button": item.hover(True)
#                     else:
#                         if item.getType() == "button": item.hover(False)

#             elif event.type == MOUSEBUTTONDOWN:  # check for clicks on reactive components
#                 for item in multiplayerDecisionMenuReactiveComponents:
#                     if item.getRect().collidepoint(pygame.mouse.get_pos()):
#                         if item.getType() == "button": 
#                             item.click()
#                             break

#         screen.fill(black)
#         for component in multiplayerDecisionMenuComponents: screen.blit(component, component.getRect())
#         pygame.display.flip()


# def userInfoInputMenu(screen: pygame.Surface):
#     clock = pygame.time.Clock()
#     UserInfoInputMenu(screen)

#     shift = False
#     capslock = False

#     running = True
#     while running:
#         clock.tick(const["fps"])

#         for event in pygame.event.get():
#             if   event.type == QUIT: running = False
#             elif event.type == KEYDOWN:
#                 if   event.key == K_ESCAPE: running = False
#                 elif event.key == K_LSHIFT or event.key == K_RSHIFT: shift = True
#                 elif event.key == K_CAPSLOCK: capslock = not capslock

#                 if shift and not capslock or not shift and capslock: # XOR between shift and capslock to match reality
#                     if event.key in uppercase:
#                         for entry in userInfoMenuEntries:
#                             entry.addLetter(uppercase[event.key])
#                 else:
#                     if event.key in lowercase:
#                         for entry in userInfoMenuEntries:
#                             entry.addLetter(lowercase[event.key])
            
#             elif event.type == KEYUP:
#                 if event.key == K_LSHIFT or event.key == K_RSHIFT: shift = False
            
#             elif event.type == MOUSEMOTION:    # check for hover on reactive components
#                 for item in userInfoMenuReactiveComponents:
#                     if item.getRect().collidepoint(pygame.mouse.get_pos()):
#                         if item.getType() == "button": item.hover(True)
#                         elif item.getType() == "entry": item.focus(True)
#                     else:
#                         if item.getType() == "button": item.hover(False)
#                         elif item.getType() == "entry":
#                             if not item.getClicked(): item.focus(False)

#             elif event.type == MOUSEBUTTONDOWN:  # check for clicks on reactive components
#                 for item in userInfoMenuReactiveComponents:
#                     if item.getRect().collidepoint(pygame.mouse.get_pos()):
#                         if item.getType() == "button": 
#                             item.click()
#                             break
#                         elif item.getType() == "entry": 
#                             item.focus(True)
#                             item.setClicked(True)
#                     else:
#                         if item.getType() == "entry": 
#                             item.focus(False)
#                             item.setClicked(False)
        
#         screen.fill(black)
#         for component in userInfoMenuComponents: screen.blit(component, component.getRect())
#         pygame.display.flip()


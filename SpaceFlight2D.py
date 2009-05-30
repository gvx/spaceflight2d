#SpaceFlight2D 0.9
#(C) 2008,2009 Robin Wellner <gyvox.public@gmail.com>
#Please report bugs to: <http://github.com/gvx/spaceflight2d/issues>
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#Released under GPL (see http://www.gnu.org/licenses/)
#
#Uses:
# * PyPGL by PyMike
# * feedback from PyMike
# * Substitute Clock by Adam Bark
# * toggle_fullscreen() by philhassey & illume + Duoas
# * Bits from Astroids 2 and Planet Vector, both by Ian Mallett
#
#Idea from <http://gpwiki.org/index.php/Game_ideas:_Two-dimensional_Space_Game> by "Saarelma".


###################################
#Importing Etc
import pygame
from pygame.locals import *
import os
from sys import platform as sys_platform
if sys_platform[:3] == 'win':
    os.environ['SDL_VIDEO_CENTERED'] = '1'
from math import *
import random
try: import cPickle
except: import Pickle as cPickle
import ExPGL as PyPGL
import menu
from clock import ABClock
import story
try:
    import psyco
    psyco.full()
except:
    pass #error message goes here
pygame.init()


###################################
#Anti-Aliased Circle
def aacircle(Surface,color,pos,radius,resolution,width=1):
    for I in xrange(resolution):
        pygame.draw.aaline(Surface, color, (pos[0] + radius*cos(2*pi*float(I)/resolution), pos[1] + radius*sin(2*pi*float(I)/resolution)), (pos[0] + radius*cos(2*pi*float(I+1)/resolution), pos[1] + radius*sin(2*pi*float(I+1)/resolution)), width)


###################################
#Toggle Full Screen
#By philhassey & illume
def toggle_fullscreen():
    screen = pygame.display.get_surface()
    tmp = screen.convert()
    caption = pygame.display.get_caption()
    cursor = pygame.mouse.get_cursor()  # Duoas 16-04-2007 

    w,h = screen.get_width(),screen.get_height()
    flags = screen.get_flags()
    bits = screen.get_bitsize()
    
    pygame.display.quit()
    pygame.display.init()
    
    screen = pygame.display.set_mode((w,h),flags^FULLSCREEN,bits)
    screen.blit(tmp,(0,0))
    pygame.display.set_caption(*caption)
 
    pygame.key.set_mods(0) #HACK: work-a-round for a SDL bug??
 
    pygame.mouse.set_cursor( *cursor )  # Duoas 16-04-2007
    
    return screen


###################################
#Sounds & Graphics
Font = pygame.font.Font("mksanstallx.ttf",14)
BigFont = pygame.font.Font("mksanstallx.ttf",18)

Sounds = {'boom': pygame.mixer.Sound(os.path.join("data", "boom2.ogg")),
          'select': pygame.mixer.Sound(os.path.join("data", "select.ogg")),
          'unselect': pygame.mixer.Sound(os.path.join("data", "unselect.ogg")),
          'shoot': pygame.mixer.Sound(os.path.join("data", "shoot.ogg"))}

try:
    pygame.mixer.music.load(os.path.join("musicdata", "music.ogg"))
    MUSIC_PACK = True
except:
    pygame.mixer.music.load(os.path.join("data", "theme.mid"))
    MUSIC_PACK = False
music = pygame.mixer.music

SoundChannels = {'boom': pygame.mixer.Channel(0),
                 'select': pygame.mixer.Channel(1),
                 'unselect': pygame.mixer.Channel(2),
                 'shoot': pygame.mixer.Channel(3)}

SoundTypes = {'FX': ['boom', 'select', 'unselect', 'shoot']}

vectorImages = {'player/1': PyPGL.image.load(os.path.join("data", 'ship-1.vgf'), (100,100), 0, 0.3),
                'player/2': PyPGL.image.load(os.path.join("data", 'ship-2.vgf'), (0,0), 0, 0.3),
                'player/3': PyPGL.image.load(os.path.join("data", 'ship-3.vgf'), (0,0), 0, 0.3),
                'player/4': PyPGL.image.load(os.path.join("data", 'ship-4.vgf'), (0,0), 0, 0.3),
                'base': PyPGL.image.load(os.path.join("data", 'base.vgf'), (0,0), 0, 0.8),
                'enemy/ship': PyPGL.image.load(os.path.join("data", 'enemy-ship.vgf'), (0,0), 0, 0.5),
                'enemy/base': PyPGL.image.load(os.path.join("data", 'enemy-base.vgf'), (0,0), 0, 0.8)}

PlayerImages = 0
Frames = 0
ArchiveIndex = 0
GamePaused = False
LastGameLoaded = 0
doCheat = False
MDOWN = False
ExtendedVision=False
GRID_WIDTH = 30

def Play(sndStr):
    if sndStr != 'music':
        SoundChannels[sndStr].play(Sounds[sndStr], 0)
    else:
        music.play(-1)

def Stop(sndStr):
    if sndStr != 'music':
        SoundChannels[sndStr].stop()
    else:
        music.stop()


###################################
#Mottos Shown In Main Menu
Mottos = ("Will you succeed in conquering the galaxy?",
          "SpaceFlight2D by Robin Wellner.",
          "Colours are overrated!",
          "Click 'New' to play.",
          "Have you tried the introduction yet?",
          "No comment.",
          "I can't believe it, but this really is version 1.0!",
          "The graphics are just some lines. Well, at least the game's fun.",
          "Have you read all these mottos? I have. I also wrote them.",
          "I'm waiting for you to do something.",
          "Come on then! Get clickin'!",
          "Welcome back!",
          "Don't click [here], nothing will happen.",
          "You're playing a brand new version of SpaceFlight2D.",
          "SpaceFlight2D 2.0 will be ready some day.",
          "Is there anyone who actually reads these mottos?",
         )


###################################
#Default Settings
MUSIC_VOLUME = 4
FX_VOLUME = 6
KEYS = {
'UP': 273,
'LEFT': 276,
'RIGHT': 275,
'FIRE': 32,
'LAUNCH': 303,
'BUILD': 98,
'REPAIR': 114,
'FILL': 102,
'PAUSE': 112,
'ZOOMOUT': 122,
'ZOOMIN': 97,
'DROP': 100,
'MAP': 109,
'EXVIS': 101,
}
SCR_FULL = False
SCR_SIZE = (640,480)

###################################
#Load Settings
f = open(os.path.join('data','settings.txt'))
subj = None
for line in f:
    if line[0] not in '#\n':
        if line[0] == '\t':
            split = line[1:].split()
            if subj == 'Sound Volume':
                if split[0] == 'Music:':
                    MUSIC_VOLUME = int(split[1])
                elif split[0] == 'Effects:':
                    FX_VOLUME = int(split[1])
            elif subj == 'Keys':
                key = split[0].upper()
                if key in KEYS:
                    KEYS[key] = int(split[1])
            elif subj == 'Screen':
                if split[0] == 'Mode:':
                    SCR_FULL = split[1] == 'Full'
                elif split[0] == 'Size:':
                    SCR_SIZE = tuple(int(i) for i in split[1].split('x'))
        else:
            subj = line[:-1]
f.close()

for Channel in SoundTypes['FX']:
    SoundChannels[Channel].set_volume(FX_VOLUME/10.0)
pygame.mixer.music.set_volume(MUSIC_VOLUME/10.0)

#Warning colours:
CLR_WARNING = (255, 0, 0)
CLR_NORMAL = (255, 255, 255)


###################################
#Defining Classes
class Planet(object):
    def __init__(self, X, Y, Size):
        self.X = X
        self.Y = Y
        self.size = Size
        self.baseAt = None
        self.enemyAt = None
        self.playerLanded = False
        self.oil = Size

class Ship(object):
    def __init__(self, X, Y, Angle, FaceAngle, Speed):
        self.X = X
        self.Y = Y
        self.toX = Speed * -sin(radians(Angle))
        self.toY = Speed * cos(radians(Angle))
        self.angle = Angle
        self.faceAngle = FaceAngle
        self.speed = Speed
        self.oil = 1000
        self.maxoil = 1000
        self.hull = 592
        self.maxhull = 592
    def move(self):
        self.X += self.toX
        self.Y += self.toY

class ownShip(Ship):
    def __init__(self, X, Y, Angle, FaceAngle, Speed):
        Ship.__init__(self, X, Y, Angle, FaceAngle, Speed)
        self.landedOn = None
        self.landedBefore = None
        self.shoot = 0

class enemyShip(Ship):
    def __init__(self, X, Y, Angle, FaceAngle, Speed, Orbit):
        Ship.__init__(self, X, Y, Angle, FaceAngle, Speed)
        self.orbit = Orbit #(centerX, centerY, altitude)
        self.orbitpos = 0
        self.dead = False
        self.explosion = 0
    def move(self):

        diffX = self.X - (self.orbit[0] + self.orbit[2] * cos(radians(self.orbitpos)))
        diffY = self.Y - (self.orbit[1] + self.orbit[2] * sin(radians(self.orbitpos)))
        if abs(diffX)+abs(diffY) < 10:
            self.orbitpos = (self.orbitpos + 2) % 360
        ang = atan2(diffY, diffX)
        diffX = cos(ang)
        diffY = sin(ang)
        self.toX = -diffX * self.speed
        self.toY = -diffY * self.speed
        self.angle = degrees(atan2(-self.toX, self.toY))
        self.faceAngle = self.angle
        Ship.move(self)

class View(object):
    X = 0
    Y = 0
    angle = 0
    zoomfactor = 1

class GameData(object):
    basesBuilt = 0
    homePlanet = None
    tasks = []
    stage = 0
    shootings = 0
    tutorial = False

class starrange(object):
    __slots__ = ('min','max','pos')
    def __init__(self, min, max):
        self.min = min
        self.max = max
        self.pos = min-1
    def __iter__(self):
        self.pos = self.min-1
        return self
    def next(self):
        if self.pos > self.max:
            raise StopIteration
        else:
            self.pos += 1
            if self.pos == 0:
                self.pos += 1
            return self.pos

class StarData(object):
    params = (random.random(),
              random.random(),
              random.random(),
              random.random(),
              random.random())
    xlist = starrange(-8, 8)
    ylist = starrange(-6, 6)


###################################
#Creating PlayerShip & Object Containers
playerShip = ownShip(0,0,0,180,0)
playerView = View()
gameData = None #GameData()
starData = StarData()

ShipContainer = []
WreckContainer = []
PlanetContainer = []
ArchiveContainer = []
SystemContainer = []

credits = (("SPACEFLIGHT2D", 0),
           ("(C)2008,2009 Robin Wellner", 15),
           ("CREDITS:", 25),
           ("Astroids 2 by Ian Mallet", 15),
           ("Planet Vector by Ian Mallet", 15),
           ("PyPGL by PyMike", 15),
           ("Substitute Clock by Adam Bark", 15),
           ("toggle_fullscreen()", 15),
           ("by philhassey & illume + Duoas", 15),
           ("FONT:", 25),
           ("Sans Tall X by Manfred Klein", 15),
           ("LICENSES:", 25),
           ("Code: GNU GPL, version 3", 15),
           ("Music: CC-BY-NC-SA", 15),
           ("Font: see TinyUrl.com/mktuo", 15),
           ("IDEA: gpwiki.org", 25))


###################################
#Function For Main Menu
def Menu():
    Clock = ABClock()
    Motto = random.choice(Mottos)
    tick = 0
    focus = 0
    Colours = ((255, 255, 255), (0, 0, 0))
    Items = [('New game', 'new'), ('Tutorial', 'tutorial'), ('Load game...', 'load'),
             ('Options...', 'options'), ('Exit', 'exit')]
    if gameData is not None:
        Items.insert(1, ('Resume', 'continue'))
    itemheight = 30
    totalheight = 50
    while True:
        Clock.tick(10)
        keystate = pygame.key.get_pressed()
        tick += 1
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return 'exit'
            elif event.type == MOUSEBUTTONDOWN:
                if event.button==1:
                    if 200 < event.pos[0] < 500 and 20 < event.pos[1] < totalheight*len(Items):
                        clicked_item = (event.pos[1] - 20)/totalheight
                        return Items[clicked_item][1]
            elif event.type == MOUSEMOTION:
                if 200 < event.pos[0] < 500 and 20 < event.pos[1] < totalheight*len(Items):
                    focus = (event.pos[1] - 20)/totalheight
            elif event.type == KEYDOWN:
                if event.key in (K_DOWN, K_RIGHT):
                    focus = (focus + 1) % len(Items)
                elif event.key in (K_UP, K_LEFT):
                    focus = (focus - 1) % len(Items)
                elif event.key in (K_RETURN, K_SPACE):
                    return Items[focus][1]
                else:
                    pass
        Surface.fill((0,0,0))
        for n in range(len(Items)):
            draw_item = Items[n][0]
            pygame.draw.rect(Surface, (255, 255, 255), (200, 20 + n*totalheight, 300, itemheight), 1-(focus==n))
            Surface.blit(Font.render(draw_item, True, Colours[focus==n]),
                         (215, 25 + n*totalheight))
        #Info text
        Text = Font.render(Motto, True, (255,255,255))
        Surface.blit(Text,(200,totalheight*len(Items)+10))
        tot_y = 0
        for line, y in credits:
            tot_y += y
            Surface.blit(Font.render(line, True, (255,255,255)),(10,tot_y+20))
        pygame.display.flip()


###################################
#Function For Options Menu
def Options():
    global FX_VOLUME, MUSIC_VOLUME, SCR_FULL, Surface
    f = 0
    while True:
        Items = [('Sound effects volume', 'fx', 'slider', (FX_VOLUME, 0, 10)),
                 ('Music volume', 'music', 'slider', (MUSIC_VOLUME, 0, 10)),
                 ('Full screen', 'full', 'checkbox', SCR_FULL),
                 ('Resolution...', 'size', 'button'),
                 ('Keys...', 'keys', 'button'),
                 ('Apply', 'ok', 'button'),
                 ('Back', 'cancel', 'cancelbutton'),
                ]
        result, data = menu.menu(Surface, Items, 30, 200, 30, 30, 50, 300, Font, f)
        if result == 'exit':
            return 'exit'
        elif result == 'cancel':
            return 'to menu'
        elif result == 'ok':
            FX_VOLUME = data['fx'].index
            MUSIC_VOLUME = data['music'].index
            for Channel in SoundTypes['FX']:
                SoundChannels[Channel].set_volume(FX_VOLUME/10.0)
            pygame.mixer.music.set_volume(MUSIC_VOLUME/10.0)
            if data['full'].checked != SCR_FULL:
                Surface = toggle_fullscreen()
                SCR_FULL = not SCR_FULL
            f = 5
        elif result == 'keys':
            ChangeKeys()
            f = 4
        elif result == 'size':
            ChangeRes()
            f = 3


###################################
#Menu For Changing Screen Size
def ChangeRes():
    global SCR_SIZE
    global Surface
    f = 0
    reslist = [('640x480', (640,480), 'button'),
               ('800x600', (800,600), 'button'),
               ('1024x768', (1024,768), 'button'),
               ('1280x800', (1280,800), 'button'),
               ('1280x1024', (1280,1024), 'button'),
               ('Cancel', 'cancel', 'cancelbutton'),
              ]
    for i in xrange(len(reslist)):
        if reslist[i][1] == SCR_SIZE:
            f = i
            break
    result, data = menu.menu(Surface, reslist, 30, 200, 30, 30, 50, 300, Font, f)
    if result != 'cancel':
        SCR_SIZE = result
        try:
            Surface = pygame.display.set_mode(SCR_SIZE, SCR_FULL and FULLSCREEN)
        except:
            pass
    


###################################
#Menu For Changing Game Keys
def ChangeKeys():
    f = 0
    keylist = [('Speed up', 'UP'),
               ('Steer left', 'LEFT'),
               ('Steer right', 'RIGHT'),
               ('Fire lasers', 'FIRE'),
               ('Launch', 'LAUNCH'),
               ('Build base', 'BUILD'),
               ('Repair ship', 'REPAIR'),
               ('Fill tank', 'FILL'),
               ('Pause game', 'PAUSE'),
               ('Zoom in', 'ZOOMIN'),
               ('Zoom out', 'ZOOMOUT'),
               ('Drop oil', 'DROP'),
               ('Extended Vision', 'EXVIS'),
              ]
    while True:
        Items = []
        for i in keylist:
            Items.append((i[0] + ' (' + ReprKey(KEYS[i[1]])+ ')', i[1], 'button'))
        Items.append(('Back', 'cancel', 'cancelbutton'))
        result, data = menu.menu(Surface, Items, 30, 200, 30, 30, 50, 300, Font, f)
        if result != 'cancel':
            ChangeKey(result)
            for i in range(len(Items)):
                if Items[i][1] == result:
                    f=i
        else:
            break


###################################
#Change A Game Key
def ChangeKey(keyname):
    key = KEYS[keyname]
    name = keyname.capitalize()
    Clock = ABClock()
    while True:
        Clock.tick(40)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key in (K_ESCAPE, K_RETURN):
                    return
                elif event.key not in (K_s, K_F1, K_F2, K_F3, K_F4):
                    KEYS[keyname] = event.key
                    return
        Surface.fill((0,0,0))
        Text = Font.render('Press a new key for the action '+name+'.', True, (255,255,255))
        Surface.blit(Text,(20,20))
        Text = Font.render('Current key: '+ReprKey(key)+'.', True, (255,255,255))
        Surface.blit(Text,(20,50))
        pygame.display.flip()


###################################
#Representation Of Key
def ReprKey(key):
    #keydict = {getattr(pygame.locals, i): i[2:].capitalize() for i in dir(pygame.locals) if i.startswith('K_')} #no Python3.0
    keydict = dict((getattr(pygame.locals, i), i[2:].capitalize()) for i in dir(pygame.locals) if i.startswith('K_'))
    return keydict.get(key, 'Unknown key')


###################################
#Get Input During Game
def GetInput():
    keystate = pygame.key.get_pressed()
    global PlayerImages, GamePaused, LastGameLoaded, doCheat, MDOWN
    PlayerImages = 0
    for event in pygame.event.get():
        if event.type == QUIT:
            return 'exit'
        elif event.type == KEYUP:
            if event.key == KEYS['PAUSE']:
                GamePaused = not GamePaused
    if keystate[K_ESCAPE]:
        return 'to menu'
    if not GamePaused:
        if keystate[KEYS['UP']]:
            playerShip.toX -= sin(radians(playerShip.faceAngle)) * .1
            playerShip.toY += cos(radians(playerShip.faceAngle)) * .1
            playerShip.speed = (playerShip.toX**2 + playerShip.toY**2) ** 0.5
            playerShip.angle = degrees(atan2(-playerShip.toX, playerShip.toY))
            playerShip.oil -= 0.1
            PlayerImages = 1
        if keystate[KEYS['LEFT']]:
            playerShip.faceAngle -= 3
            playerShip.faceAngle = playerShip.faceAngle % 360
        if keystate[KEYS['RIGHT']]:
            playerShip.faceAngle += 3
            playerShip.faceAngle = playerShip.faceAngle % 360
        if keystate[KEYS['FIRE']]:
            playerShip.oil -= 0.1
            Hit = False
            playerShip.shoot = 3
            for item in ShipContainer:
                if ((playerShip.X - item.X)**2 + (playerShip.Y + item.Y)**2)**.5 < 200:
                    item.hull -= 10
                    Hit = True
                    if item.hull <= 0:
                        Play('boom')
                        item.dead = True
                        item.explosion = 0
                        WreckContainer.append(ShipContainer.pop(ShipContainer.index(item)))
                        #del item
            for item in PlanetContainer:
                    if item.enemyAt is not None:
                        X = item.X + item.size*cos(radians(item.enemyAt+90))
                        Y = item.Y + item.size*sin(radians(item.enemyAt+90))
                        if ((playerShip.X - X)**2 + (playerShip.Y + Y)**2)**.5 < 200:
                            Play('boom')
                            item.enemyAt = None
            if Hit: Play('shoot')
        if keystate[KEYS['LAUNCH']]:
            PlayerImages = 2
            playerShip.toX -= sin(radians(playerShip.faceAngle)) * 2
            playerShip.toY += cos(radians(playerShip.faceAngle)) * 2
            playerShip.speed = (playerShip.toX**2 + playerShip.toY**2) ** 0.5
            playerShip.angle = degrees(atan2(-playerShip.toX, playerShip.toY))
            playerShip.oil -= 10
        if keystate[KEYS['BUILD']]:
            if playerShip.landedOn is not None:
                if PlanetContainer[playerShip.landedOn].baseAt is None and PlanetContainer[playerShip.landedOn].enemyAt is None:
                    if PlanetContainer[playerShip.landedOn].oil >= 200:
                        PlanetContainer[playerShip.landedOn].oil -= 200
                        XDiff = playerShip.X - PlanetContainer[playerShip.landedOn].X
                        YDiff = playerShip.Y + PlanetContainer[playerShip.landedOn].Y
                        PlanetContainer[playerShip.landedOn].baseAt = degrees(atan2(-XDiff, -YDiff))
                        PlanetContainer[playerShip.landedOn].playerLanded = 'base'
                        gameData.basesBuilt += 1
                        checkProgress('base built')
                else:
                        checkProgress('base failed')
        if keystate[KEYS['REPAIR']]:
            if playerShip.landedOn is not None:
                if PlanetContainer[playerShip.landedOn].playerLanded == 'base':
                    if PlanetContainer[playerShip.landedOn].oil >= playerShip.maxhull - playerShip.hull:
                        PlanetContainer[playerShip.landedOn].oil -= playerShip.maxhull - playerShip.hull
                        playerShip.hull = playerShip.maxhull
                    else:
                        playerShip.hull += PlanetContainer[playerShip.landedOn].oil
                        PlanetContainer[playerShip.landedOn].oil = 0
        if keystate[KEYS['FILL']]:
            if playerShip.landedOn is not None:
                if PlanetContainer[playerShip.landedOn].playerLanded == 'base':
                    if PlanetContainer[playerShip.landedOn].oil >= playerShip.maxoil - playerShip.oil:
                        PlanetContainer[playerShip.landedOn].oil -= playerShip.maxoil - playerShip.oil
                        playerShip.oil = playerShip.maxoil
                    else:
                        playerShip.oil += PlanetContainer[playerShip.landedOn].oil
                        PlanetContainer[playerShip.landedOn].oil = 0
        if keystate[KEYS['DROP']]:
            if playerShip.landedOn is not None:
                if PlanetContainer[playerShip.landedOn].playerLanded == 'base':
                    if playerShip.oil > 20:
                        playerShip.oil -= 5
                        PlanetContainer[playerShip.landedOn].oil += 5
    if keystate[K_s]:
        SaveAs()
    if keystate[KEYS['ZOOMIN']]:
        if playerView.zoomfactor > 1:
            playerView.zoomfactor = playerView.zoomfactor * .9
    elif keystate[KEYS['ZOOMOUT']]:
        if playerView.zoomfactor < 100:
            playerView.zoomfactor = playerView.zoomfactor / .9
    if keystate[KEYS['MAP']] and not MDOWN:
        if Map() == 'exit':
            return 'exit'
        MDOWN = 10
    elif MDOWN:
        MDOWN -= 1
    global ExtendedVision;ExtendedVision = keystate[KEYS['EXVIS']]


###################################
#Check Progress & Continue Story Line
def checkProgress(action):
    return story.check(action, gameData, DisplayMessage, SystemContainer, Planet, ArchiveContainer, enemyShip, playerShip, ReprKey, KEYS, GRID_WIDTH)

###################################
#Move Ships & Collision Detection
def Move():
    global ArchiveIndex, gameData
    playerShip.landedBefore = playerShip.landedOn
    playerShip.landedOn = None
    for Thing in PlanetContainer:
        XDiff = playerShip.X - Thing.X
        YDiff = playerShip.Y + Thing.Y
        Distance = (XDiff**2+YDiff**2)**0.5
        if Distance > 40000:
           ArchiveContainer.append(Thing)
           PlanetContainer.remove(Thing)
        elif Distance <= Thing.size+26:
            #collision OR landed --> check speed
            if playerShip.speed > 2:
                playerShip.hull -= playerShip.speed**2
            if playerShip.hull <= 0:
                #crash!
                Play('boom')
                if gameData.homePlanet in ArchiveContainer:
                    PlanetContainer.append(gameData.homePlanet)
                    ArchiveContainer.remove(gameData.homePlanet)
                if gameData.homePlanet.oil > 1592: #592+1000
                    playerShip.hull = 592
                    playerShip.oil = 1000
                    playerShip.X = 0
                    playerShip.Y = 25
                    playerShip.toX = 0
                    playerShip.toY = 0
                    playerShip.faceAngle = 180
                    gameData.homePlanet.oil -= 1592
                else:
                    playerShip.hull = 0
                    DisplayMessage('You crashed and died in the explosion. You lose.')
                    gameData = None
                    return 'to menu'
            else:
                #land!
                playerShip.landedOn = PlanetContainer.index(Thing)
                if not Thing.playerLanded:
                    if gameData.tutorial and gameData.stage == 1:
                        checkProgress("player landed")
                    if Thing.baseAt is not None and \
                       ((Thing.X+Thing.size*cos(radians(Thing.baseAt+90)) - playerShip.X)**2 + (-Thing.Y-Thing.size*sin(radians(Thing.baseAt+90)) - playerShip.Y)**2)**.5 < 60:
                        Thing.playerLanded = 'base'
                    else:
                        Thing.playerLanded = True
                    playerShip.toX = 0
                    playerShip.toY = 0
                    continue
                else:
                    NDistance = ((playerShip.X+playerShip.toX-Thing.X)**2 +
                                 (playerShip.Y+playerShip.toY+Thing.Y)**2)**0.5
                    if NDistance < Distance:
                        playerShip.toX = Thing.size/20/Distance * XDiff/Distance
                        playerShip.toY = Thing.size/20/Distance * YDiff/Distance
                        playerShip.speed = (playerShip.toX**2 + playerShip.toY**2) ** 0.5
                        playerShip.angle = degrees(atan2(-playerShip.toX, playerShip.toY))
                        playerShip.move()
                        playerShip.toX = 0
                        playerShip.toY = 0
                        continue
        else:
            Thing.playerLanded = False
        if gameData.stage > 0 and Thing.enemyAt is not None:
            X = Thing.X + Thing.size*cos(radians(Thing.enemyAt+90))
            Y = Thing.Y + Thing.size*sin(radians(Thing.enemyAt+90))
            if ((playerShip.X - X)**2 + (playerShip.Y + Y)**2)**.5 < 300:
                playerShip.hull -= random.randint(1,3)*random.randint(1,3)
                gameData.shootings = 3
                if playerShip.hull <= 0:
                    Play('boom')
                    if gameData.homePlanet in ArchiveContainer:
                        PlanetContainer.append(gameData.homePlanet)
                        ArchiveContainer.remove(gameData.homePlanet)
                    if gameData.homePlanet.oil > 1592: #592+1000
                        playerShip.hull = 592
                        playerShip.oil = 1000
                        playerShip.X = 0
                        playerShip.Y = 25
                        playerShip.toX = 0
                        playerShip.toY = 0
                        playerShip.faceAngle = 180
                        gameData.homePlanet.oil -= 1592
                    else:
                        playerShip.hull = 0
                        DisplayMessage('You where shot and died. You lose.')
                        gameData = None
                        return 'to menu'
        Acceleration = Thing.size/20/Distance
        playerShip.toX -= Acceleration * XDiff/Distance
        playerShip.toY -= Acceleration * YDiff/Distance
        playerShip.speed = (playerShip.toX**2 + playerShip.toY**2) ** 0.5
        playerShip.angle = degrees(atan2(-playerShip.toX, playerShip.toY))
    for Thing in ShipContainer:
        #move ships
        Thing.move()
        if gameData.stage > 0:
            if ((playerShip.X - Thing.X)**2 + (playerShip.Y + Thing.Y)**2)**.5 < 300:
                playerShip.hull -= random.randint(1,3)*random.randint(1,3)
                gameData.shootings = 3
                if playerShip.hull <= 0:
                    Play('boom')
                    if gameData.homePlanet in ArchiveContainer:
                        PlanetContainer.append(gameData.homePlanet)
                        ArchiveContainer.remove(gameData.homePlanet)
                    if gameData.homePlanet.oil > 1592: #592+1000
                        playerShip.hull = 592
                        playerShip.oil = 1000
                        playerShip.X = 0
                        playerShip.Y = 25
                        playerShip.toX = 0
                        playerShip.toY = 0
                        playerShip.faceAngle = 180
                        gameData.homePlanet.oil -= 1592
                    else:
                        playerShip.hull = 0
                        DisplayMessage('You where shot and died. You lose.')
                        gameData = None
                        return 'to menu'
    for Thing in WreckContainer:
        Thing.explosion += 0.1
        if Thing.explosion > 10:
            WreckContainer.remove(Thing)
    playerShip.move()
    if floor(playerShip.X/30000) != floor((playerShip.X-playerShip.toX)/30000) or floor(playerShip.Y/30000) != floor((playerShip.Y-playerShip.toY)/30000):
        checkProgress('sector changed')
    playerView.X = playerShip.X
    playerView.Y = playerShip.Y
    if playerShip.oil <= 0:
        Play('boom')
        if gameData.homePlanet in ArchiveContainer:
            PlanetContainer.append(gameData.homePlanet)
            ArchiveContainer.remove(gameData.homePlanet)
        if gameData.homePlanet.oil > 1592: #592+1000
            playerShip.hull = 592
            playerShip.oil = 1000
            playerShip.X = 0
            playerShip.Y = 25
            playerShip.toX = 0
            playerShip.toY = 0
            playerShip.faceAngle = 180
            gameData.homePlanet.oil -= 1592
        else:
            playerShip.oil = 0
            DisplayMessage("Your oilsupply is empty. You can't do anything anymore. You lose.")
            gameData = None
            return 'to menu'
        playerShip.X = 0
        playerShip.Y = 25
        playerShip.toX = 0
        playerShip.toY = 0
        playerShip.faceAngle = 180
        playerShip.oil = 1000
    if Frames % 10 == 0:
        try:
            Distance = ((playerShip.X - ArchiveContainer[ArchiveIndex].X)**2+(playerShip.Y + ArchiveContainer[ArchiveIndex].Y)**2)**0.5
            if Distance < 35000:
                T = ArchiveContainer.pop(ArchiveIndex)
                if type(T) == Planet:
                    PlanetContainer.append(T)
                elif T.dead:
                    WreckContainer.append(T)
                else:
                    ShipContainer.append(T)
                ArchiveIndex = ArchiveIndex % len(ArchiveContainer)
            else:
                ArchiveIndex = (ArchiveIndex + 1) % len(ArchiveContainer)
        except: #If the ArchiveContainer is empty
            pass


###################################
#Function To Draw Everything
def Draw(update=True):
    global WreckContainer, ShipContainer, PlanetContainer, Frames, GamePaused, ZoomedOut
    if gameData.shootings > 0:
        Surface.fill((100,0,0))
        gameData.shootings -= 1
    else:
        Surface.fill((0,0,0))
    #Display direction (Thanks, retroredge, for pointing it out!)
    tmpColor = (playerView.zoomfactor*2,)*3
    aacircle(Surface, tmpColor, (320, 240), 180, 45, 1)
    rads = radians(playerShip.faceAngle+90)
    rads2 = rads + 2.094 #radians(120)
    rads3 = rads - 2.094 #this should be precise enough
    xy = (320+180*cos(rads),240+180*sin(rads))
    pygame.draw.aaline(Surface, tmpColor, xy, (320+180*cos(rads2),240+180*sin(rads2)), 1)
    pygame.draw.aaline(Surface, tmpColor, xy, (320+180*cos(rads3),240+180*sin(rads3)), 1)
    if playerShip.shoot > 0:
        pygame.draw.circle(Surface,(128,128,128),(320, 240), int(200/playerView.zoomfactor))
        playerShip.shoot -= 1

    STARy = 240 - playerView.Y/200
    STARx = 320 - playerView.X/200
    for i in starData.xlist:
        for j in starData.ylist:
            tmp = (i+starData.params[0])*starData.params[1]+(j+starData.params[2])*starData.params[3]+starData.params[4]
            x = STARx + i * 200 * cos(tmp)
            y = STARy + j * 200 * sin(tmp)
            pygame.draw.aaline(Surface, (255,255,255), (x,y), (x+1.5,y+1.5), 1)
            pygame.draw.aaline(Surface, (255,255,255), (x+1.5,y), (x,y+1.5), 1)
    
    for Thing in PlanetContainer:
        aacircle(Surface,(255,255,255),((Thing.X-playerView.X)/playerView.zoomfactor+320,(-Thing.Y-playerView.Y)/playerView.zoomfactor+240),Thing.size/playerView.zoomfactor,int(10*log(Thing.size*.2/playerView.zoomfactor,2))+20,1)
        tmpExVisStr = ''
        if Thing.baseAt is not None:
            vectorImages['base'].position((320+(-playerView.X+Thing.X+Thing.size*cos(radians(Thing.baseAt+90)))/playerView.zoomfactor ,240+(-playerView.Y-Thing.Y-Thing.size*sin(radians(Thing.baseAt+90)))/playerView.zoomfactor))
            vectorImages['base'].rotate(Thing.baseAt)
            vectorImages['base'].scale(0.8/playerView.zoomfactor)
            vectorImages['base'].draw(Surface, (255,255,255))
            tmpExVisStr = 'Own base'
        if Thing.enemyAt is not None:
            vectorImages['enemy/base'].position((320+(-playerView.X+Thing.X+Thing.size*cos(radians(Thing.enemyAt+90)))/playerView.zoomfactor ,240+(-playerView.Y-Thing.Y-Thing.size*sin(radians(Thing.enemyAt+90)))/playerView.zoomfactor))
            vectorImages['enemy/base'].rotate(Thing.enemyAt)
            vectorImages['enemy/base'].scale(0.8/playerView.zoomfactor)
            vectorImages['enemy/base'].draw(Surface, (255,255,255))
            tmpExVisStr = 'Enemy base'
        if ExtendedVision:
            tmpExVisx = (Thing.X-playerView.X)/playerView.zoomfactor+320
            tmpExVisy = (-Thing.Y-playerView.Y)/playerView.zoomfactor+240
            Surface.blit(Font.render(tmpExVisStr, True, (255,255,255)),(tmpExVisx,tmpExVisy))
            Surface.blit(Font.render('Oil: '+str(int(Thing.oil)), True, (255,255,255)),(tmpExVisx,tmpExVisy+15))
    for Thing in ShipContainer:
        vectorImages['enemy/ship'].position((320+(-playerView.X+Thing.X)/playerView.zoomfactor ,240+(-playerView.Y-Thing.Y)/playerView.zoomfactor))
        vectorImages['enemy/ship'].rotate(Thing.faceAngle)
        vectorImages['enemy/ship'].scale(0.5/playerView.zoomfactor)
        vectorImages['enemy/ship'].explode(0)
        vectorImages['enemy/ship'].draw(Surface, (255,255,255))
    for Thing in WreckContainer:
        vectorImages['enemy/ship'].position((320+(-playerView.X+Thing.X)/playerView.zoomfactor ,240+(-playerView.Y-Thing.Y)/playerView.zoomfactor))
        vectorImages['enemy/ship'].rotate(Thing.faceAngle)
        vectorImages['enemy/ship'].scale(0.5/playerView.zoomfactor)
        vectorImages['enemy/ship'].explode(Thing.explosion)
        vectorImages['enemy/ship'].draw(Surface, (255,255,255), max=int(7-Thing.explosion))

    if PlayerImages == 0:
        imgStr = '1'
    elif PlayerImages == 1:
        if (Frames//5) % 2:
            imgStr = '3'
        else:
            imgStr = '2'
    elif PlayerImages == 2:
        if (Frames//5) % 2:
            imgStr = '2'
        else:
            imgStr = '4'
    vectorImages['player/'+imgStr].position((320, 240))
    vectorImages['player/'+imgStr].rotate(-playerShip.faceAngle-180+playerView.angle)
    vectorImages['player/'+imgStr].scale(0.3/playerView.zoomfactor)
    vectorImages['player/'+imgStr].draw(Surface, (255,255,255))
    
    pygame.draw.rect(Surface, (255-playerShip.oil*255/playerShip.maxoil if playerShip.oil > 0 else 255, 0, playerShip.oil*255/playerShip.maxoil if playerShip.oil > 0 else 0), (8, 8+(playerShip.maxoil-playerShip.oil)*464/playerShip.maxoil, 20, playerShip.oil*464/playerShip.maxoil), 0)
    if playerShip.oil < 100:
        c_ = CLR_WARNING
        n_ = 2
    else:
        c_ = CLR_NORMAL
        n_ = 1
    pygame.draw.rect(Surface, c_, (8, 8, 20, 464), n_)

    pygame.draw.rect(Surface, (0, 255, 0), (40, 8, 592*playerShip.hull/playerShip.maxhull, 20), 0)
    if playerShip.hull < 50:
        c_ = CLR_WARNING
        n_ = 2
    else:
        c_ = CLR_NORMAL
        n_ = 1
    pygame.draw.rect(Surface, c_, (40, 8, 592, 20), n_)
    
    if playerShip.speed > 16:
        c_ = CLR_WARNING
    else:
        c_ = CLR_NORMAL
    Text = BigFont.render("Speed: %.2d" % playerShip.speed, True, c_)
    Surface.blit(Text,(40,40))
    if GamePaused:
        Text = Font.render("Game paused...", True, (255,255,255))
        Surface.blit(Text,(40,80))
    Text = Font.render("Bases built: " + str(gameData.basesBuilt), True, (255,255,255))
    Surface.blit(Text,(40,95))
    Text = Font.render("You are in Sector " + str(int(floor(playerShip.X/30000))) + ":" + str(int(floor(playerShip.Y/30000))), True, (255,255,255))
    Surface.blit(Text,(40,125))
    top = 40
    for task in gameData.tasks:
        Text = Font.render(task, True, (255,255,255))
        top += 13
        Surface.blit(Text,(400,top))
    if playerShip.landedOn is not None:
        if PlanetContainer[playerShip.landedOn].playerLanded == 'base':
            Text = Font.render("Oil on planet: " + str(int(PlanetContainer[playerShip.landedOn].oil)), True, (255,255,255))
            Surface.blit(Text,(40,110))
    elif playerShip.landedBefore is not None:
        if PlanetContainer[playerShip.landedBefore].playerLanded == 'base':
            Text = Font.render("Oil on planet: " + str(int(PlanetContainer[playerShip.landedBefore].oil)), True, (255,255,255))
            Surface.blit(Text,(40,110))
    if update:
        pygame.display.flip()


###################################
#Displaying an ingame message
def DisplayMessage(msg, source='Game'):
    global GamePaused
    GamePaused = True
    Clock = ABClock()
    while True:
        Clock.tick(20)
        for event in pygame.event.get():
            if event.type == QUIT:
                GamePaused = False
                return
        keystate = pygame.key.get_pressed()
        if keystate[K_RETURN]:
            GamePaused = False
            return
        Draw(False)
        if Font.size(msg)[0] > 380:
            words = msg.split(' ')
            print_text = []
            line = ''
            height = 0
            for word in words:
                if Font.size(line + word + " ")[0] < 380:
                    line += word + ' '
                else:
                    print_text.append(line)
                    height += Font.size(line)[1]
                    line = word + " "
            print_text.append(line)
            height += Font.size(line)[1]
        else:
            print_text = [msg]
            height = Font.size(msg)[1]
        pygame.draw.rect(Surface, (155, 155, 155), (100, 160, 400, 40), 0)
        pygame.draw.rect(Surface, (255, 255, 255), (100, 200, 400, 40+height), 0)
        Text = Font.render(source, True, (0,0,0))
        Surface.blit(Text,(110,170))
        for i in range(len(print_text)):
            m = print_text[i]
            Text = Font.render(m, True, (0,0,0))
            Surface.blit(Text,(110,210+i*height/len(print_text)))
        Text = Font.render("Press [RETURN] to continue...", True, (0,0,0))
        Surface.blit(Text,(220,220+height))
        pygame.display.flip()


###################################
#Starting A New Game
def SetUpGame():
    global WreckContainer, ShipContainer, PlanetContainer, ArchiveContainer, playerShip, gameData, SystemContainer
    gameData = GameData()
    gameData.tutorial = False
    PlanetContainer = [Planet(0, -1050, 1000)]
    gameData.homePlanet = PlanetContainer[0]
    gameData.tasks = ["Build a base on another planet"]
    PlanetContainer[0].baseAt = 0
    ShipContainer = []
    ShipContainer.append(enemyShip(200, 200, 0, 0, 2, (0, -1050, 1500)))
    WreckContainer = []
    SystemContainer = [(0, 0, "Home System")]
    for newPlanetX in range(-1, 2):
        for newPlanetY in range(-1, 2):
            if newPlanetX == 0 and newPlanetY == 0: continue
            PlanetContainer.append(Planet(newPlanetX * 20000 + random.randint(-8000, 8000), newPlanetY * 18000 + random.randint(-6000, 6000), random.randint(250, 1500)))
            PlanetContainer[-1].enemyAt = random.choice((None, random.randint(0, 360)))
    PlanetContainer[0].playerLanded = 'base'
    ArchiveContainer = []
    playerShip.X = 0
    playerShip.Y = 25
    playerShip.angle = 0
    playerShip.faceAngle = 180
    playerShip.speed = 0
    playerShip.hull = 592
    playerShip.toX = 0
    playerShip.toY = 0
    playerView.X = 0
    playerView.Y = 0
    playerView.angle = 0
    playerView.zoomfactor = 1
    gameData.basesBuilt = 0
    playerShip.oil = 1000
    starData.params = (random.random(),
                       random.random(),
                       random.random(),
                       random.random(),
                       random.random())
    Game()


###################################
#Starting A Tutorial
def Tutorial():
    global WreckContainer, ShipContainer, PlanetContainer, ArchiveContainer, playerShip, gameData, SystemContainer
    gameData = GameData()
    gameData.tutorial = True
    PlanetContainer = [Planet(0, -1050, 1000)]
    gameData.homePlanet = PlanetContainer[0]
    gameData.tasks = ["Follow the instructions."]
    PlanetContainer[0].enemyAt = 180
    ShipContainer = []
    WreckContainer = []
    SystemContainer = [(0, 0, "Home System")]
    moon = Planet(2000, 2000, 300)
    PlanetContainer.append(moon)
    PlanetContainer[0].playerLanded = True
    ArchiveContainer = []
    playerShip.X = 0
    playerShip.Y = 25
    playerShip.angle = 0
    playerShip.faceAngle = 180
    playerShip.speed = 0
    playerShip.hull = 592
    playerShip.toX = 0
    playerShip.toY = 0
    playerView.X = 0
    playerView.Y = 0
    playerView.angle = 0
    playerView.zoomfactor = 1
    gameData.basesBuilt = 0
    playerShip.oil = 1000
    starData.params = (random.random(),
                       random.random(),
                       random.random(),
                       random.random(),
                       random.random())
    checkProgress('game started')
    Game()


###################################
#Returns A List Of Saved Games
def ListGames():
    return [file[:-4] for file in os.listdir(os.path.join("data", 'games')) if file.endswith(".pkl")]

###################################
#Opens A Certain Game File
def OpenGameFile(file, mode):
    return open(os.path.join("data", 'games', file+'.pkl'), mode)


###################################
#Loading A Saved Game
def Load():
    MenuList = [(file, file, 'button') for file in ListGames()]
    f = 0
    if LastGameLoaded:
        for i in range(len(MenuList)):
            if MenuList[i][0] == LastGameLoaded:
                f = i
    MenuList.append(('Cancel', 'cancel', 'cancelbutton'))
    result, data = menu.menu(Surface, MenuList, 20, 200, 10, 30, 35, 300, Font,f)
    if result != 'cancel':
        LoadGame(result)


###################################
#Load A Game
def LoadGame(Slot):
    global LastGameLoaded, playerShip, playerView, gameData, WreckContainer, ShipContainer, PlanetContainer, ArchiveContainer, starData
    LastGameLoaded = Slot
    f = OpenGameFile(Slot, 'rb')
    try:
        test = cPickle.load(f)
        if isinstance(test, str):
            if test == '0.9B':
                playerShip = cPickle.load(f)
                playerView = cPickle.load(f)
                gameData = cPickle.load(f)
                ShipContainer = cPickle.load(f)
                WreckContainer = cPickle.load(f)
                PlanetContainer = cPickle.load(f)
                ArchiveContainer = cPickle.load(f)
                SystemContainer = cPickle.load(f)
                starData = cPickle.load(f)
            elif test == '0.9':
                playerShip = cPickle.load(f)
                playerView = cPickle.load(f)
                gameData = cPickle.load(f)
                ShipContainer = cPickle.load(f)
                WreckContainer = cPickle.load(f)
                PlanetContainer = cPickle.load(f)
                ArchiveContainer = cPickle.load(f)
                SystemContainer = [(0, 0, "Home System")]
                starData = cPickle.load(f)
        else:
            playerShip = test
            playerView = cPickle.load(f)
            gameData = cPickle.load(f)
            ShipContainer = cPickle.load(f)
            WreckContainer = []
            PlanetContainer = cPickle.load(f)
            ArchiveContainer = cPickle.load(f)
            starData = cPickle.load(f)
    except:
        f.close()
        Play('unselect')
    else:
        f.close()
        if Game() == 'exit':
            return 'exit'
        else:
            return 'to menu'

###################################
#Get A Filename To Save To
def SaveAs():
    global GamePaused
    GP = GamePaused
    GamePaused = True
    Clock = ABClock()
    if isinstance(LastGameLoaded, str):
        text = LastGameLoaded
    else:
        text = ''
    ticks = 0
    insertpos = len(text)
    Left = 35
    Top = 200
    printable = [ord(char) for char in 'abcdefghijklmnopqrstuvwxyz0123456789']
    FileList = ListGames()
    while True:
        Clock.tick(20)
        for event in pygame.event.get():
            if event.type == QUIT:
                GamePaused = GP
                return
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    if insertpos > 0:
                        text = text[:insertpos-1] + text[insertpos:]
                        insertpos -= 1
                elif event.key == K_DELETE:
                    text = text[:insertpos] + text[insertpos+1:]
                elif event.key in printable:
                    text = text[:insertpos] + chr(event.key) + text[insertpos:]
                    insertpos += 1
                elif event.key == K_TAB:
                    GamePaused = GP
                    return
                elif event.key == K_RETURN:
                    if text:
                        Save(text)
                    GamePaused = GP
                    return
                elif event.key == K_LEFT:
                    if insertpos > 0: insertpos -= 1
                elif event.key == K_RIGHT:
                    if insertpos < len(text): insertpos += 1
                elif event.key == K_HOME:
                    insertpos = 0
                elif event.key == K_END:
                    insertpos = len(text)
        Draw(False)
        ticks+= 1
        Y = Font.size(text)[1]
        pygame.draw.rect(Surface, (255, 255, 255), (Left, Top, 300, Y+4))
        pygame.draw.rect(Surface, (150, 150, 150), (Left, Top, 300, Y+4), 1)
        Surface.blit(Font.render('Save to: (press Tab to cancel)', 1, (255, 255, 255)),
                     (Left+2, Top-Y-3))
        Surface.blit(Font.render(text, 1, (0, 0, 0)),
                     (Left+2, Top))
        if (ticks//8)%2 == 0:
            X = Font.size(text[:insertpos])[0]
            pygame.draw.line(Surface, (0,0,0), (Left+2+X,Top+2), (Left+2+X,Top+Y), 1)
        #if ticks % 500 == 0:       #Uncomment this code
        #    FileList = ListGames() #to check for new games once in a while
        ypos = Top + Y + 8
        for file in FileList:
            if file.startswith(text):
                Surface.blit(Font.render(file, 1, (255, 255, 255)),
                             (Left+2, ypos))
                ypos += Y
        pygame.display.flip()


###################################
#Save The Current Game
def Save(Slot):
    global LastGameLoaded
    f = OpenGameFile(Slot, 'wb')
    cPickle.dump('0.9', f, -1)
    cPickle.dump(playerShip, f, -1)
    cPickle.dump(playerView, f, -1)
    cPickle.dump(gameData, f, -1)
    cPickle.dump(ShipContainer, f, -1)
    cPickle.dump(WreckContainer, f, -1)
    cPickle.dump(PlanetContainer, f, -1)
    cPickle.dump(ArchiveContainer, f, -1)
    cPickle.dump(starData, f, -1)
    f.close()
    LastGameLoaded = Slot


###################################
#Helper Function For Map() That Gives Randomized Coordinates
def map_randxy():
    if random.randint(0, 100) < 6:
        return random.randint(-5,5)
    return 0


###################################
#Show A Map To Help Navigating
def Map():
    Clock = ABClock()
    viewx = posx = playerShip.X/30000*GRID_WIDTH
    viewy = posy = playerShip.Y/30000*GRID_WIDTH
    #viewx = 0
    #viewy = 0
    Frames = 0
    green = (0, 210, 0)
    lgreen = (10, 255, 10)
    white = (255,255,255)
    t = "You are here"
    p = Font.render(t, 1, white)
    txtwd = Font.size(t)[0]
    while True:
        Clock.tick(15)
        keystate = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == QUIT:
                return 'exit'
            elif event.type == KEYDOWN:
                if event.key == KEYS['MAP'] or event.key == K_ESCAPE:
                    Play('unselect')
                    return
        if keystate[K_LEFT]:
            viewx -= 5
        if keystate[K_UP]:
            viewy -= 5
        if keystate[K_RIGHT]:
            viewx += 5
        if keystate[K_DOWN]:
            viewy += 5
        Frames+=1
        #green[1] = int(200+sin(Frames/10.0)*50)
        Surface.fill((0,0,0))
        for X in xrange(SCR_SIZE[0]/GRID_WIDTH+2):
            pygame.draw.line(Surface, green, (X*GRID_WIDTH - viewx%GRID_WIDTH, 0), (X*GRID_WIDTH - viewx%GRID_WIDTH, SCR_SIZE[1]))
        for Y in xrange(SCR_SIZE[1]/GRID_WIDTH+2):
            pygame.draw.line(Surface, green, (0, Y*GRID_WIDTH - viewy%GRID_WIDTH), (SCR_SIZE[0], Y*GRID_WIDTH - viewy%GRID_WIDTH))
        Surface.blit(p, (SCR_SIZE[0]/2 - viewx + posx - txtwd - 10, SCR_SIZE[1]/2 - viewy + posy - 10))
        pX = int(SCR_SIZE[0]/2 - viewx + posx)
        pY = int(SCR_SIZE[1]/2 - viewy + posy)
        pygame.draw.aaline(Surface, lgreen, (pX-9000,pY-9000), (pX+9000,pY+9000))
        pygame.draw.aaline(Surface, lgreen, (pX-9000,pY+9000), (pX+9000,pY-9000))
        #aacircle(Surface,green,(SCR_SIZE[0]/2 - viewx, SCR_SIZE[1]/2 - viewy),6,10)
        for system in SystemContainer:
            pygame.draw.circle(Surface,green,(int(SCR_SIZE[0]/2 - viewx + system[0]), int(SCR_SIZE[1]/2 - viewy + system[1])),4,0)
            Surface.blit(Font.render(system[2], 1, white), (SCR_SIZE[0]/2 - viewx + system[0] + 5, SCR_SIZE[1]/2 - viewy + system[1] - 5))
        #pygame.draw.circle(Surface,green,(SCR_SIZE[0]/2 - viewx, SCR_SIZE[1]/2 - viewy),6,0)
        pygame.display.flip()


###################################
#The Main Game Loop
def Game():
    global Frames
    Clock = ABClock()
    while True:
        returnvalue = GetInput()
        if returnvalue == 'to menu':
            return
        elif returnvalue == 'exit':
            return 'exit'
        if GamePaused == False:
            if Move() == 'to menu':
                return
            Frames += 1
            Clock.tick(45)
        else:
            Clock.tick(10)
        Draw()


###################################
#Save Settings To File
def SaveSettings():
    f = open('data/settings.txt', 'w')
    f.write('Sound Volume\n\tMusic: %d\n\tEffects: %d\n'
            'Keys\n\tUp: %d\n\tLeft: %d\n\tRight: %d\n\tFire: %d\n\tLaunch: %d\n\tBuild: %d\n\tRepair: %d\n\tFill: %d\n\tPause: %d\n\tZoomOut: %d\n'
            '\tZoomIn: %d\n\tDrop: %d\n\tMap: %d\n\tExVis: %d\nScreen\n\tMode: %s\n\tSize: %s\n\n'
            '#Default Keys:\n#Action\t\tKey\tCode\n#Speed Up\tUp\t273\n#Steer Left\tLeft\t276\n#Steer Right\tRight\t275\n#Fire\t\tSpace\t32\n'
            '#Launch\t\tRShift\t303\n#Build Base\tB\t98\n'
            '#Repair\t\tR\t114\n#Fill oil tank\tF\t102\n#Pause\t\tP\t112\n#Zoom out\tZ\t122\n#Zoom in\tA\t97\n#Drop\t\tD\t100\n#Map\t\tM\t109\n#ExVis\t\tE\t101\n#For other key codes, check pygame.locals'
            % (MUSIC_VOLUME, FX_VOLUME, KEYS['UP'], KEYS['LEFT'], KEYS['RIGHT'], KEYS['FIRE'], KEYS['LAUNCH'], KEYS['BUILD'], KEYS['REPAIR'], KEYS['FILL'], KEYS['PAUSE'], KEYS['ZOOMOUT'], KEYS['ZOOMIN'], KEYS['DROP'], KEYS['MAP'], KEYS['EXVIS'], 'Full' if SCR_FULL else 'Windowed', 'x'.join(str(i) for i in SCR_SIZE)))
    f.close()


###################################
#The Main Loop
def Main():
    #Set Up Window
    pygame.display.set_caption("SpaceFlight2D")
    icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
    global Surface
    Surface = pygame.display.set_mode(SCR_SIZE, SCR_FULL and FULLSCREEN)
    Play('music')
    while True:
        result = Menu()
        if result == 'new':
            if SetUpGame() == 'exit':
                break
        elif result == 'continue':
            if Game() == 'exit':
                break
        elif result == 'tutorial':
            if Tutorial() == 'exit':
                break
        elif result == 'load':
            if Load() == 'exit':
                break
        elif result == 'intro':
            if Intro() == 'exit':
                break
        elif result == 'options':
            r = Options()
            SaveSettings()
            if r == 'exit':
                break
        elif result == 'exit':
            break
    pygame.quit()


if __name__ == '__main__': Main()

# -*- coding: iso-8859-1 -*-

'''
This is an example on using Stackless Python in PSP. The idea is based on a
tutorial created by Sakya.

Here we have the concept of agent based programming where the player, the NPC
and the render engine as an agent doing its actions.

The player agent waits for the user input captured from the keypad.

The NPC agent starts running around the screen in a predefined pattern.

The render engine does all the drawing job clearing the screen and putting each
agent in its own place.

As you can see, all the logic is very simplified because of the flexibility
stackless gives to us. Every agent can have its own behaviour and optionally
follow some "world" rules defined for example in a separate Agent.

This "World" could detect collisions, handle communications between agents and
interact with other elements. This can be an exercise to the user.

'''
import psp2d, pspos
import pspnet
import pspmp3
import pspogg
from time import time, localtime
import datetime
import sys
import stackless

# Set processor and bus speed
pspos.setclocks(333,166)
#pspos.setclock(100)
#pspos.setbus(50)

print "Localtime: ", localtime()
print "Datetime: ", datetime.datetime.now()


# Creates the screen and its background color (Black)
screen = psp2d.Screen()
screen.clear(psp2d.Color(0,0,0,255))

# Loads the font
font = psp2d.Font('font.png')

# Loads the character movement images
spriteImages = []
spriteImages.append((psp2d.Image('amg1_bk1.png'), psp2d.Image('amg1_bk2.png'))) #Direction = north   = 0
spriteImages.append((psp2d.Image('amg1_fr1.png'), psp2d.Image('amg1_fr2.png'))) #Direction = south   = 1
spriteImages.append((psp2d.Image('amg1_lf1.png'), psp2d.Image('amg1_lf2.png'))) #Direction = west    = 2
spriteImages.append((psp2d.Image('amg1_rt1.png'), psp2d.Image('amg1_rt2.png'))) #Direction = east    = 3


# Creates the Agent base class
class Agent(object):
    def __init__(self):
        self.ch = stackless.channel()       # Communication channel (not used here)
        self.running = True                 # Flag to control the running status
        stackless.tasklet(self.runAction)() # Creates the agent tasklet

    def runAction(self):
        # Here we define the main action, a repetition of the function self.action()
        while self.running:
            # Runs the action
            self.action()
            # Give other tasklets its turn
            stackless.schedule()

    def action(self):
        # In the base class do nothing
        pass

class player(Agent):
    def __init__(self, rend):
        Agent.__init__(self)
        self.rend = rend        # Reference to the renderer tasklet
        self.boolSprite = False
        self.direction = 1
        self.speed = 3
        self.posX = 30
        self.posY = 30
        self.lastPad = time()
        self.rend.agents.append(self) # Adds this agent to the renderer
        self.sprite = spriteImages[self.direction][int(self.boolSprite)]
        self.screenshot = 1;

    def action(self):
        self.sprite = spriteImages[self.direction][int(self.boolSprite)]
        pad = psp2d.Controller()
        if pad.cross:
            print "exit"
            self.rend.exit()
        elif pad.triangle:
            screen.saveToFile("ms0:/PSP/PHOTO/screenshot%s.png" % self.screenshot)
            self.screenshot += 1
        elif pad.down and (not self.lastPad or time() - self.lastPad >= 0.05):
          #Draw the player facing south:
          self.lastPad = time()
          self.direction = 1
          if self.posY + self.sprite.height + self.speed < 272:
            self.posY += self.speed
            self.boolSprite = not self.boolSprite
        elif pad.up and (not self.lastPad or time() - self.lastPad >= 0.05):
          #Draw the player facing north:
          self.lastPad = time()
          self.direction = 0
          if self.posY - self.speed >= 0:
            self.posY -= self.speed
            self.boolSprite = not self.boolSprite
        elif pad.left and (not self.lastPad or time() - self.lastPad >= 0.05):
          #Draw the player facing west:
          self.lastPad = time()
          self.direction = 2
          if self.posX - self.speed >= 0:
            self.posX -= self.speed
            self.boolSprite = not self.boolSprite
        elif pad.right and (not self.lastPad or time() - self.lastPad >= 0.05):
          #Draw the player facing east:
          self.lastPad = time()
          self.direction = 3
          if self.posX + self.sprite.width + self.speed < 480:
            self.posX += self.speed
            self.boolSprite = not self.boolSprite

class NPC(Agent):
    def __init__(self, rend):
        Agent.__init__(self)
        self.rend = rend
        self.boolSprite = False
        self.direction = 0
        self.speed = 5
        self.posX = 230
        self.posY = 230
        self.lastPad = time()
        self.rend.agents.append(self)
        self.sprite = spriteImages[self.direction][int(self.boolSprite)]
        self.count = 20

    def action(self):
        # This NPC runs around the screen changing its direction
        # when touches the border.
        self.sprite = spriteImages[self.direction][int(self.boolSprite)]
        if self.direction == 0 and \
           (not self.lastPad or time() - self.lastPad >= 0.05):
            self.lastPad = time()
            if self.posY - self.speed >= 20:
                self.posY -= self.speed
                self.boolSprite = not self.boolSprite
            else:
                self.direction = 2
        if self.direction == 2 and \
           (not self.lastPad or time() - self.lastPad >= 0.05):
            self.lastPad = time()
            if self.posX - self.speed > 0:
                self.posX -= self.speed
                self.boolSprite = not self.boolSprite
            else:
                self.direction = 1
        if self.direction == 1 and \
           (not self.lastPad or time() - self.lastPad >= 0.05):
            self.lastPad = time()
            if self.posY + self.sprite.height + self.speed < 252:
                self.posY += self.speed
                self.boolSprite = not self.boolSprite
            else:
                self.direction = 3
        if self.direction == 3 and \
           (not self.lastPad or time() - self.lastPad >= 0.05):
            self.lastPad = time()
            if self.posX + self.sprite.width + self.speed < 450:
                self.posX += self.speed
                self.boolSprite = not self.boolSprite
            else:
                self.direction = 0


class render(Agent):
    # This is the renderer agent
    def __init__(self):
        Agent.__init__(self)
        self.agents = []

    def exit(self):
        # When the player calls the exit, tell all Agents to stop running
        print "Stopping agents..."
        for agent in self.agents:
            print "Stopped agent %s" % agent
            agent.running = False
        self.running = False
        print "Stopped self..."

    def action(self):
        # Each frame the renderer clears the screen,
        # writes the text and draws each registered agent.
        screen.clear(psp2d.Color(0,0,0,255))
        font.drawText(screen, 10, 225, "Move your character with directional")
        font.drawText(screen, 10, 240, "Triangle takes screenshot")
        font.drawText(screen, 10, 255, "Press X to exit")
        for agent in self.agents:
            screen.blit(agent.sprite, 0, 0, agent.sprite.width,
                        agent.sprite.height, agent.posX, agent.posY, True)
        screen.swap()


print "Real memory: ",pspos.realmem()

#Loads background music
pspmp3.init(1)
#pspmp3.load("MP3Sample.mp3")        # Uncomment this to add a MP3 in backgound
pspmp3.play()

#Loads background music in ogg
#pspogg.init(2)
#pspogg.load('Oggsample.ogg')
#pspogg.play()

# Creates the renderer object
rend = render()
# Creates a player Agent
play = player(rend)
# Creates one NPC that runs around the screen
NPC1 = NPC(rend)

# Starts the game loop
stackless.run()
#pspogg.end()
pspmp3.end()

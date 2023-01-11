import pygame
from pygame.locals import *
import os
import time
import json
import logging

pygame.init() # initialize pygame
# Load in main settings json
with open("./settings.json", "r") as configjsonFile:
    scriptconfig = json.load(configjsonFile)
    logtype = scriptconfig['logtype']
    screenh = scriptconfig['screenheight']
    screenw = scriptconfig['screenwidth']

initcurtime = time.localtime()
curtime = (f'{initcurtime.tm_hour}{initcurtime.tm_min}{initcurtime.tm_sec}')
curdate = (f'{initcurtime.tm_year}{initcurtime.tm_mon}{initcurtime.tm_mday}')

logging.basicConfig(filename=f"RHS_ADisplay_renderd_{curdate}.log",
                    format='%(asctime)s %(levelname)s %(message)s',
                    filemode='a')
log = logging.getLogger()
if "debug" in logtype:
    log.setLevel(logging.DEBUG) # use this for debugging.
elif "info" in logtype:
    log.setLevel(logging.INFO) # use this for production
else:
    log.setLevel(logging.INFO)
    log.error("A logger type was not specified in the configuration file.")
    print("Error: A logger type was not specified in the configuration file.")
    exit()

# screen = pygame.display.set_mode((screenh,screenw))
screen = pygame.display.set_mode((1280,700))
pygame.display.set_caption("RHSDisplay")
# TODO: make this a config option, and make sure this will scale properly

class Square(pygame.sprite.Sprite):
    def __init__(self):
        super(Square, self).__init__()
        # Define the dimension of the surface
        # Here we are making squares of side 25px
        self.surf = pygame.Surface((25, 25))
        # Define the color of the surface using RGB color coding.
        self.surf.fill((0, 200, 255))
        self.rect = self.surf.get_rect()

testi = pygame.image.load("xenoclap_apng.png").convert()
screen.blit(testi,(0,0))


# instantiate all square objects
square1 = Square()
square2 = Square()
square3 = Square()
square4 = Square()

gameOn = True

while gameOn:
    for event in pygame.event.get():
        if event.type == QUIT:
            gameOn = False
    # Define where the squares will appear on the screen
    # Use blit to draw them on the screen surface
    screen.blit(square1.surf, (40, 40))
    screen.blit(square2.surf, (40, 530))
    screen.blit(square3.surf, (730, 40))
    screen.blit(square4.surf, (730, 530))

    pygame.display.flip()
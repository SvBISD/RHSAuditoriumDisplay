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

screen = pygame.display.setmode((screenh,screenw))
# TODO: make this a config option, and make sure this will scale properly


"""
Just a ton of colours
"""

import random

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
dark_red = (128,0,0)
light_green = (0,255,0)
grass_green = (0,128,0)
dark_green = (0,60,0)
dark_blue = (0, 0, 255)
maroon = (128, 0, 0)
dark_orange = (255, 69, 0)
orange = (255, 140, 0)
gold = (255, 215, 0)
yellow = (255, 255, 0)
turquoise = (32, 178, 170)
light_blue = (0, 192, 220)
skyblue = (0, 191, 255)
navy = (0, 0, 64)
purple = (138, 43, 226)
pink = (255, 0, 255)
brown = (70, 35, 10)
grey = (128, 128, 128)
dark_grey = (64, 64, 64)
light_grey = (192,192,192)
slategrey = (112, 128, 144)

colour = ["black", "white", "red", "dark_red", "light_green", "grass_green", "dark_grey", "dark_green", "dark_blue", "maroon", "dark_orange", "orange", "gold", "yellow", "turquoise", "light_blue", "skyblue", "navy", "purple", "pink", "brown", "grey", "slategrey"]

colours = {"black":black,
           "white":white,
           "red":red,
           "dark_red":dark_red,
           "light_green":light_green,
           "grass_green":grass_green,
           "dark_green":dark_green,
           "dark_blue":dark_blue,
           "maroon":maroon,
           "dark_orange":dark_orange,
           "orange":orange,
           "gold":gold,
           "yellow":yellow,
           "turquoise":turquoise,
           "light_blue":light_blue,
           "skyblue":skyblue,
           "navy":navy,
           "purple":purple,
           "pink":pink,
           "brown":brown,
           "grey":grey,
           "dark_grey":dark_grey,
           "slategrey":slategrey}


def random_colour():
    c = random.choice(colour)
    return colours[c]
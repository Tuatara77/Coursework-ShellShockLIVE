from os.path import join
from pygame.image import load

friendly_tank = load(join("images", "green-tank.png"))
friendly_tank_barrel = load(join("images", "green-barrel.png"))
enemy_tank = load(join("images", "red-tank.png"))
enemy_tank_barrel = load(join("images", "red-barrel.png"))

explosion = load(join("images", "explosion.png")).convert_alpha()
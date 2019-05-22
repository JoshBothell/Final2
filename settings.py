import pygame as pg
vec = pg.math.Vector2

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
BROWN = (106, 55, 5)
DARKGREEN = (20, 130, 39)

# game settings
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = DARKGREEN

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

WALL_IMG = 'treeGreen_large.png'

# player settings
PLAYER_HEALTH = 500
PLAYER_SPEED = 250
PLAYER_ROT_SPEED = 250
PLAYER_IMG = 'tank_red.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 0)

# gun settings
BULLET_IMG = 'bulletRed1_outline.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 1000
MOB_BULLET_RATE = 1000
BULLET_RATE = 500
KICKBACK = 0
GUN_SPREAD = 5
BULLET_DAMAGE = 20

# mob settings
MOB_IMG = 'tank_dark.png'
MOB_SPEED = 150
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
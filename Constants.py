import os

'''-----------------------------------------------------------------------------
    COLORS '''

WHITE =             (255, 255, 255)
BLACK =             (  0,   0,   0)
RED =               (255,   0,   0)
GREEN =             (  0, 255,   0)
BLUE =              (  0,   0, 255)
YELLOW =            (255, 255,   0)
PURPLE =            (  0, 255, 255)

STEEL_BLUE =        ( 70, 130, 180)

'''-----------------------------------------------------------------------------
    GAME SETTINGS'''

WIDTH =             800
HEIGHT =            800
FPS =               60

GAME_FONT =         "comicsans"
GAME_FONT_COLOR =   WHITE
GAME_FONT_SIZE =    50
TEXT_BOX_COLOR =    (20,  20,  20)
MENU_PADDING =      5

'''-----------------------------------------------------------------------------
    AVATAR ATTRIBUTES '''

PLAYER_ATTRIBUTES = {
    "power" :       5,
    "speed" :       5,
    "inventory" :   2,
    "health" :      100,
    "laser_vel":    -6}

ENEMY_ATTRIBUTES = {
    "power" :       5,
    "speed" :       5,
    "inventory" :   1,
    "health" :      100,
    "laser_vel":    6}

ENEMY_SPAWN_TIME =  70

'''-----------------------------------------------------------------------------
    LOGGING '''

LOGGING_FORMAT =        '%(asctime)s %(message)s'
LOGGING_DATE_FORMAT =   '%m/%d/%Y %I:%M:%S %p'
LOG_EVENTS =            False
LOG_OBJECTS =           False
LOG_COLLISIONS =        True

'''-----------------------------------------------------------------------------
    PATHS '''

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

IMG_PLAYER_SHIP =   f"{CURRENT_DIR}\\img\\spaceship_yellow.png"
IMG_AVATAR_SHIP =   f"{CURRENT_DIR}\\img\\spaceship_red.png"
IMG_LASER =         f"{CURRENT_DIR}\\img\\laser.png"
IMG_SPACE =         f"{CURRENT_DIR}\\img\\space.png"

'''-----------------------------------------------------------------------------'''

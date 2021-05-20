from Constants import *
import pygame
import os
import sys
import random
import logging
import functools


pygame.init()

'''-----------------------------------------------------------------------------
    GAME LOG '''

logging.basicConfig(    format=LOGGING_FORMAT,
                        datefmt=LOGGING_DATE_FORMAT,
                        level=logging.DEBUG)

def log_event(event, obj):
    if event == "State":             logging.info(f"Game State Change:    {str(obj)}")
    if event == "Loop":              logging.info(f"Current Loop:         {str(obj)}")
    if event == "Menu Selection":    logging.info(f"Menu Selection:       {str(obj)}")
    if LOG_EVENTS:
        if event == "Event":         logging.info(f"Event:                {str(obj)}")
    if LOG_OBJECTS:
        if event == "Obj Created":   logging.info(f"Obj Created:          {str(obj)}")
        if event == "Obj Removed":   logging.info(f"Obj Removed:          {str(obj)}")
    if LOG_COLLISIONS:
        if event == "Collision":     logging.info(f"Collision:            {str(obj)}")

'''-----------------------------------------------------------------------------
    BASIC OBJECTS '''

class Py_Game:
    def __init__(self, screen_width, screen_height, fps):
        self.w =                    screen_width
        self.h =                    screen_height
        self.fps =                  fps

        self.font =                 pygame.font.SysFont(GAME_FONT, GAME_FONT_SIZE)
        self.font_color =           GAME_FONT_COLOR
        self.clock =                pygame.time.Clock()
        self.display =              pygame.Surface((self.w, self.h))
        self.screen =               pygame.display.set_mode((self.w, self.h))

        self.running =              True
        self.state_history =        []
        self.state_is_new =         False

        self.objects =              []
        self.background =           None

        self.game_over_timer =      100
        self.game_over_text =       Text_obj(self, "Game Over")

    def __str__(self):
        return str(type(self))

    # --------------------------------------------------------------------------
    # SCREEN MANAGEMENT

    def screen_update(self):
        pygame.display.update()
        self.clock.tick(self.fps)

    def set_background(self, filename, scale = None):
        self.background = Img(filename, scale)

    def draw_background(self):
        self.screen.blit(self.background.file,(0,0))

    # --------------------------------------------------------------------------
    # GAME STATE MANAGEMENT

    def set_state(self, state):
        log_event("State", state)
        self.state_history.append(state)
        self.state_is_new = True

    def get_state(self):
        return self.state_history[-1]

    # --------------------------------------------------------------------------
    # EVENT MANAGEMENT

    def check_events_for_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                log_event("Event","User quit")
                pygame.quit()
                quit()

    def check_state(self):
        self.check_events_for_quit()
        if self.state_is_new == True:
            self.state_is_new = False
            self.log_obj_counts()
            if   self.get_state() == "Exit":  pygame.quit()
            elif self.get_state() == "Stop":  self.running = False
            #Add Other Game States Here

    def main_loop(self):
        log_event("Loop", self)
        self.running = True
        while self.running:
            self.check_state()
            self.screen_update()

    def game_over(self):
        x = (self.w - self.game_over_text.w)/2
        y = (self.h - self.game_over_text.h)/2
        while self.game_over_timer != 0:
            self.screen.blit(self.game_over_text.obj, (x, y))
            self.game_over_timer -= 1
            self.screen_update()
        self.running = False

'''-----------------------------------------------------------------------------'''

class Img:
    def __init__(self, img_filename, scale = None):
        self.file = None
        self.mask = None
        self.get_file(img_filename)
        if scale:
            self.resize(scale)

    def __str__(self):
        return str(type(self))

    # --------------------------------------------------------------------------

    def get_mask(self):
        self.mask =         pygame.mask.from_surface(self.file)

    def get_file(self, img_filename, img_location = None):
        try:
            self.file =    pygame.image.load(img_filename)
        except FileNotFoundError:
            logging.error(f"File not found: \t\t {img_filename}")
            pygame.quit()
            quit()
        finally:
            self.get_mask()

    def resize(self, scale):
        new_width =         int(scale / 100 * self.file.get_width())
        new_height =        int(scale / 100 * self.file.get_height())
        self.file =         pygame.transform.scale(self.file, (new_width, new_height))
        self.mask =         self.get_mask()

'''-----------------------------------------------------------------------------'''

class Drawable_Object:
    def __init__(self, game):
        self.game =                 game
        self.show =                 True
        self.collided =             False
        self.img =                  None
        self.img_mask =             None
        self.x =                    0
        self.y =                    0
        self.x_min =                0
        self.y_min =                0
        self.x_max =                game.w
        self.y_max =                game.h
        self.w =                    0
        self.h =                    0
        self.speed =                1
        self.game.objects.append(self)

    def __str__(self):
        return str(type(self))

    # --------------------------------------------------------------------------
    # IMAGE

    def set_img(self, filename, size):
        self.img =          Img(filename, size)
        self.img_mask =     pygame.mask.from_surface(self.img.file)
        self.w =            self.get_width()
        self.h =            self.get_height()

    def get_width(self):
        return self.img.file.get_width()

    def get_height(self):
        return self.img.file.get_height()

    def draw(self, screen):
        screen.blit(self.img.file, (self.x, self.y))

    # --------------------------------------------------------------------------
    # POSITIONING

    def set_movement_area(self, x_min, x_max, y_min, y_max):
        self.x_min =                x_min
        self.y_min =                x_max
        self.x_max =                y_min
        self.y_max =                y_max

    def set_location(self, x, y):
        self.x = x
        if self.x > self.x_max - self.w:    self.x = self.x_max - self.w
        if self.x < self.x_min:             self.x = self.x_min
        self.y = y
        if self.y > self.y_max - self.h:    self.y = self.y_max - self.h
        if self.y < self.y_min:             self.y = self.y_min

    def set_movement_multiplier(self, value):
        self.movement_multiplier = value

    # --------------------------------------------------------------------------
    # MOVEMENT MANAGEMENT

    def move(self, x_offset = 0, y_offset = 0, use_multiplier = True):
        if not use_multiplier: multiplier = 1
        else: multiplier = self.speed
        x = self.x + (x_offset * multiplier)
        y = self.y + (y_offset * multiplier)
        self.set_location(x, y)

    def move_up(self):      self.move( 0, -1)

    def move_down(self):    self.move( 0,  1)

    def move_right(self):   self.move( 1,  0)

    def move_left(self):    self.move(-1,  0)

    # --------------------------------------------------------------------------
    # MISCELLANEOUS

    def check_for_collisions(self):
        if self.collided == False:
            for other_obj in self.game.objects:
                if other_obj != self:
                    x_offset = int(other_obj.x - self.x)
                    y_offset = int(other_obj.y - self.y)
                    is_overlap = self.img_mask.overlap(other_obj.img_mask, (x_offset, y_offset))
                    if is_overlap:
                        log_event("Collision", str(self) +" & " + str(other_obj))
                        self.collided = True
                        other_obj.collided = True

'''-----------------------------------------------------------------------------'''

class Text_obj:
    def __init__(self, game, text):
        self.game =     game
        self.text =     text
        self.obj =      self.game.font.render(self.text, 1, self.game.font_color)
        self.w =        self.obj.get_width()
        self.h =        self.obj.get_height()

    def __str__(self):
        return str(type(self)) + " - " + self.text

    def set_text(self, text):
        self.text =     text
        self.obj =      self.game.font.render(self.text, 1, self.game.font_color)

    # --------------------------------------------------------------------------

'''-----------------------------------------------------------------------------
    MENUS '''

class Menu:
    def __init__(self, game):
        self.game =              game
        self.running =           True
        self.state =             ""
        self.options =           []
        self.padding =           self.game.menu_padding
        self.options_padding =   5
        self.current_selection = 0
        self.menu_rect =         pygame.Rect( 0, 0, 20, 20)
        self.cursor =            Text_obj(self.game, "*")
        self.w =                 self.get_width()
        self.h =                 self.get_height()
        self.x =                 (self.game.w - self.w) / 2
        self.y =                 (self.game.h - self.h) / 2
        self.options_x =         self.x + self.padding + self.cursor.w + self.options_padding
        self.options_y =         self.y + self.padding
        self.cursor_x =          self.x + self.padding
        self.menu_rect.update(self.x, self.y, self.w, self.h)

    def __str__(self):
        return str(type(self))

    # --------------------------------------------------------------------------
    # POSITIONING

    def set_geometry(self):
        self.w =                 self.get_width()
        self.h =                 self.get_height()
        self.x =                 (self.game.w - self.w) / 2
        self.y =                 (self.game.h - self.h) / 2
        self.options_x =         self.x + self.padding + self.cursor.w + self.options_padding
        self.options_y =         self.y + self.padding
        self.cursor_x =          self.x + self.padding
        self.menu_rect.update(self.x, self.y, self.w, self.h)

    def get_width(self):
        w = 0
        for option in self.options:
            if option.w > w:
                w = option.w
        w = w + self.cursor.w + self.options_padding
        w = w + (self.padding * 2)
        return w

    def get_height(self):
        h = self.game.font.get_height() + 5
        h = h * len(self.options)
        h = h + (self.padding * 2)
        return h

    # --------------------------------------------------------------------------
    # SCREEN MANAGEMENT

    def draw(self):
        self.draw_menu()
        self.draw_options()

    def draw_menu(self):
        pygame.draw.rect(self.game.screen, STEEL_BLUE, self.menu_rect)

    def draw_options(self):
        x = self.options_x
        y = self.options_y
        for option in self.options:
            self.game.screen.blit(option.obj, (x, y))
            if option == self.current_option():
                self.cursor_y = y
                self.draw_cursor()
            y += option.h + self.options_padding

    def draw_cursor(self):
        self.game.screen.blit(self.cursor.obj, (self.cursor_x, self.cursor_y))

    # --------------------------------------------------------------------------
    # CURSOR MANAGEMENT

    def cursor_move_down(self):
        if self.current_selection  == len(self.options)-1:
            self.current_selection = 0
        else:
            self.current_selection += 1

    def cursor_move_up(self):
        if self.current_selection  == 0:
            self.current_selection = len(self.options)-1
        else:
            self.current_selection -= 1

    def cursor_select(self):
        selection = self.options[self.current_selection]
        log_event("Menu Selection", selection)
        selection.call_func()
        self.running = False

    # --------------------------------------------------------------------------
    # EVENT MANAGEMENT

    def check_events(self):
        for event in pygame.event.get():
            log_event("Event", event)
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.cursor_move_up()
                if event.key == pygame.K_DOWN:
                    self.cursor_move_down()
                if event.key == pygame.K_RETURN:
                    self.cursor_select()
            self.game.screen_update()

    def main_loop(self):
        log_event("Loop", self)
        self.set_geometry()
        self.running = True
        while self.running == True:
            self.game.check_events_for_quit()
            self.draw()
            self.check_events()

    # --------------------------------------------------------------------------
    # MISCELLANEOUS

    def add_menu_option(self, text, func, *args, **kwargs):
        # self.options.append(Menu_Option(    self.game,
        #                                     self,
        #                                     text,
        #                                     func,
        #                                     args, kwargs))

        if   len(args) != 0 and len(kwargs) != 0:
            self.options.append(Menu_Option(    self.game,
                                                self,
                                                text,
                                                func,
                                                args, kwargs))
        elif len(args) != 0 and len(kwargs) == 0:
            if len(args) == 1:
                self.options.append(Menu_Option(    self.game,
                                                    self,
                                                    text,
                                                    func,
                                                    args[0]))
            else:
                self.options.append(Menu_Option(    self.game,
                                                    self,
                                                    text,
                                                    func,
                                                    args))
        elif len(args) == 0 and len(kwargs) != 0:
            self.options.append(Menu_Option(    self.game,
                                                self,
                                                text,
                                                func,
                                                kwargs))


    def current_option(self):
        return self.options[self.current_selection]

'''-----------------------------------------------------------------------------'''

class Menu_Option(Text_obj):
    def __init__(self, game, menu, text, func, *args, **kwargs):
        super().__init__(game, text)
        self.menu =         menu
        self.func =         func
        self.args =         args
        self.kwargs =       kwargs
        self.w =            self.obj.get_width()
        self.h =            self.obj.get_height()

    def set_text(self, text):
        super().__init__(self.game, text)
        self.w =            self.obj.get_width()
        self.h =            self.obj.get_height()

    # --------------------------------------------------------------------------

    def call_func(self):
        def func_to_call():
            if   len(self.args) != 0 and len(self.kwargs) != 0:
                self.func(self.args, self.kwargs)
            elif len(self.args) != 0 and len(self.kwargs) == 0:
                if len(self.args) == 1:
                    self.func(self.args[0])
                else:
                    self.func(self.args)
            elif len(self.args) == 0 and len(self.kwargs) != 0:
                self.func(self.kwargs)

        return func_to_call()

'''-----------------------------------------------------------------------------'''

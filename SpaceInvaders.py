from Game_Objects import *

'''-----------------------------------------------------------------------------
    CLASS - GAME'''

class Game:
    def __init__(self, game):
        self.game =                     game
        self.running =                  True
        self.timer_enemy_spawn =        0
        self.timer_enemy_spawns_max =   ENEMY_SPAWN_TIME
        self.player_1 =                 Player(self.game)
        self.lives =                    Text_obj(game, f"LIVES: {self.player_1.lives}")
        self.score =                    Text_obj(game, f"SCORE: {self.player_1.score}")

    def __str__(self):
        return str(type(self))

    # --------------------------------------------------------------------------

    def key_bindings(self):
        keys = pygame.key.get_pressed()

        for key in keys:
            log_event("Event", key)

        if keys[pygame.K_ESCAPE]   : self.game.set_state("Pause")
        if keys[pygame.K_TAB]      : None
        if keys[pygame.K_CAPSLOCK] : None
        if keys[pygame.K_LSHIFT]   : None
        if keys[pygame.K_LCTRL]    : None

        if keys[pygame.K_SPACE]    : self.player_1.shoot_laser()

        if keys[pygame.K_UP]       : self.player_1.move_up()
        if keys[pygame.K_DOWN]     : self.player_1.move_down()
        if keys[pygame.K_LEFT]     : self.player_1.move_left()
        if keys[pygame.K_RIGHT]    : self.player_1.move_right()

        if keys[pygame.K_DELETE]   : None
        if keys[pygame.K_RETURN]   : None
        if keys[pygame.K_BACKSPACE]: None
        if keys[pygame.K_HOME]     : None
        if keys[pygame.K_END]      : None
        if keys[pygame.K_PAGEDOWN] : None
        if keys[pygame.K_PAGEUP]   : None

    def spawn_enemies(self):
        self.timer_enemy_spawn
        if self.timer_enemy_spawn == self.timer_enemy_spawns_max:
            self.game.enemies.append(Enemy(self.game))
            self.timer_enemy_spawn = 0
        else:
            self.timer_enemy_spawn += 1

    def draw_labels(self):
        self.lives = Text_obj(self.game, f"LIVES: {self.player_1.lives}")
        self.score = Text_obj(self.game, f"SCORE: {self.player_1.score}")
        self.game.screen.blit(self.lives.obj, (10,10))
        self.game.screen.blit(self.score.obj, (self.game.w - self.score.w, 10))

    def update_objects(self):
        for enemy in self.game.enemies:
            enemy.move()
        for laser in self.game.lasers:
            laser.move()
        self.check_for_collisions()
        for obj in self.game.objects:
            obj.draw()

    def check_for_collisions(self):
        for obj in self.game.objects:
            obj.check_for_collisions()
        for obj in self.game.objects:
            if obj.collided:
                obj.remove()

    def main_loop(self):
        log_event("Loop", self)
        logging.info("Game Objects: 	     Objects \t Enemies \t Lasers")
        while self.game.get_state() == "Play":
            self.game.check_events_for_quit()
            self.game.draw_background()
            self.key_bindings()
            self.spawn_enemies()
            self.update_objects()
            self.draw_labels()
            self.game.screen_update()

'''-----------------------------------------------------------------------------'''

class Start_Menu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.options = []
        self.set_menu_options()
        self.set_geometry()

    def __str__(self):
        return str(type(self))

    # --------------------------------------------------------------------------

    def set_menu_options(self):
        self.add_menu_option(   "Start Game",
                                self.game.set_state,
                                "Play")

        self.add_menu_option(   "Exit Game",
                                self.game.set_state,
                                "Exit")

'''-----------------------------------------------------------------------------'''

class Pause_Menu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.options = []
        self.set_menu_options()
        self.set_geometry()

    def __str__(self):
        return str(type(self))

    # --------------------------------------------------------------------------

    def set_menu_options(self):
        self.add_menu_option(   "Resume Game",
                                self.game.set_state,
                                "Play")

        self.add_menu_option(   "Exit Game",
                                self.game.set_state,
                                "Exit")

    # --------------------------------------------------------------------------

'''-----------------------------------------------------------------------------
    MAIN PROGRAM'''

class Program(Py_Game):
    def __init__(self, screen_width, screen_height, fps):
        super().__init__(screen_width, screen_height, fps)
        self.set_background(IMG_SPACE)

        self.enemies =              []
        self.lasers =               []
        self.menu_padding =         MENU_PADDING
        self.text_box_color =       TEXT_BOX_COLOR
        self.font_color =           WHITE

        self.start_menu =           Start_Menu(self)
        self.pause_menu =           Pause_Menu(self)
        self.session =              Game(self)

        self.draw_background()
        self.screen_update()
        pygame.display.set_caption("Space Invaders!")

        self.set_state("Start")

    # --------------------------------------------------------------------------

    def check_state(self):
        self.check_events_for_quit()
        if self.state_is_new == True:
            self.state_is_new = False
            if   self.get_state() == "Start":       self.start_menu.main_loop()
            elif self.get_state() == "Play":        self.session.main_loop()
            elif self.get_state() == "Pause":       self.pause_menu.main_loop()
            elif self.get_state() == "Exit":        pygame.quit()
            elif self.get_state() == "Game Over":   self.game_over()

    def log_obj_counts(self, obj):
        if LOG_OBJECTS:
            count_objects = len(self.objects) -1
            count_enemies = len(self.enemies)
            count_lasers = count_objects - count_enemies
            logging.debug(f"Game Objects: 	     {count_objects} \t\t {count_enemies} \t\t {count_lasers}".replace("\t0","\t "))

'''-----------------------------------------------------------------------------
    MAIN LOOP'''

if __name__ == "__main__":
    playing = True
    while playing:
        g = Program(WIDTH, HEIGHT, FPS)
        g.main_loop()

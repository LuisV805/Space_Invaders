from PyGame_Base import *

'''-----------------------------------------------------------------------------
    CONSTANTS'''

IMG_PLAYER_SHIP =   f"{CURRENT_DIR}\\img\\spaceship_yellow.png"
IMG_AVATAR_SHIP =   f"{CURRENT_DIR}\\img\\spaceship_red.png"
IMG_LASER =         f"{CURRENT_DIR}\\img\\laser.png"
IMG_SPACE =         f"{CURRENT_DIR}\\img\\space.png"

ENEMY_SPAWN_TIME =  70

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

'''-----------------------------------------------------------------------------
    GAME OBJECTS '''

class Avatar(Drawable_Object):
    def __init__(self, game):
        super().__init__(game)
        self.show = True
        self.lasers = []
        self.timer_laser_cooldown = 0
        game.log_obj_counts(self)

    def shoot_laser(self):
        if self.timer_laser_cooldown == 0:
            if len(self.lasers) < self.inventory:
                self.lasers.append(Laser(self.game, self))
                self.timer_laser_cooldown = 10
        else: self.timer_laser_cooldown -= 1

    def set_attributes(self, attributes):
        self.power =                attributes["power"]
        self.speed =                attributes["speed"]
        self.inventory =            attributes["inventory"]
        self.max_health =           attributes["health"]
        self.laser_velocity =       attributes["laser_vel"]
        self.health =               self.max_health

    def draw(self):
        self.game.screen.blit(self.img.file, (self.x, self.y))

class Enemy(Avatar):
    def __init__(self, game):
        super().__init__(game)
        self.set_img(IMG_AVATAR_SHIP, 10)
        self.set_attributes(ENEMY_ATTRIBUTES)
        self.x = self.set_x()
        self.y = -20
        self.set_location(self.x, self.y)
        self.speed = random.randint(1,5)/2
        print("")

    def set_x(self):
        x = random.randint(0,self.x_max)
        overlaps = False
        for enemy in self.game.enemies:
            distance_from_enemy = abs(enemy.x - x)
            enemy_buffer = enemy.w * 2
            if distance_from_enemy < enemy_buffer:
                overlaps = True
                break
        if overlaps:
            self.collided = True
        return x

    def move(self):
        new_y = self.y + self.speed
        if new_y < self.y_max:
            self.y = new_y
        else:
            self.remove()
        x_player = self.game.session.player_1.x
        x_max = self.x + 5
        x_min = self.x - 5
        if x_player > x_min and x_player < x_max:
            laser_armed = random.randint(0,100) % 2 == 0
            if laser_armed:
                self.shoot_laser()

    def remove(self):
        self.game.enemies.remove(self)
        self.game.objects.remove(self)
        self.game.log_obj_counts(self)

class Player(Avatar):
    def __init__(self, game):
        super().__init__(game)
        self.set_img(IMG_PLAYER_SHIP, 10)
        self.set_location(self.game.w/2, self.game.h/2)
        self.set_attributes(PLAYER_ATTRIBUTES)
        self._flip_img()
        self.lives = 5
        self.score = 0
        self.flash_timer =  0

    def _flip_img(self):
        rotated_image = pygame.transform.rotate(self.img.file, 180)
        self.img = rotated_image

    def flash(self):
        if self.flash_timer % 3 == 0:
            if self.show:   self.show = False
            else:           self.show = True
        self.flash_timer += 1
        if self.flash_timer == 30:
            self.flash_timer = 0
            self.show = True

    def draw(self):
        if self.flash_timer > 0: self.flash()
        if self.show:
            self.game.screen.blit(self.img, (self.x, self.y))

    def remove(self):
        self.flash()
        self.lives -= 1
        self.collided = False
        if self.lives == 0:
            self.game.set_state("Game Over")

class Laser(Drawable_Object):
    def __init__(self, game, parent):
        super().__init__(game)
        self.parent_avatar =    parent
        self.speed =            parent.laser_velocity
        self.x =                parent.x + (parent.w/2)
        self.y =                parent.y
        self.set_img(IMG_LASER, 100)
        self.set_location(self.x, self.y)
        game.log_obj_counts(self)
        game.lasers.append(self)

        if self.parent_avatar == game.session.player_1:
            self.y -= self.parent_avatar.h
        else:
            self.y += self.parent_avatar.h

    def move(self):
        new_y = self.y + self.speed
        if self.y_min < new_y and new_y < self.y_max:
            self.y = new_y
        else:
            self.remove()

    def draw(self):
        self.game.screen.blit(self.img.file, (self.x, self.y))

    def remove(self):
        self.parent_avatar.lasers.remove(self)
        self.game.objects.remove(self)
        self.game.lasers.remove(self)
        self.game.log_obj_counts(self)
        if self.collided:
            if self.parent_avatar == self.game.session.player_1:
                self.game.session.player_1.score += 10

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

    def draw_labels(self):
        self.lives = Text_obj(self.game, f"LIVES: {self.player_1.lives}")
        self.score = Text_obj(self.game, f"SCORE: {self.player_1.score}")
        self.game.screen.blit(self.lives.obj, (10,10))
        self.game.screen.blit(self.score.obj, (self.game.w - self.score.w, 10))

    def spawn_enemies(self):
        self.timer_enemy_spawn
        if self.timer_enemy_spawn == self.timer_enemy_spawns_max:
            self.game.enemies.append(Enemy(self.game))
            self.timer_enemy_spawn = 0
        else:
            self.timer_enemy_spawn += 1

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

class Start_Menu(Basic_Start_Menu):
    def __init__(self, game):
        super().__init__(game)
        self.options = []
        self.set_menu_options()
        self.set_geometry()

    def set_menu_options(self):
        self.options.append(Menu_Option(    self.game,
                                            self,
                                            "Start Game",
                                            self.game.set_state,
                                            "Play"))

        self.options.append(Menu_Option(    self.game,
                                            self,
                                            "Exit Game",
                                            self.game.set_state,
                                            "Exit"))

class Pause_Menu(Basic_Pause_Menu):
    def __init__(self, game):
        super().__init__(game)
        self.set_menu_options()

    def set_menu_options(self):
        self.options.append(Menu_Option(    self.game,
                                            self,
                                            "Resume Game",
                                            self.game.set_state,
                                            "Play"))

        self.options.append(Menu_Option(    self.game,
                                            self,
                                            "Exit Game",
                                            self.game.set_state,
                                            "Exit"))

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

    def check_state(self):
        self.check_events_for_quit()
        if self.state_is_new == True:
            self.state_is_new = False
            if   self.get_state() == "Start":       self.start_menu.main_loop()
            elif self.get_state() == "Play":        self.session.main_loop()
            elif self.get_state() == "Pause":       self.pause_menu.main_loop()
            elif self.get_state() == "Exit":        pygame.quit()
            elif self.get_state() == "Game Over":   self.running = False

    def log_obj_counts(self, obj):
        if LOG_OBJECTS:
            count_objects = len(self.objects) -1
            count_enemies = len(self.enemies)
            count_lasers = count_objects - count_enemies
            logging.debug(f"Game Objects: 	     {count_objects} \t\t {count_enemies} \t\t {count_lasers}".replace("\t0","\t "))

'''-----------------------------------------------------------------------------
    MAIN LOOP'''

if __name__ == "__main__":
    pygame.init()
    playing = True
    while playing:
        g = Program(WIDTH, HEIGHT, FPS)
        g.main_loop()

from Game_CodeBase import *

'''-----------------------------------------------------------------------------'''

class Avatar(Drawable_Object):
    def __init__(self, game):
        super().__init__(game)
        self.show = True
        self.lasers = []
        self.timer_laser_cooldown = 0
        game.log_obj_counts(self)

    # --------------------------------------------------------------------------

    def set_attributes(self, attributes):
        self.power =                attributes["power"]
        self.speed =                attributes["speed"]
        self.inventory =            attributes["inventory"]
        self.max_health =           attributes["health"]
        self.laser_velocity =       attributes["laser_vel"]
        self.health =               self.max_health

    def draw(self):
        self.game.screen.blit(self.img.file, (self.x, self.y))

    def shoot_laser(self):
        if self.timer_laser_cooldown == 0:
            if len(self.lasers) < self.inventory:
                self.lasers.append(Laser(self.game, self))
                self.timer_laser_cooldown = 10
        else: self.timer_laser_cooldown -= 1

'''-----------------------------------------------------------------------------'''

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

    # --------------------------------------------------------------------------

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

'''-----------------------------------------------------------------------------'''

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

    # --------------------------------------------------------------------------

    def _flip_img(self):
        rotated_image = pygame.transform.rotate(self.img.file, 180)
        self.img = rotated_image

    def draw(self):
        if self.flash_timer > 0: self.flash()
        if self.show:
            self.game.screen.blit(self.img, (self.x, self.y))

    def flash(self):
        if self.flash_timer % 3 == 0:
            if self.show:   self.show = False
            else:           self.show = True
        self.flash_timer += 1
        if self.flash_timer == 30:
            self.flash_timer = 0
            self.show = True

    def remove(self):
        self.flash()
        self.lives -= 1
        self.collided = False
        if self.lives == 0:
            self.game.set_state("Game Over")

'''-----------------------------------------------------------------------------'''

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
        self.set_direction()

    # --------------------------------------------------------------------------

    def set_direction(self):
        if self.parent_avatar == self.game.session.player_1:
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

'''-----------------------------------------------------------------------------'''

import pygame
import color
import random

from math import inf, isinf, pi, cos, sin
from printable import Printable
from boundedValue import BoundedValue
from animationClass import ParticleExplosion, CircularEffect


class Zombie(Printable):
    object = "Zombie"

    def __init__(self, game, x, y, config):
        self.game = game

        config |= self.game.config.zombies
        self.config = self.game.config.zombies | config

        self.speed = self.config.speed
        self.range = self.config.range
        self.damage = self.config.damage
        self.atk_rate = self.config.atk_rate
        self.size = self.config.size
        self.value = self.config.value
        self.type = self.config.type
        self.experience = self.config.experience
        max_life = config.max_life
        self.life = BoundedValue(max_life, 0, max_life)

        Printable.__init__(self, game, self.config.color, self.size, x, y)

        # Aux parameters
        self.life_expect = max_life
        self.target_lock = False
        self.target = None
        self.tower_reach = False
        self.pause = 0
        self.last_atk = self.game.time
        self.attackers = set()

        # Bar parameters
        self.life_bar_height = self.config.bar.life_bar_height
        self.bar_length = self.config.bar.bar_length
        self.color_bar = self.config.bar.color_bar
        self.color_life_bar = self.config.bar.color_life_bar
        self.color_missing_life_bar = self.config.bar.color_missing_life_bar
        self.bar_y = self.config.bar.bar_y
        self.border_y = self.config.bar.border_y

        self.bar_height = self.life_bar_height + 2 * self.border_y

    @classmethod
    def out_of_view(cls, game):
        if not isinf(game.max_x) and not isinf(game.max_y):
            angle = random.random() * 2 * pi
            longeur = (game.max_x ** 2 + game.max_y ** 2) ** 0.5 + 20
            # x = min(max(longeur * cos(angle), -game.max_x), game.max_x)  Spawn au bords
            # y = min(max(longeur * sin(angle), -game.max_y), game.max_y)  Spawn au bords
            x = longeur * cos(angle)
            y = longeur * sin(angle)
            return cls(game, x, y)

        else:
            print("Can't spawn out of view zombie on infinite map")

    def find_target(self, new_tower=None):
        potential_towers = self.game.towers_set() if new_tower is None else new_tower
        closest, dist_min = (None, inf) if not self.target_lock else (self.target, self.dist(self.target))
        for tower in potential_towers:
            new_dist = tower.dist(self)
            if new_dist < dist_min:
                closest, dist_min = tower, new_dist
        if closest is not None:
            self.target_lock = True
            self.target = closest
            self.target.attackers.add(self)

    def attackers_set(self):
        return set(canon.origin for canon in self.attackers)

    def move(self):
        if self.life > 0:
            if not self.target_lock:
                self.find_target()
            if self.target_lock:
                if not self.tower_reach:
                    dist = self.target.dist(self)
                    if dist > self.target.size + self.range + self.size:
                        self.x += self.speed * self.game.moving_action * (self.target.x - self.x) / dist
                        self.y += self.speed * self.game.moving_action * (self.target.y - self.y) / dist
                    else:
                        self.tower_reach = True
                        self.last_atk = self.game.time
                else:
                    self.attack()

    def attack(self):
        if self.game.time - self.last_atk >= self.atk_rate:
            self.target.life -= self.damage
            if self.target.life <= 0:
                self.target.destroyed()
            self.last_atk = self.game.time

    def life_bar(self):

        x_left = self.x - self.size * self.bar_length / 2
        y_up = self.y + self.size * self.bar_y - self.bar_height / 2

        # BAR BG
        pygame.draw.circle(self.game.screen,
                           self.color_bar,
                           (self.game.view_x(x_left),
                            self.game.view_y(y_up + self.bar_height / 2)),
                           self.bar_height / 2 * self.game.zoom)

        pygame.draw.circle(self.game.screen,
                           self.color_bar,
                           (self.game.view_x(x_left + self.bar_length * self.size),
                            self.game.view_y(y_up + self.bar_height / 2)),
                           self.bar_height / 2 * self.game.zoom)

        pygame.draw.rect(self.game.screen,
                         self.color_bar,
                         [self.game.view_x(x_left),
                          self.game.view_y(y_up),
                          self.bar_length * self.size * self.game.zoom,
                          self.bar_height * self.game.zoom])

        # LIFE BAR
        pygame.draw.rect(self.game.screen,
                         self.color_missing_life_bar,
                         [self.game.view_x(x_left),
                          self.game.view_y(y_up + self.border_y),
                          (self.bar_length * self.size) * self.game.zoom,
                          self.life_bar_height * self.game.zoom])
        pygame.draw.circle(self.game.screen,
                           self.color_missing_life_bar,
                           (self.game.view_x(x_left + self.size * self.bar_length),
                            self.game.view_y(y_up + self.border_y + self.life_bar_height / 2)),
                           self.life_bar_height / 2 * self.game.zoom)
        pygame.draw.circle(self.game.screen,
                           self.color_life_bar,
                           (self.game.view_x(x_left),
                            self.game.view_y(y_up + self.border_y + self.life_bar_height / 2)),
                           self.life_bar_height / 2 * self.game.zoom)
        pygame.draw.rect(self.game.screen,
                         self.color_life_bar,
                         [self.game.view_x(x_left),
                          self.game.view_y(y_up + self.border_y),
                          (self.bar_length * self.size) * self.game.zoom * self.life / self.life.max,
                          self.life_bar_height * self.game.zoom])

        radius = abs(self.life.max / 2 - self.life) / self.life.max * self.life_bar_height
        pygame.draw.ellipse(self.game.screen,
                            self.color_life_bar if self.life >= self.life.max / 2 else self.color_missing_life_bar,
                            [self.game.view_x(
                                x_left + self.size * self.bar_length * self.life / self.life.max - radius),
                             self.game.view_y(y_up + self.border_y),
                             2 * radius * self.game.zoom,
                             self.life_bar_height * self.game.zoom])

    def selected(self):
        self.under_selected()

    def under_selected(self):
        pygame.draw.circle(
            self.screen,
            color.LIGHT_GREY,
            (self.view_x(), self.view_y()),
            (self.size + self.range) * self.game.zoom,
            1,
        )
        self.life_bar()

    def killed(self):
        for tower in self.attackers:
            tower.erase_target(self)
        self.target.attackers.discard(self)
        self.game.zombies_bin.add(self)
        self.game.zombies_soon_dead.discard(self)
        self.game.money_prize(self.value)
        if self.game.selected == self:
            self.game.unselect()
        self.kill_animation()

    def kill_animation(self):
        self.game.new_animations.add(ParticleExplosion(self))

    def __str__(self):
        return f"Zombie ({self.type}) at x: {self.x:.1f}, y: {self.y:.1f}"

    def info(self):
        sep = "\n\t\t\t"
        return (
            f"\t\tZombie   (type : {self.type})"
            f"\nStats:"
            f"\n\tPosition : {self.x}, {self.y}"
            f"\n\tIn game.zombies : {self in self.game.zombies}"
            f"\n\tIn game.zombies_soon_dead : {self in self.game.zombies_soon_dead}"
            f"\n\tLife : {self.life} / Expect : {self.life_expect} / Max : {self.life.max}"
            f"\n\tSpeed : {self.speed}   (moving : {not self.tower_reach})"
            f"\n\tDamage : {self.damage}"
            f"\n\tRange : {self.range}"
            f"\n\tAtk_rate : {self.atk_rate}"
            f"\n\tValue : {self.value}"
            f"\n"
            f"\nComplement:"
            f"\n\tTarget : {self.target}    (lock : {self.target_lock})"
            f"\n\tAttacker(s) : {sep + sep.join(map(str, self.attackers))}"
            f"\n\tLast Atk : {self.last_atk}"
            f"\n\tSelected : {self.game.selected == self}"
            f"\n\n"
        ) + "\n".join(
            (str(key) + " : " + str(getattr(self, key))) for key in self.__dict__
        )


class SpecialAtkZombie(Zombie):

    def __init__(self, game, x, y, config):
        Zombie.__init__(self, game, x, y, config)
        self.last_special_atk = self.last_atk
        self.pause_time = 0
        self.special_atk_rate = config.special_atk_rate
        self.special_range = config.special_range
        self.special_pause = config.special_pause

        self.spc_bar_height = self.config.bar.special.spc_bar_height
        self.bar_height += self.spc_bar_height + self.border_y * 0.5

        for special_parameter in config.special_parameters:
            setattr(self, special_parameter, config[special_parameter])


    def special_attack(self):
        pass

    def move(self):
        if self.life > 0 and self.game.time > self.pause_time:
            if self.game.time - self.last_special_atk >= self.special_atk_rate:
                self.special_attack()
            Zombie.move(self)

    def selected(self):
        self.complete_bar()

    def complete_bar(self):
        x_left = self.x - self.size * self.bar_length / 2
        y_up = self.y + self.size * self.bar_y - self.bar_height / 2

        # BAR BG
        pygame.draw.circle(self.game.screen,
                           self.color_bar,
                           (self.game.view_x(x_left),
                            self.game.view_y(y_up + self.bar_height / 2)),
                           self.bar_height / 2 * self.game.zoom)

        pygame.draw.circle(self.game.screen,
                           self.color_bar,
                           (self.game.view_x(x_left + self.bar_length * self.size),
                            self.game.view_y(y_up + self.bar_height / 2)),
                           self.bar_height / 2 * self.game.zoom)

        pygame.draw.rect(self.game.screen,
                         self.color_bar,
                         [self.game.view_x(x_left),
                          self.game.view_y(y_up),
                          self.bar_length * self.size * self.game.zoom,
                          self.bar_height * self.game.zoom])

        # SPECIAL BAR
        pygame.draw.rect(self.game.screen,
                         self.color,
                         [self.game.view_x(x_left),
                          self.game.view_y(y_up + 1.5 * self.border_y + self.life_bar_height),
                          self.size * self.bar_length * self.game.zoom * min(1, (
                                      self.game.time - self.last_special_atk) / self.special_atk_rate),
                          self.spc_bar_height * self.game.zoom])
        pygame.draw.circle(self.game.screen,
                           self.color,
                           (self.game.view_x(x_left),
                            self.game.view_y(
                                y_up + 1.5 * self.border_y + self.life_bar_height + self.spc_bar_height / 2)),
                           self.spc_bar_height / 2 * self.game.zoom)
        pygame.draw.circle(self.game.screen,
                           self.color,
                           (self.game.view_x(x_left + self.size * self.bar_length * min(1, (
                                       self.game.time - self.last_special_atk) / self.special_atk_rate)),
                            self.game.view_y(
                                y_up + 1.5 * self.border_y + self.life_bar_height + self.spc_bar_height / 2)),
                           self.spc_bar_height / 2 * self.game.zoom)

        # LIFE BAR
        pygame.draw.rect(self.game.screen,
                         self.color_missing_life_bar,
                         [self.game.view_x(x_left),
                          self.game.view_y(y_up + self.border_y),
                          (self.bar_length * self.size) * self.game.zoom,
                          self.life_bar_height * self.game.zoom])
        pygame.draw.circle(self.game.screen,
                           self.color_missing_life_bar,
                           (self.game.view_x(x_left + self.size * self.bar_length),
                            self.game.view_y(y_up + self.border_y + self.life_bar_height / 2)),
                           self.life_bar_height / 2 * self.game.zoom)
        pygame.draw.circle(self.game.screen,
                           self.color_life_bar,
                           (self.game.view_x(x_left),
                            self.game.view_y(y_up + self.border_y + self.life_bar_height / 2)),
                           self.life_bar_height / 2 * self.game.zoom)
        pygame.draw.rect(self.game.screen,
                         self.color_life_bar,
                         [self.game.view_x(x_left),
                          self.game.view_y(y_up + self.border_y),
                          (self.bar_length * self.size) * self.game.zoom * self.life / self.life.max,
                          self.life_bar_height * self.game.zoom])

        radius = abs(self.life.max / 2 - self.life) / self.life.max * self.life_bar_height
        pygame.draw.ellipse(self.game.screen,
                            self.color_life_bar if self.life >= self.life.max / 2 else self.color_missing_life_bar,
                            [self.game.view_x(
                                x_left + self.size * self.bar_length * self.life / self.life.max - radius),
                             self.game.view_y(y_up + self.border_y),
                             2 * radius * self.game.zoom,
                             self.life_bar_height * self.game.zoom])


class ClassicZombie(Zombie):
    def __init__(self, game, x, y):
        Zombie.__init__(self, game, x, y, game.config.zombies.classic)


class TankZombie(Zombie):
    def __init__(self, game, x, y):
        Zombie.__init__(self, game, x, y, game.config.zombies.tank)


class SpeedyZombie(Zombie):
    def __init__(self, game, x, y):
        Zombie.__init__(self, game, x, y, game.config.zombies.speedy)


class RandomZombie(Zombie):
    def __init__(self, game, x, y):
        Zombie.__init__(self, game, x, y, game.config.zombies.random)


class HealerZombie(SpecialAtkZombie):
    def __init__(self, game, x, y):
        SpecialAtkZombie.__init__(self, game, x, y, game.config.zombies.healer)
        self.alpha_screen = self.game.create_alpha_screen()

    def special_attack(self):
        atk_made = False
        for zombie in self.game.zombies.difference(self.game.zombies_bin):
            if self.dist(zombie) <= self.special_range and zombie.life < zombie.life.max:
                atk_made = True
                zombie.life += self.special_heal
                zombie.life_expect += self.special_heal
                if zombie.life_expect > 0:
                    self.game.zombies_soon_dead.discard(zombie)
                    self.game.zombies.add(zombie)
        if atk_made:
            self.game.animations.add(CircularEffect(self, self.special_range))
            self.last_special_atk = self.game.time
            self.pause_time = self.game.time + self.special_pause


class SpawnerZombie(SpecialAtkZombie):

    def __init__(self, game, x, y):
        SpecialAtkZombie.__init__(self, game, x, y, game.config.zombies.spawner)
        self.alpha_screen = self.game.create_alpha_screen()

    def special_attack(self):
        for _ in range(random.randint(self.config.mini_spawn_num, self.config.maxi_spawn_num)):
            random_angle = 2 * pi * random.random()
            radius = self.special_range * random.random()
            x, y = self.x + cos(random_angle) * radius, self.y + sin(random_angle) * radius
            zombie = self.game.recognize_dico[random.choices(self.spawnable_zombies, self.spawnable_weights)[0]](
                self.game, x, y)
            self.game.spawn_zombie(zombie)

        self.game.animations.add(CircularEffect(self, self.special_range))
        self.last_special_atk = self.game.time
        self.pause_time = self.game.time + self.special_pause


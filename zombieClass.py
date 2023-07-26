import random as rd

from printable import Printable
import color
from math import inf
import time
import pygame
from config import Config


class Zombie(Printable):
    def __init__(self, game, x, y, config, col):
        self.game = game
        # Zombie config
        self.max_life = config.max_life
        self.speed = config.speed
        self.range = config.range
        self.damage = config.damage
        self.atk_rate = config.atk_rate
        self.size = config.size
        self.value = config.value
        self.type = config.type

        Printable.__init__(self, game, col, self.size, self.size, x, y)

        # Aux parameters
        self.life = self.max_life
        self.life_expect = self.max_life
        self.target_lock = False
        self.target = None
        self.stop = False
        self.last_atk = time.time()
        self.attackers = set()

    def find_target(self):
        closest, dist_min = None, inf
        for tow in self.game.attack_towers.symmetric_difference(self.game.attack_towers_bin):
            new_dist = tow.dist(self)
            if new_dist < dist_min:
                closest = tow
                dist_min = new_dist
        if closest is not None:
            self.target_lock = True
            self.target = closest
            self.target.attackers.add(self)

    def move(self):
        if self.life > 0:
            if not self.target_lock:
                self.find_target()
            if self.target_lock:
                if not self.stop:
                    dist = self.target.dist(self)
                    if dist > self.target.size + self.range:
                        self.x += (
                            self.speed
                            * self.game.moving_action
                            * (self.target.x - self.x)
                            / dist
                        )
                        self.y += (
                            self.speed
                            * self.game.moving_action
                            * (self.target.y - self.y)
                            / dist
                        )
                    else:
                        self.stop = True
                        self.last_atk = self.game.time
                else:
                    if self.game.time - self.last_atk >= self.atk_rate:
                        self.target.life -= self.damage
                        if self.target.life <= 0:
                            self.target.destroyed()
                        self.last_atk = self.game.time

    def selected(self):
        self.under_selected()

    def under_selected(self):
        pygame.draw.circle(
            self.screen,
            color.LIGHT_GREY,
            (self.view_x(), self.view_y()),
            self.size * self.game.zoom,
            1,
        )
        pygame.draw.rect(
            self.game.screen,
            color.RED,
            pygame.Rect(
                (self.game.view_x(self.x - self.size / 2)),
                self.game.view_y(self.y + self.size / 1.8),
                self.size * self.game.zoom,
                3 * self.game.zoom,
            ),
        )
        pygame.draw.rect(
            self.game.screen,
            color.GREEN,
            pygame.Rect(
                (self.game.view_x(self.x - self.size / 2)),
                self.game.view_y(self.y + self.size / 1.8),
                (self.size * self.life / self.max_life) * self.game.zoom,
                3 * self.game.zoom,
            ),
        )


    def killed(self):
        for tower in self.attackers:
            tower.erase_target(self)
        self.game.zombies_bin.add(self)
        self.game.zombies_soon_dead.discard(self)
        self.game.money_prize(self.value)
        if self.game.selected == self:
            self.game.selected = None

    # @classmethod
    # def get_random_config(cls, config):
    #     return Config({
    #         name: config.name for name in ["max_life", "speed", "range", "damage", "atk_rate", "size", "value"]
    #     })


    def __str__(self):
        return f"Zombie ({self.type}) at x: {self.x:.1f}, y: {self.y:.1f}"

    def info(self):
        sep = "\n\t\t\t"
        return (f"\t\tZombie   (type : {self.type})"
                f"\nStats:"
                f"\n\tPosition : {self.x}, {self.y}"
                f"\n\tLife : {self.life} / Expect : {self.life_expect} / Max : {self.max_life}"
                f"\n\tSpeed : {self.speed}   (moving : {not self.stop})"
                f"\n\tDamage : {self.damage}"
                f"\n\tRange : {self.range}"
                f"\n\tAtk_rate : {self.atk_rate}"
                f"\n\tValue : {self.value}"
                f"\n"
                f"\nComplement:"
                f"\n\tTarget : {self.target}    (lock : {self.target_lock})"
                f"\n\tAttacker(s) : {sep+sep.join(map(str,self.attackers))}"
                f"\n\tLast Atk : {self.last_atk}"
                f"\n\tSelected : {self.game.selected == self}"
                f"\n\n")


class ClassicZombie(Zombie):
    def __init__(self, game, x, y):
        Zombie.__init__(self, game, x, y, game.config.zombies.classic, color.GREEN)


class TankZombie(Zombie):
    def __init__(self, game, x, y):
        Zombie.__init__(self, game, x, y, game.config.zombies.tank, color.DARK_GREEN)


class SpeedyZombie(Zombie):
    def __init__(self, game, x, y):
        Zombie.__init__(
            self, game, x, y, game.config.zombies.speedy, color.lighter(color.GREEN, 70)
        )


class RandomZombie(Zombie):
    def __init__(self, game, x, y):
        Zombie.__init__(
            self, game, x, y, game.config.zombies.random, color.mix(color.GOLD, color.LIGHT_RED),
        )


# class RandomTanky(Zombie):
#     def __init__(self, game, x, y):
#         c = random.random() * 100
#         Zombie.__init__(
#             self,
#             game,
#             x,
#             y,
#             5000 * c,
#             5 / c,
#             c / 20,
#             c / 2,
#             c / 20,
#             color.mix(color.CREA2, color.CREA3),
#             c / 2,
#             int(c * 100),
#         )
#
#
# class RandomTanky2(Zombie):
#     def __init__(self, game, x, y):
#         c = max(random.random() ** 20, 0.01)
#         Zombie.__init__(
#             self,
#             game,
#             x,
#             y,
#             10000000000 * c**4,
#             1,
#             c * 4,
#             c * 20,
#             c * 4,
#             color.WHITE,
#             c * 1000,
#             int(c * 10000),
#         )

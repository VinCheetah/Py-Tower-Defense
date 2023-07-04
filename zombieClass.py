import random

from printable import Printable
import color
from math import inf
import time
import pygame


class Zombie(Printable):

    def __init__(self, game, x, y, max_life, speed, range_, damage, atk_rate, col, size, value):
        Printable.__init__(self, game, col, size, size, x, y)
        self.size = size
        self.game = game
        self.max_life = max_life
        self.speed = speed
        self.range = range_
        self.damage = damage
        self.atk_rate = atk_rate
        self.life = self.max_life
        self.life_expect = self.max_life
        self.target_lock = False
        self.target = None
        self.stop = False
        self.last_atk = time.time()
        self.value = value

        self.attackers = set()

    def find_target(self):
        closest, dist_min = None, inf
        for tow in self.game.attack_towers:
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
            if not self.stop:
                if not self.target_lock:
                    self.find_target()
                else:
                    dist = self.target.dist(self)
                    if dist > self.target.size + self.range:
                        self.x += self.speed * self.game.moving_action * (self.target.x - self.x) / dist
                        self.y += self.speed * self.game.moving_action * (self.target.y - self.y) / dist
                    else:
                        self.stop = True
                        self.last_atk = self.game.tick
            else:
                if self.game.tick - self.last_atk >= 60 * self.atk_rate:
                    self.target.life -= self.damage
                    if self.target.life <= 0:
                        self.target.destroyed()
                    self.last_atk = self.game.tick

    def under_selected(self):
        pygame.draw.circle(self.screen, color.LIGHT_GREY, (self.view_x(), self.view_y()), self.size*self.game.zoom, 1)
        pygame.draw.rect(self.game.screen, color.RED,
                         pygame.Rect((self.game.view_x(self.x-self.size/2)), self.game.view_y(self.y+self.size/1.8), self.size*self.game.zoom, 3*self.game.zoom))
        pygame.draw.rect(self.game.screen, color.GREEN,
                         pygame.Rect((self.game.view_x(self.x-self.size/2)), self.game.view_y(self.y+self.size/1.8), (self.size * self.life / self.max_life) * self.game.zoom, 3*self.game.zoom))


class ClassicZombie(Zombie):

    def __init__(self, game, x, y):
        Zombie.__init__(self, game, x, y, 200, 0.2, 1, 10, 1, color.GREEN, 10, 50)


class TankZombie(Zombie):

    def __init__(self, game, x, y):
        Zombie.__init__(self, game, x, y, 1000, 0.1, 3, 50, 2, color.DARK_GREEN, 15, 200)


class SpeedyZombie(Zombie):

    def __init__(self, game, x, y):
        Zombie.__init__(self, game, x, y, 200, 1, 2, 20, 1.5, color.lighter(color.GREEN, 70), 13, 100)


class RandomZombie(Zombie):

    def __init__(self, game, x, y):
        Zombie.__init__(self, game, x, y, random.randint(100, 5000), random.randint(1, 20) / 10, 2, random.randint(5,50), random.randint(1, 5), color.mix(color.GOLD, color.LIGHT_RED), random.randint(10, 30), 500)


class RandomTanky(Zombie):

    def __init__(self, game, x, y):
        c = random.random() * 100
        Zombie.__init__(self, game, x, y, 5000*c, 5/c, c/20, c/2, c/20, color.mix(color.CREA2,color.CREA3), c/2, int(c*100))


class RandomTanky2(Zombie):

    def __init__(self, game, x, y):
        c = max(random.random() ** 20, .01)
        Zombie.__init__(self, game, x, y, 10000000000*c**4, 1, c*4, c*20, c*4, color.WHITE, c*1000, int(c*10000))
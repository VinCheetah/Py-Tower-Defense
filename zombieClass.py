import pygame
import color
import random

from math import inf, isinf, pi, cos, sin
from printable import Printable
from boundedValue import BoundedValue
from animationClass import ParticleExplosion, CircularEffect


class Zombie(Printable):
    def __init__(self, game, x, y, config):
        self.game = game
        # Zombie config

        self.speed = config.speed
        self.range = config.range
        self.damage = config.damage
        self.atk_rate = config.atk_rate
        self.size = config.size
        self.value = config.value
        self.type = config.type

        for special_parameter in config.special_parameters:
            setattr(self, special_parameter, config[special_parameter])

        Printable.__init__(self, game, config.color, self.size, x, y)

        # Aux parameters
        max_life = config.max_life
        self.life = BoundedValue(max_life, 0, max_life)
        self.life_expect = max_life
        self.target_lock = False
        self.target = None
        self.tower_reach = False
        self.pause = 0
        self.last_atk = self.game.time
        self.attackers = set()

    @classmethod
    def out_of_view(cls, game):
        if not isinf(game.max_x) and not isinf(game.max_y):
            angle = random.random() * 2 * pi
            longeur = (game.max_x**2 + game.max_y**2) ** 0.5 + 20
            # x = min(max(longeur * cos(angle), -game.max_x), game.max_x)  Spawn au bords
            # y = min(max(longeur * sin(angle), -game.max_y), game.max_y)  Spawn au bords
            x = longeur * cos(angle)
            y = longeur * sin(angle)
            return cls(game, x, y)

        else:
            print("Can't spawn out of view zombie on infinite map")

    def find_target(self, new_tower=None):
        potential_towers = (
            self.game.attack_towers.difference(self.game.attack_towers_bin).union(
                self.game.effect_towers.difference(self.game.effect_towers_bin)
            )
            if new_tower is None
            else new_tower
        )
        closest, dist_min = (
            (None, inf)
            if not self.target_lock
            else (self.target, self.dist(self.target))
        )
        for tow in potential_towers:
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
                if not self.tower_reach:
                    dist = self.target.dist(self)
                    if dist > self.target.size + self.range + self.size:
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
        pygame.draw.rect(
            self.game.screen,
            color.RED,
            pygame.Rect(
                (self.game.view_x(self.x - self.size)),
                self.game.view_y(self.y + self.size * 2 / 1.8),
                2 * self.size * self.game.zoom,
                3 * self.game.zoom,
            ),
        )
        pygame.draw.rect(
            self.game.screen,
            color.GREEN,
            pygame.Rect(
                (self.game.view_x(self.x - self.size)),
                self.game.view_y(self.y + self.size * 2 / 1.8),
                (2 * self.size * self.life / self.life.max) * self.game.zoom,
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
        self.kill_animation()

    def kill_animation(self):
        self.game.new_animations.add(ParticleExplosion(self))

    # @classmethod
    # def get_random_config(cls, config):
    #     return Config({
    #         name: config.name for name in ["max_life", "speed", "range", "damage", "atk_rate", "size", "value"]
    #     })

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


class HealerZombie(Zombie):
    def __init__(self, game, x, y):
        Zombie.__init__(self, game, x, y, game.config.zombies.healer)
        self.last_special_atk = self.last_atk
        self.pause_time = 0
        self.alpha_screen = self.game.create_alpha_screen()

    def move(self):
        if self.life > 0 and self.game.time > self.pause_time:
            if self.game.time - self.last_special_atk >= self.special_atk_rate:
                self.special_attack()
            Zombie.move(self)

    def special_attack(self):
        atk_made = False
        for zombie in self.game.zombies.difference(self.game.zombies_bin):
            if (
                self.dist(zombie) <= self.special_range
                and zombie.life < zombie.life.max
            ):
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

    def selected(self):
        pygame.draw.circle(
            self.game.screen,
            color.lighter(self.game.background_col, 5),
            (self.view_x(), self.view_y()),
            self.special_range * self.game.zoom,
        )
        pygame.draw.circle(
            self.game.screen,
            color.GREEN,
            (self.view_x(), self.view_y()),
            self.special_range * self.game.zoom,
            1,
        )
        Zombie.selected(self)


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

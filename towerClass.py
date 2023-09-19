import random

from printable import Printable
import animationClass
import color
import pygame
from math import pi
from boundedValue import BoundedValue
from canon import Canon


class Tower(Printable):
    def __init__(self, game, x, y, config):
        self.game = game

        config |= self.game.config.towers
        self.config = config

        self.type = config.type
        self.range = config.range
        self.price = config.price
        self.size = config.size
        self.max_life = config.max_life


        self.animation = []

        Printable.__init__(
            self, game, config.color, self.size, game.unview_x(x), game.unview_y(y)
        )

        self.life = BoundedValue(self.max_life, 0, self.max_life)
        self.alive = True

        self.level = 1

        self.level_memory = []

        self.experience_booster = 1

        self.experience = BoundedValue(0, 0, self.level ** 2 * config.experience_level)

        self.new_level_price = self.price * 2

        self.targets = set()
        self.targets_bin = set()
        self.attackers = set()
        self.effecting = set()
        self.animations = set()
        self.post_animations = set()
        self.animations_bin = set()

        self.upgradable_animation = False

        self.life_bar_height = config.bar.life_bar_height
        self.exp_bar_height = config.bar.exp_bar_height
        self.bar_length = config.bar.bar_length
        self.color_bar = config.bar.color_bar
        self.color_life_bar = config.bar.color_life_bar
        self.color_missing_life_bar = config.bar.color_missing_life_bar
        self.color_exp_bar = config.bar.color_exp_bar
        self.bar_y = config.bar.bar_y
        self.border_y = config.bar.border_y

        self.bar_height = self.life_bar_height + self.exp_bar_height + 2.5 * self.border_y

    def check_target(self):
        for target in self.targets:
            if self.dist(target) > self.range:
                self.erase_target(target)

    def erase_target(self, target):
        self.targets_bin.add(target)

    def clean(self):
        if len(self.targets_bin) > 0:
            for target in self.targets_bin:
                self.targets.discard(target)
            self.targets_bin.clear()
        if len(self.animations_bin) > 0:
            for animation in self.animations_bin:
                self.animations.discard(animation)
            self.animations_bin.clear()

    def bar(self):

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


        # EXP BAR
        pygame.draw.rect(self.game.screen,
                         self.color_exp_bar,
                         [self.game.view_x(x_left),
                                     self.game.view_y(y_up + 1.5 * self.border_y + self.life_bar_height),
                                     self.size * self.bar_length * self.game.zoom * self.experience / self.experience.max,
                                     self.exp_bar_height * self.game.zoom])
        pygame.draw.circle(self.game.screen,
                           self.color_exp_bar,
                    (self.game.view_x(x_left),
                           self.game.view_y(y_up + 1.5 * self.border_y + self.life_bar_height + self.exp_bar_height / 2)),
                           self.exp_bar_height / 2 * self.game.zoom)
        pygame.draw.circle(self.game.screen,
                           self.color_exp_bar,
                    (self.game.view_x(x_left + self.size * self.bar_length * self.experience / self.experience.max),
                           self.game.view_y(y_up + 1.5 * self.border_y + self.life_bar_height + self.exp_bar_height / 2)),
                           self.exp_bar_height / 2 * self.game.zoom)


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
                            [self.game.view_x(x_left + self.size * self.bar_length * self.life / self.life.max - radius),
                            self.game.view_y(y_up + self.border_y),
                            2 * radius * self.game.zoom,
                            self.life_bar_height * self.game.zoom])



    def selected(self):
        pygame.draw.circle(
            self.game.screen,
            color.lighter(self.game.background_color, 5),
            (self.view_x(), self.view_y()),
            self.range * self.game.zoom,
        )
        pygame.draw.circle(
            self.game.screen,
            color.LIGHT_GREY,
            (self.view_x(), self.view_y()),
            self.range * self.game.zoom,
            1,
        )

        self.bar()

        for target in self.targets:
            target.under_selected()

    def boost_new_level(self):
        self.range *= 1.3


    def upgrade(self):
        if self.experience.max == self.experience and self.game.transaction(self.new_level_price):
            self.boost_new_level()
            self.upgradable_animation = False
            self.post_animations.clear()
            self.new_level_price *= 2
            self.level += 1
            self.experience.set_value(0)
            self.experience.set_extremum(0, self.level ** 2 * self.config.experience_level)

    def experience_reward(self, amount):
        self.experience += amount * self.experience_booster
        if self.experience.max == self.experience:
            if not self.upgradable_animation:
                self.upgradable_animation = True
                self.post_animations.add(animationClass.UpgradableTower(self))


    def destroyed(self):
        if self.alive:
            self.alive = False
            if self.game.selected == self:
                self.game.selected = None
            for effect_tower in self.effecting:
                effect_tower.targets.discard(self)
            self.destruction_animation()
            self.erase_existence()

    def destruction_animation(self):
        self.game.animations.add(animationClass.ParticleExplosion(self))

    def boost_affecting(self):
        for effect_tower in self.game.effect_towers:
            effect_tower.check_boost(self, self.effect_type)

    def animate_bop(self):
        self.game.new_animations.add(animationClass.TowerBop(self))

    def under_selected(self):
        pygame.draw.circle(
            self.game.screen,
            color.LIGHT_GREY,
            (self.view_x(), self.view_y()),
            2 * self.size * self.game.zoom,
            1,
        )

    def __str__(self):
        return f"Tower ({self.type}) at x: {self.x:.1f}, y: {self.y:.1f}"

    def info(self):
        sep = "\n\t\t\t"
        return (
            f"\t\tTower   (type : {self.type})"
            f"\nStats:"
            f"\n\tPosition : {self.x}, {self.y}"
            f"\n\tLife : {self.life} / Max : {self.max_life}"
            f"\n\tRange : {self.range}"
            f"\n\tPrice : {self.price}"
            f"\n"
            f"\nComplement:"
            f"\n\tTarget(s) : {sep+sep.join(map(str,self.targets))}"
            f"\n\tAttacker(s) : {sep+sep.join(map(str,self.attackers))}"
            f"\n\tEffecting : {sep+sep.join(map(str,self.effecting))}"
            f"\n\tSelected : {self.game.selected == self}"
            f"\n\n"
            + "\n".join(
                (str(key) + " : " + str(getattr(self, key))) for key in self.__dict__
            )
        )

    def print_game(self):
        for animation in self.animations:
            animation.anime()
        Printable.print_game(self)
        for animation in self.post_animations:
            animation.anime()

    def get_super(self):
        return super()


class AttackTower(Tower):
    effect_type = 2

    def __init__(self, game, x, y, config):
        Tower.__init__(self, game, x, y, config)

        self.num_targets = config.num_targets
        self.damage = config.damage
        self.atk_rate = config.atk_rate

        random_angle = random.random() * 2 * pi
        self.active_canons = set()
        self.canon_speed = 0.03
        self.inactive_canons = set(
            Canon(self, random_angle + 2 * i * pi / self.num_targets)
            for i in range(self.num_targets)
        )
        self.active_canons_bin = set()

        self.attack = config.attack
        self.targets_lock = False
        self.last_attack = self.game.time

        self.boost_affecting()

    def find_target(self):
        distances = sorted(
            [
                (self.dist(zombie), zombie)
                for zombie in self.game.zombies.difference(self.game.zombies_soon_dead)
                .difference(self.targets)
                .difference(self.targets_bin)
                if self.dist(zombie) <= self.range
            ],
            key=lambda x: x[0],
        ) + sorted(
            [(self.dist(zombie), zombie) for zombie in self.targets], key=lambda x: x[0]
        )
        for i in range(min(len(distances), len(self.inactive_canons))):
            self.targets.add(distances[i][1])
            canon = self.inactive_canons.pop()
            canon.new_target(distances[i][1])
            self.active_canons.add(canon)
        if len(self.active_canons) == self.num_targets:
            self.targets_lock = True

    def tow_attack(self):
        self.check_target()
        if not self.targets_lock:
            self.find_target()
        for canon in self.active_canons:
            canon.action()
        for canon in self.inactive_canons:
            if not canon.inactive:
                canon.rotate_home()

        # if (
        #     len(self.targets) != 0
        #     and (self.game.time - self.last_attack) > self.atk_rate
        # ):
        #     self.animations.add(TowerBop(self))
        #     for target in self.targets:
        #         if target.life_expect > 0:
        #             target.life_expect -= self.damage
        #             target.attackers.add(self)
        #             self.game.attacks.add(self.attack(self.game, target, self))
        #             if target.life_expect <= 0:
        #                 self.game.zombies_soon_dead.add(target)
        #                 for attacker in target.attackers:
        #                     attacker.erase_target(target)
        #         else:
        #             self.erase_target(target)
        #     self.last_attack = self.game.time

    def erase_target(self, target):
        Tower.erase_target(self, target)
        self.targets_lock = False

    def erase_existence(self):
        self.game.attack_towers_bin.add(self)
        for zombie in self.attackers:
            zombie.target_lock = False
            zombie.target = None
            zombie.tower_reach = False

    def print_game(self):
        for canon in self.inactive_canons:
            canon.print_game()
        for canon in self.active_canons:
            canon.print_game()
        Tower.print_game(self)

    def clean(self):
        Tower.clean(self)
        if len(self.active_canons_bin) > 0:
            for active_canon in self.active_canons_bin:
                self.active_canons.discard(active_canon)
            self.active_canons_bin.clear()

    def selected(self):
        Tower.selected(self)

        for target in self.game.zombies_soon_dead:
            if self in target.attackers:
                target.under_selected()


class EffectTower(Tower):
    effect_type = 0

    def __init__(self, game, x, y, config):
        Tower.__init__(self, game, x, y, config)

        self.target_type = config.target_type
        self.power_up_factor = config.power_up_factor
        self.alpha_screen = self.game.create_alpha_screen()

        # self.init_effecting()
        # 0 is for effect_towers | 1 is for all towers | 2 is for attack_towers

    def animate_boost(self):
        self.game.new_animations.add(animationClass.CircularEffect(self, self.range))

    def init_effecting(self):
        self.find_target()
        self.signal_targets()
        self.boost_affecting()

    def find_target(self):
        if self.target_type > 0:
            for tower in self.game.attack_towers:
                if self.dist(tower) <= self.range:
                    self.targets.add(tower)
        if self.target_type < 2:
            for tower in self.game.effect_towers:
                if self.dist(tower) <= self.range:
                    self.targets.add(tower)

    def signal_targets(self):
        self.animate_boost()
        for tower in self.targets:
            tower.animate_bop()
            self.start_boost(tower)
            tower.effecting.add(self)

    def erase_existence(self):
        self.game.effect_towers_bin.add(self)
        for tower in self.targets:
            self.stop_boost(tower)

    def check_boost(self, tower, tower_type):
        if self.dist(tower) <= self.range:
            if abs(tower_type - self.target_type) <= 1:
                self.animate_boost()
                tower.animate_bop()
                self.targets.add(tower)
                self.start_boost(tower)
                tower.effecting.add(self)


class DamageBoostTower(EffectTower):
    def __init__(self, game, x, y):
        EffectTower.__init__(self, game, x, y, game.config.effect_towers.damage)

    def start_boost(self, tower):
        tower.damage *= self.power_up_factor

    def stop_boost(self, tower):
        tower.damage /= self.power_up_factor


class AtkRateBoostTower(EffectTower):
    def __init__(self, game, x, y):
        EffectTower.__init__(self, game, x, y, game.config.effect_towers.atkrate)

    def start_boost(self, tower):
        tower.atk_rate /= self.power_up_factor

    def stop_boost(self, tower):
        tower.damage /= self.power_up_factor


class RangeBoostTower(EffectTower):
    def __init__(self, game, x, y):
        EffectTower.__init__(self, game, x, y, game.config.effect_towers.range)

    def start_boost(self, tower):
        tower.range *= self.power_up_factor

    def stop_boost(self, tower):
        tower.range /= self.power_up_factor


class CanonSpeedBoostTower(EffectTower):
    def __init__(self, game, x, y):
        EffectTower.__init__(self, game, x, y, game.config.effect_towers.canon_speed)

    def start_boost(self, tower):
        tower.canon_speed *= self.power_up_factor

    def stop_boost(self, tower):
        tower.canon_speed /= self.power_up_factor


class HomeTower(AttackTower):
    def __init__(self, game):
        AttackTower.__init__(
            self, game, game.width / 2, game.height / 2, game.config.attack_towers.home
        )
        self.alpha_screen = self.game.create_alpha_screen()

    def destruction_animation(self):
        self.game.animations.add(animationClass.CircularExplosion(self))


class ArcheryTower(AttackTower):
    def __init__(self, game, x, y):
        AttackTower.__init__(self, game, x, y, game.config.attack_towers.archery)


class MagicTower(AttackTower):
    def __init__(self, game, x, y):
        AttackTower.__init__(self, game, x, y, game.config.attack_towers.magic)


class BombTower(AttackTower):
    def __init__(self, game, x, y):
        AttackTower.__init__(self, game, x, y, game.config.attack_towers.bomb)
        self.alpha_screen = self.game.create_alpha_screen()

    def damaging(self):
        for potential_target in self.game.zombies:
            if (
                self.target.dist(potential_target) <= self.range
                and potential_target != self.target
            ):
                potential_target.life_expect -= self.origin.damage
                potential_target.life -= self.origin.damage
                if potential_target.life <= 0:
                    potential_target.killed()

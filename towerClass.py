from printable import Printable
import attackClass
import color
import pygame
import math
import animationClass


class Tower(Printable):

    def __init__(self, game, x, y, image, size, rng, price, life):
        Printable.__init__(self, game, image, size, size, game.unview_x(x), game.unview_y(y))

        self.range = rng
        self.price = price
        self.size = size
        self.max_life = life
        self.life = self.max_life
        self.game = game

        self.targets = set()
        self.targets_bin = set()

        self.attackers = set()
        self.effecting = set()

        self.game.unlock_zombies_target()

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

    def selected(self):
        pygame.draw.circle(self.game.screen, color.lighter(self.game.background_col, 5), (self.view_x(), self.view_y()),
                           self.range * self.game.zoom)
        pygame.draw.circle(self.game.screen, color.LIGHT_GREY, (self.view_x(), self.view_y()),
                           self.range * self.game.zoom, 1)
        pygame.draw.rect(self.game.screen, color.RED,
                         pygame.Rect((self.game.view_x(self.x - self.size / 2)),
                                     self.game.view_y(self.y + self.size / 1.8), self.size * self.game.zoom,
                                     5 * self.game.zoom))
        pygame.draw.rect(self.game.screen, color.GREEN,
                         pygame.Rect((self.game.view_x(self.x - self.size / 2)),
                                     self.game.view_y(self.y + self.size / 1.8),
                                     (self.size * self.life / self.max_life) * self.game.zoom, 5 * self.game.zoom))
        for target in self.targets:
            target.under_selected()

    def destroyed(self):
        if self.game.selected == self:
            self.game.selected = None
        for effect_tower in self.effecting:
            effect_tower.targets.discard(self)
        self.erase_existence()

    def boost_affecting(self):
        for effect_tower in self.game.effect_towers:
            effect_tower.check_boost(self, self.type)

    def under_selected(self):
        pygame.draw.circle(self.game.screen, color.LIGHT_GREY, (self.view_x(), self.view_y()),
                           self.size * self.game.zoom, 1)


class AttackTower(Tower):
    type = 2

    def __init__(self, game, x, y, image, attack, size, rng, price, life, num_targets, damage, atk_rate):
        Tower.__init__(self, game, x, y, image, size, rng, price, life)
        self.game.attack_towers.add(self)
        self.num_targets = num_targets
        self.damage = damage
        self.atk_rate = atk_rate
        self.attack = attack
        self.targets_lock = False
        self.last_attack = self.game.tick
        self.boost_affecting()

    def find_target(self):
        distances = sorted([(self.dist(zombie), zombie) for zombie in
                            self.game.zombies.difference(self.game.zombies_soon_dead).difference(
                                self.targets).difference(self.targets_bin)],
                           key=lambda x: x[0])
        for i in range(min(len(distances), self.num_targets - len(self.targets))):
            if distances[i][0] <= self.range:
                self.targets.add(distances[i][1])
                distances[i][1].attackers.add(self)
        if len(self.targets) == self.num_targets:
            self.targets_lock = True

    def tow_attack(self):
        self.check_target()
        if not self.targets_lock or len(self.targets) == 0:
            self.find_target()
        for _ in range(1, int((self.game.tick - self.last_attack) / (self.game.original_frame_rate * self.atk_rate))):
            for target in self.targets:
                if target.life_expect > 0:
                    target.life_expect -= self.damage
                    target.attackers.add(self)
                    self.game.attacks.add(self.attack(self.game, target, self))
                    if target.life_expect <= 0:
                        self.game.zombies_soon_dead.add(target)
                        for attacker in target.attackers:
                            attacker.erase_target(target)
                else:
                    self.erase_target(target)
            self.last_attack = self.game.tick

    def erase_target(self, target):
        Tower.erase_target(self, target)
        self.targets_lock = False

    def erase_existence(self):
        self.game.attack_towers_bin.add(self)
        for zombie in self.attackers:
            zombie.target_lock = False
            zombie.stop = False


class EffectTower(Tower):
    type = 0

    def __init__(self, game, x, y, image, size, rng, price, life, target_type):
        Tower.__init__(self, game, x, y, image, size, rng, price, life)
        self.game.effect_towers.add(self)
        self.target_type = target_type
        self.find_target()
        self.affect_targets()
        self.boost_affecting()
        # 0 is for effect_towers | 1 is for all towers | 2 is for attack_towers

    def find_target(self):
        if self.target_type > 0:
            for tower in self.game.attack_towers:
                if self.dist(tower) <= self.range:
                    self.targets.add(tower)
        if self.target_type < 2:
            for tower in self.game.effect_towers:
                if self.dist(tower) <= self.range:
                    self.targets.add(tower)

    def affect_targets(self):
        for tower in self.targets:
            self.start_boost(tower)
            tower.effecting.add(self)

    def erase_existence(self):
        self.game.effect_towers_bin.add(self)
        for tower in self.targets:
            self.stop_boost(tower)

    def check_boost(self, tower, tower_type):
        if self.dist(tower) <= self.range:
            if abs(tower_type - self.target_type) <= 1:
                self.targets.add(tower)
                self.start_boost(tower)
                tower.effecting.add(self)


class DamageBoostTower(EffectTower):
    price = 2000

    def __init__(self, game, x, y):
        self.power_up_value = 2
        EffectTower.__init__(self, game, x, y, color.CREA2, 15, 100, 1000, 200, 2)

    def start_boost(self, tower):
        tower.damage *= self.power_up_value

    def stop_boost(self, tower):
        tower.damage /= self.power_up_value


class AtkRateBoostTower(EffectTower):
    price = 2000

    def __init__(self, game, x, y):
        self.power_up_value = 2
        EffectTower.__init__(self, game, x, y, color.CREA1, 15, 100, 1000, 200, 2)

    def start_boost(self, tower):
        tower.atk_rate /= self.power_up_value

    def stop_boost(self, tower):
        tower.damage /= self.power_up_value


class RangeBoostTower(EffectTower):
    price = 2000

    def __init__(self, game, x, y):
        self.power_up_value = 2
        EffectTower.__init__(self, game, x, y, color.CREA3, 15, 100, 1000, 200, 2)

    def start_boost(self, tower):
        tower.range *= self.power_up_value

    def stop_boost(self, tower):
        tower.range /= self.power_up_value


class HomeTower(AttackTower):

    def __init__(self, game):
        AttackTower.__init__(self, game, game.width / 2, game.height / 2, color.GOLD2, attackClass.HomeAttack, 30, 100,
                             math.inf, 500, 5, 100, .2)

    def destroyed(self):
        Tower.destroyed(self)
        self.game.animations.add(
            animationClass.Explosion(self.game, self.x, self.y, color.GOLD2, self.game.width, 60))


class ArcheryTower(AttackTower):
    price = 1000

    def __init__(self, game, x, y):
        AttackTower.__init__(self, game, x, y, color.VIOLET, attackClass.ArcherAttack, 20, 600, 300, 200, 2, 20, .3)


class MagicTower(AttackTower):
    price = 2000

    def __init__(self, game, x, y):
        AttackTower.__init__(self, game, x, y, color.BLUE, attackClass.MagicAttack, 20, 400, 500, 200, 5, 50, .8)


class BombTower(AttackTower):
    price = 5000

    def __init__(self, game, x, y):
        AttackTower.__init__(self, game, x, y, color.BLACK, attackClass.BombAttack, 20, 700, 1000, 100, 1, 350, 2)

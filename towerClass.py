from printable import Printable
from animationClass import ParticleExplosion
from animationClass import TowerBop
import attackClass
import color
import pygame
import math
import animationClass


class Tower(Printable):
    def __init__(self, game, x, y, config, color):
        self.game = game

        self.type = config.type
        self.range = config.range
        self.price = config.price
        self.size = config.size
        self.max_life = config.max_life

        Printable.__init__(
            self, game, color, self.size, self.size, game.unview_x(x), game.unview_y(y)
        )

        self.life = self.max_life
        self.alive = True

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
        pygame.draw.circle(
            self.game.screen,
            color.lighter(self.game.background_col, 5),
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
        pygame.draw.rect(
            self.game.screen,
            color.RED,
            pygame.Rect(
                (self.game.view_x(self.x - self.size / 2)),
                self.game.view_y(self.y + self.size / 1.8),
                self.size * self.game.zoom,
                5 * self.game.zoom,
            ),
        )
        pygame.draw.rect(
            self.game.screen,
            color.GREEN,
            pygame.Rect(
                (self.game.view_x(self.x - self.size / 2)),
                self.game.view_y(self.y + self.size / 1.8),
                (self.size * self.life / self.max_life) * self.game.zoom,
                5 * self.game.zoom,
            ),
        )
        for target in self.targets:
            target.under_selected()

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
        self.game.animations.add(ParticleExplosion(self.game, self.x, self.y, self.color, self.size))


    def boost_affecting(self):
        for effect_tower in self.game.effect_towers:
            effect_tower.check_boost(self, self.effect_type)

    def under_selected(self):
        pygame.draw.circle(
            self.game.screen,
            color.LIGHT_GREY,
            (self.view_x(), self.view_y()),
            self.size * self.game.zoom,
            1,
        )

    def __str__(self):
        return f"Tower ({self.type}) at x: {self.x:.1f}, y: {self.y:.1f}"


    def info(self):
        sep = "\n\t\t\t"
        return (f"\t\tTower   (type : {self.type})"
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
                f"\n\n")

class AttackTower(Tower):
    effect_type = 2

    def __init__(self, game, x, y, config, color, attack):
        Tower.__init__(self, game, x, y, config, color)

        self.num_targets = config.num_targets
        self.damage = config.damage
        self.atk_rate = config.atk_rate

        self.attack = attack
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
            ],
            key=lambda x: x[0],
        )
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
        if len(self.targets) != 0 and (self.game.time - self.last_attack) > self.atk_rate:
            self.game.animations.add(TowerBop(self.game, self))
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
            self.last_attack = self.game.time

    def erase_target(self, target):
        Tower.erase_target(self, target)
        self.targets_lock = False

    def erase_existence(self):
        self.game.attack_towers_bin.add(self)
        for zombie in self.attackers:
            zombie.target_lock = False
            zombie.target = None
            zombie.stop = False





class EffectTower(Tower):
    effect_type = 0

    def __init__(self, game, x, y, config, color):
        Tower.__init__(self, game, x, y, config, color)

        self.target_type = config.target_type
        self.power_up_factor = config.power_up_factor

        self.init_effecting()
        # 0 is for effect_towers | 1 is for all towers | 2 is for attack_towers

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

    def __init__(self, game, x, y):
        EffectTower.__init__(self, game, x, y, game.config.effect_towers.damage, color.CREA2)

    def start_boost(self, tower):
        tower.damage *= self.power_up_factor

    def stop_boost(self, tower):
        tower.damage /= self.power_up_factor


class AtkRateBoostTower(EffectTower):

    def __init__(self, game, x, y):
        EffectTower.__init__(self, game, x, y, game.config.effect_towers.atkrate, color.CREA1)

    def start_boost(self, tower):
        tower.atk_rate /= self.power_up_factor

    def stop_boost(self, tower):
        tower.damage /= self.power_up_factor


class RangeBoostTower(EffectTower):

    def __init__(self, game, x, y):
        EffectTower.__init__(self, game, x, y, game.config.effect_towers.range, color.CREA3)

    def start_boost(self, tower):
        tower.range *= self.power_up_factor

    def stop_boost(self, tower):
        tower.range /= self.power_up_factor




class HomeTower(AttackTower):
    def __init__(self, game):
        AttackTower.__init__(self, game, game.width/2, game.height/2, game.config.attack_towers.home, color.GOLD2, attackClass.HomeAttack)


    def destruction_animation(self):
        self.game.animations.add(
            animationClass.CircularExplosion(
                self.game, self.x, self.y, color.GOLD2, self.game.width, 60
            )
        )


class ArcheryTower(AttackTower):

    def __init__(self, game, x, y):
        AttackTower.__init__(self, game, x, y, game.config.attack_towers.magic, color.VIOLET, attackClass.ArcherAttack)



class MagicTower(AttackTower):

    def __init__(self, game, x, y):
        AttackTower.__init__(self, game, x, y, game.config.attack_towers.magic, color.BLUE, attackClass.MagicAttack)


class BombTower(AttackTower):

    def __init__(self, game, x, y):
        AttackTower.__init__(self, game, x, y, game.config.attack_towers.bomb, color.BLACK, attackClass.BombAttack)

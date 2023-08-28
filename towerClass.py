import random

from printable import Printable
import animationClass
import attackClass
import color
import pygame
from math import pi
from boundedValue import BoundedValue
from canon import  Canon


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

        self.life = BoundedValue(self.max_life, 0, self.max_life)
        self.alive = True

        self.targets = set()
        self.targets_bin = set()
        self.attackers = set()
        self.effecting = set()
        self.animations = set()
        self.animations_bin = set()

        self.temp = 0

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
        for target in self.game.zombies_soon_dead:
            if self in target.attackers:
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
        self.game.animations.add(
            animationClass.ParticleExplosion(self.game, self.x, self.y, self.color, self.size)
        )

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
            self.size * self.game.zoom,
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
            f"\n\n" + "\n".join((str(key) + " : " + str(getattr(self,key))) for key in self.__dict__)
        )

    def print_game(self):
        for animation in self.animations:
            animation.anime()
        self.width = self.size
        Printable.print_game(self)


class AttackTower(Tower):
    effect_type = 2

    def __init__(self, game, x, y, config, color, attack):
        Tower.__init__(self, game, x, y, config, color)

        self.num_targets = config.num_targets
        self.damage = config.damage
        self.atk_rate = config.atk_rate

        self.active_canons = set()
        random_angle = random.random() * 2 * pi
        self.inactive_canons = set(Canon(self,random_angle + 2 * i * pi / self.num_targets) for i in range(self.num_targets))
        self.active_canons_bin = set()

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
                .difference(self.targets_bin) if self.dist(zombie) <= self.range
            ],
            key=lambda x: x[0],
        ) + sorted([(self.dist(zombie), zombie) for zombie in self.targets])
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
        self.temp += 1
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


class EffectTower(Tower):
    effect_type = 0

    def __init__(self, game, x, y, config, color):
        Tower.__init__(self, game, x, y, config, color)

        self.target_type = config.target_type
        self.power_up_factor = config.power_up_factor
        self.alpha_screen = self.game.create_alpha_screen()

        #self.init_effecting()
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
        EffectTower.__init__(
            self, game, x, y, game.config.effect_towers.damage, color.CREA2
        )

    def start_boost(self, tower):
        tower.damage *= self.power_up_factor

    def stop_boost(self, tower):
        tower.damage /= self.power_up_factor


class AtkRateBoostTower(EffectTower):
    def __init__(self, game, x, y):
        EffectTower.__init__(
            self, game, x, y, game.config.effect_towers.atkrate, color.CREA1
        )

    def start_boost(self, tower):
        tower.atk_rate /= self.power_up_factor

    def stop_boost(self, tower):
        tower.damage /= self.power_up_factor


class RangeBoostTower(EffectTower):
    def __init__(self, game, x, y):
        EffectTower.__init__(
            self, game, x, y, game.config.effect_towers.range, color.CREA3
        )

    def start_boost(self, tower):
        tower.range *= self.power_up_factor

    def stop_boost(self, tower):
        tower.range /= self.power_up_factor


class HomeTower(AttackTower):
    def __init__(self, game):
        AttackTower.__init__(
            self,
            game,
            game.width / 2,
            game.height / 2,
            game.config.attack_towers.home,
            color.GOLD2,
            attackClass.HomeAttack,
        )
        self.alpha_screen = self.game.create_alpha_screen()

    def destruction_animation(self):
        self.game.animations.add(
            animationClass.CircularExplosion(
                self.game, self.x, self.y, color.GOLD2, self.game.width, 60, self
            )
        )


class ArcheryTower(AttackTower):
    def __init__(self, game, x, y):
        AttackTower.__init__(
            self,
            game,
            x,
            y,
            game.config.attack_towers.archery,
            color.VIOLET,
            attackClass.ArcherAttack,
        )


class MagicTower(AttackTower):
    def __init__(self, game, x, y):
        AttackTower.__init__(
            self,
            game,
            x,
            y,
            game.config.attack_towers.magic,
            color.BLUE,
            attackClass.MagicAttack,
        )


class BombTower(AttackTower):
    def __init__(self, game, x, y):
        AttackTower.__init__(
            self,
            game,
            x,
            y,
            game.config.attack_towers.bomb,
            color.BLACK,
            attackClass.BombAttack,
        )
        self.alpha_screen = self.game.create_alpha_screen()





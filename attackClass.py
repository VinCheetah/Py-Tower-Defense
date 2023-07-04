import random

import printable
import color
import animationClass


class Attack(printable.Printable):

    def __init__(self, game, target, origin, col, speed):
        printable.Printable.__init__(self, game, col, 5, 5, origin.x, origin.y)
        self.game = game
        self.speed = speed
        self.target = target
        self.origin = origin

    def move(self):
        self.origin.target_lock = False
        dist = self.dist(self.target)
        if dist < self.speed * self.game.moving_action:
            self.attack_over()
        else:
            self.x += self.speed * self.game.moving_action * (self.target.x - self.x) / dist
            self.y += self.speed * self.game.moving_action * (self.target.y - self.y) / dist

    def kill_zombie(self, zombie):
        for tower in zombie.attackers:
            tower.erase_target(zombie)
        self.game.zombies_bin.add(zombie)
        self.game.zombies_soon_dead.discard(zombie)
        self.game.money_prize(zombie.value)

    def attack_over(self):
        self.game.attacks_bin.add(self)
        self.target.life -= self.origin.damage
        if self.target.life <= 0:
            self.kill_zombie(self.target)


class HomeAttack(Attack):

    def __init__(self, game, target, origin):
        Attack.__init__(self, game, target, origin, color.GOLD2, 3)


class MagicAttack(Attack):

    def __init__(self, game, target, origin):
        Attack.__init__(self, game, target, origin, color.BLUE, 8)


class ArcherAttack(Attack):

    def __init__(self, game, target, origin):
        Attack.__init__(self, game, target, origin, color.darker(color.VIOLET), 6)


class BombAttack(Attack):

    def __init__(self, game, target, origin):
        Attack.__init__(self, game, target, origin, color.BLACK, 3)
        self.range = random.randint(20, 80)

    def attack_over(self):
        Attack.attack_over(self)
        self.game.animations.add(
            animationClass.Explosion(self.game, self.x, self.y, color.RED, self.range, 10, self))

    def damaging(self):
        for potential_target in self.game.zombies:
            if self.target.dist(potential_target) <= self.range and potential_target != self.target:
                potential_target.life_expect -= self.origin.damage
                potential_target.life -= self.origin.damage
                if potential_target.life <= 0:
                    self.kill_zombie(potential_target)

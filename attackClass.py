import random

import printable
import color
import animationClass


class Attack(printable.Printable):
    def __init__(self, game, target, origin, config):
        self.game = game
        self.target = target
        self.origin = origin
        self.config = self.game.config.attacks | config
        self.speed = self.config.speed

        printable.Printable.__init__(self, game, self.config.color, self.config.size, origin.x, origin.y)

    def move(self):
        self.origin.target_lock = False
        dist = self.dist(self.target)
        if dist >= self.speed * self.game.moving_action:
            self.x += (
                self.speed * self.game.moving_action * (self.target.x - self.x) / dist
            )
            self.y += (
                self.speed * self.game.moving_action * (self.target.y - self.y) / dist
            )
        else:
            self.attack_over()

    def attack_over(self):
        self.game.attacks_bin.add(self)
        self.target.life -= self.origin.damage
        if self.target.life == 0:
            self.origin.experience_reward(self.target.experience)
            self.origin.zombie_killed += 1
            self.target.killed()


class HomeAttack(Attack):
    def __init__(self, game, target, origin):
        Attack.__init__(self, game, target, origin, game.config.attacks.home)


class MagicAttack(Attack):
    def __init__(self, game, target, origin):
        Attack.__init__(self, game, target, origin, game.config.attacks.magic)


class ArcheryAttack(Attack):
    def __init__(self, game, target, origin):
        Attack.__init__(self, game, target, origin, game.config.attacks.archery)


class BombAttack(Attack):
    def __init__(self, game, target, origin):
        Attack.__init__(self, game, target, origin, game.config.attacks.bomb)
        self.range = random.randint(20, 80)

    def attack_over(self):
        Attack.attack_over(self)
        self.game.animations.add(animationClass.CircularExplosion(self))

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

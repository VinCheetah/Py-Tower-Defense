import color
import pygame
from math import pi, cos, sin, atan


class Canon:
    def __init__(self, origin, rotation=0):
        self.origin = origin
        self.game = self.origin.game
        self.config = self.game.config.towers.canon
        self.center_x = self.origin.x
        self.center_y = self.origin.y
        self.original_rotation = rotation
        self.rotation = self.original_rotation
        self.width = pi / 4
        self.color = color.mix(self.origin.color, self.config.mix_color)
        self.target = None
        self.target_lock = False
        self.adjusted_aim = False
        self.last_attack = self.game.time
        self.length2 = 1.3
        self.length = 2
        self.width2 = 1
        self.inactive = True
        self.type = "Canon"

    def new_target(self, target):
        self.inactive = False
        target.attackers.add(self)
        self.target = target
        self.target_lock = True

    def action(self):
        if self.target_lock:
            self.aim()


    def angle(self):
        x = self.target.x - self.center_x
        y = self.target.y - self.center_y
        if x > 0:
            return atan(y / x)
        elif x < 0:
            return atan(y / x) + (pi if y >= 0 else -pi)
        else:
            return 0 if y == 0 else pi / 2

    def aim(self):
        target_theta = self.angle()
        if (
                10 * self.origin.canon_speed * self.game.moving_action
                < (self.rotation - target_theta) % (2 * pi)
                < pi
        ):
            self.rotation -= self.origin.canon_speed * self.game.moving_action
        elif 10 * self.origin.canon_speed * self.game.moving_action < (
                self.rotation - target_theta
        ) % (2 * pi):
            self.rotation += self.origin.canon_speed * self.game.moving_action
        else:
            self.rotation = target_theta
            self.attack()

    def attack(self):
        if (self.game.time - self.last_attack) > self.origin.atk_rate:
            if self.target.life_expect > 0:
                self.target.life_expect -= self.origin.damage
                self.game.attacks.add(
                    self.origin.attack(self.game, self.target, self.origin)
                )
                if self.target.life_expect <= 0:
                    self.game.zombies_soon_dead.add(self.target)
                    for attacker in self.target.attackers:
                        attacker.erase_target(self.target)
            else:
                self.origin.erase_target(self.target)
            self.last_attack = self.game.time

    def erase_target(self, target):
        self.origin.active_canons_bin.add(self)
        self.origin.inactive_canons.add(self)
        self.target = None
        self.target_lock = False
        self.origin.erase_target(target)

    def style_display(self):
        pass

    def shape_display(self):
        pygame.draw.polygon(self.game.screen, color.BLACK, self.transforms(self.shape(bigger=True)))
        pygame.draw.polygon(self.game.screen, self.color, self.transforms(self.shape()))

    def print_game(self):
        self.shape_display()
        self.style_display()
        # if self.target_lock:
        #     target_theta = self.target_theta
        #     pygame.draw.line(self.game.screen, (255, 255, 255),
        #                      (self.game.view_x(self.center_x), self.game.view_y(self.center_y)), (
        #                      self.game.view_x(self.center_x + 100 * cos(target_theta)),
        #                      self.game.view_y(self.center_y + 100 * sin(target_theta))))



    def transform(self, point):
        return (self.game.view_x(self.center_x + point[0] * self.origin.size),
                self.game.view_y(self.center_y + point[1] * self.origin.size))

    def transforms(self, points):
        return tuple(self.transform(point) for point in points)

    def shape(self, bigger=False):
        pass

    def rotate_home(self):
        target_theta = self.original_rotation
        if (
                3 * self.origin.canon_speed * self.game.time_speed
                < (self.rotation - target_theta) % (2 * pi)
                < pi
        ):
            self.rotation -= self.origin.canon_speed * self.game.moving_action
        elif 3 * self.origin.canon_speed * self.game.time_speed < (
                self.rotation - target_theta
        ) % (2 * pi):
            self.rotation += self.origin.canon_speed * self.game.moving_action
        else:
            self.rotation = target_theta
            self.inactive = True


class BasicCanon(Canon):

    def __init__(self, origin, rotation=0):
        super().__init__(origin, rotation)

    def shape(self, bigger=False):
        return self.trapeze(bigger)

    def trapeze(self, bigger=False):
        epsilon = bigger * 0.05
        theta1 = self.rotation - self.width / 2 - epsilon
        theta2 = self.rotation + self.width / 2 + epsilon
        theta3 = self.rotation + self.width / 4 + epsilon / 2
        theta4 = self.rotation - self.width / 4 - epsilon / 2
        p1 = cos(theta1), sin(theta1)
        p2 = cos(theta2), sin(theta2)
        p3 = cos(theta3) * (self.length2 + epsilon), sin(theta3) * (
                self.length2 + epsilon
        )
        p4 = cos(theta4) * (self.length2 + epsilon), sin(theta4) * (
                self.length2 + epsilon
        )
        return p1, p2, p3, p4

    def style_display(self):
        p1, p2, p3, p4 = self.shape()
        epsilon = 0.08
        for i in range(self.origin.level - 1):
            rapport = (i + 1) / self.origin.level
            theta = self.rotation - self.width / 2 + rapport * self.width
            p_1 = cos(theta - epsilon), sin(theta - epsilon)
            p_2 = cos(theta + epsilon), sin(theta + epsilon)
            p_3 = p3[0] * (rapport+epsilon) + p4[0] * (1-rapport-epsilon), p3[1] * (rapport+epsilon) + p4[1] * (1-rapport-epsilon)
            p_4 = p3[0] * (rapport - epsilon) + p4[0] * (1-rapport+epsilon), p3[1] * (rapport-epsilon) + p4[1] * (1-rapport+epsilon)
            pygame.draw.polygon(self.game.screen, self.origin.color, self.transforms([p_1, p_2, p_3, p_4]))
            pygame.draw.polygon(self.game.screen, color.BLACK, self.transforms([p_1, p_2, p_3, p_4]), max(1,int(self.game.zoom * .5)))

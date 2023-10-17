import pygame
from math import pi, cos, sin, atan

import color


class Canon:
    def __init__(self, origin, rotation=0):
        self.origin = origin
        self.center_x = self.origin.x
        self.center_y = self.origin.y

        self.game = self.origin.game
        self.config = self.game.config.towers.canon.basics
        self.type = self.config.type
        self.width = self.config.width
        self.length = self.config.length

        self.last_attack = self.game.time
        self.original_rotation = rotation
        self.rotation = self.original_rotation
        self.color = color.mix(self.origin.color, self.config.mix_color)

        self.target = None
        self.target_lock = False
        self.adjusted_aim = False
        self.inactive = True

    def new_target(self, target):
        self.inactive = False
        self.target_lock = True
        target.attackers.add(self)
        self.target = target

    def set_original_rotation(self, rotation):
        self.original_rotation = rotation
        self.inactive = False

    def action(self):
        if self.target_lock:
            self.attack()

    def aim(self):
        theta = self.angle()
        if self.origin.epsi_rotation < (theta - self.rotation) % (2 * pi) < pi:
            self.rotation += self.origin.epsi_rotation
        elif pi <= (theta - self.rotation) % (2 * pi) < 2 * pi - self.origin.epsi_rotation:
            self.rotation -= self.origin.epsi_rotation
        else:
            return True
        return False

    def attack(self):
        if self.aim() and self.game.time - self.last_attack > self.origin.atk_rate:
            if self.target.life_expect > 0:
                self.target.life_expect -= self.origin.damage
                self.game.attacks.add(self.origin.attack(self.game, self.target, self.origin))
                if self.target.life_expect <= 0:
                    self.game.zombies_soon_dead.add(self.target)
                    for attacker in self.target.attackers:
                        attacker.erase_target(self.target)
            else:
                self.erase_target(self.target)
            self.last_attack = self.game.time

    def rotate_home(self):
        theta = self.original_rotation
        if self.origin.epsi_rotation < (theta - self.rotation) % (2 * pi) < pi:
            self.rotation += self.origin.epsi_rotation
        elif pi <= (theta - self.rotation) % (2 * pi) < 2 * pi - self.origin.epsi_rotation:
            self.rotation -= self.origin.epsi_rotation
        else:
            self.rotation = theta
            self.inactive = True

    def erase_target(self, target):
        self.origin.active_canons_bin.add(self)
        self.origin.inactive_canons.add(self)
        self.target = None
        self.target_lock = False
        self.inactive = False
        self.origin.erase_target(target)

    def angle(self):
        x = self.target.x - self.center_x
        y = self.target.y - self.center_y
        if x > 0:
            return atan(y / x)
        elif x < 0:
            return atan(y / x) + (pi if y >= 0 else -pi)
        else:
            return 0 if y == 0 else pi / 2

    def style_display(self):
        pass

    def shape(self, bigger=0):
        pass

    def shape_display(self):
        pygame.draw.polygon(self.game.map_window.window, color.BLACK, self.transforms(self.shape(bigger=1)))
        pygame.draw.polygon(self.game.map_window.window, self.color, self.transforms(self.shape()))

    def print_game(self):
        self.shape_display()
        self.style_display()

    def transform(self, point):
        return (self.game.view_x(self.center_x + point[0] * self.origin.size),
                self.game.view_y(self.center_y + point[1] * self.origin.size))

    def transforms(self, points):
        return tuple(self.transform(point) for point in points)

    def collide(self, x, y):
        return False
        # Not Working
        # p = list(self.transforms(self.shape()))
        # p.append(p[0])
        # c = 0
        # for i in range(len(p)-1):
        #     p1_x, p1_y = p[i][0] - x, p[i][1] - y
        #     p2_x, p2_y = p[i+1][0] - x, p[i+1][1] - y
        #     c += (p1_y * p2_y <= 0 and - (p1_y - (p2_y-p1_y) / (p2_x - p1_x) / p1_x) / (p2_y - p1_y) / (p2_x - p1_x) > 0)
        #     if (p1_y * p2_y <= 0 and - (p1_y - (p2_y-p1_y) / (p2_x - p1_x) / p1_x) / (p2_y - p1_y) / (p2_x - p1_x) > 0):
        #         self.game.show.add(tuple([p[i], p[i+1]]))
        # print(c)
        # return c % 2


class BasicCanon(Canon):

    def shape(self, bigger=0):
        epsilon = bigger * 0.03
        ps = list(self.trapeze(epsilon))

        p_start = [ps[2]]
        p_end = [ps[3]]

        rapport = 0.15 - epsilon
        length = 0.07 + epsilon / 3

        for i in range((self.origin.level - 1) // self.origin.max_sub_level):
            p_s = p_start[-1]
            p_e = p_end[-1]
            p_sn = p_s[0] * (1 - rapport) + p_e[0] * rapport, p_s[1] * (1 - rapport) + p_e[1] * rapport
            p_snn = p_sn[0] + cos(self.rotation) * length, p_sn[1] + sin(self.rotation) * length
            p_en = p_e[0] * (1 - rapport) + p_s[0] * rapport, p_e[1] * (1 - rapport) + p_s[1] * rapport
            p_enn = p_en[0] + cos(self.rotation) * length, p_en[1] + sin(self.rotation) * length

            p_start.append(p_sn)
            p_start.append(p_snn)
            p_end.append(p_en)
            p_end.append(p_enn)

        return ps[:2] + p_start + list(reversed(p_end))

    def trapeze(self, epsilon):
        theta1 = self.rotation - self.width / 2 - epsilon
        theta2 = self.rotation + self.width / 2 + epsilon
        theta3 = self.rotation + self.width / 4 + epsilon / 2
        theta4 = self.rotation - self.width / 4 - epsilon / 2
        p1 = cos(theta1), sin(theta1)
        p2 = cos(theta2), sin(theta2)
        p3 = cos(theta3) * (self.length + epsilon), sin(theta3) * (self.length + epsilon)
        p4 = cos(theta4) * (self.length + epsilon), sin(theta4) * (self.length + epsilon)
        return p1, p2, p3, p4

    def style_display(self):
        p = self.shape(0.5)
        p1, p2, p3, p4 = p[0], p[1], p[2], p[-1]
        epsilon = 0.08
        for i in range((self.origin.level - 1) // self.origin.max_sub_level):
            pygame.draw.line(self.game.map_window.window, color.BLACK, self.transform(p[(i+1) * 2]), self.transform(p[(i+1) * -2 + 1]), int(max(1, self.game.zoom)))
        for i in range((self.origin.level - 1) % self.origin.max_sub_level):
            rapport = (i + 1) / (1 + (self.origin.level - 1) % self.origin.max_sub_level)
            theta = self.rotation - self.width / 1.8 + rapport * self.width / 0.9
            p_1 = cos(theta - epsilon), sin(theta - epsilon)
            p_2 = cos(theta + epsilon), sin(theta + epsilon)
            p_3 = p3[0] * (rapport + epsilon) + p4[0] * (1-rapport - epsilon), p3[1] * (rapport + epsilon) + p4[1] * (1 - rapport-epsilon)
            p_4 = p3[0] * (rapport - epsilon) + p4[0] * (1-rapport + epsilon), p3[1] * (rapport - epsilon) + p4[1] * (1 - rapport+epsilon)
            pygame.draw.polygon(self.game.map_window.window, self.origin.color, self.transforms([p_1, p_2, p_3, p_4]))
            pygame.draw.polygon(self.game.map_window.window, color.BLACK, self.transforms([p_1, p_2, p_3, p_4]), max(1, int(self.game.zoom * .5)))


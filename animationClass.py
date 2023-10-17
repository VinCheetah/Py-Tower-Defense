import pygame
import random

import color
import math_functions
import towerClass

from math import pi, cos, sin


class Animation:

    def from_origin(self, origin, config):
        Animation.__init__(self, origin.game, config, origin.x, origin.y)
        self.origin = origin

    def __init__(self, game, config, x, y):
        self.game = game
        self.config = self.game.config.animation.basics | config

        self.start_time = self.game.time
        self.type = self.config.type
        self.life_time = self.config.life_time
        self.color = self.config.color
        self.screen = self.game.map_window.window
        self.alpha_screen = self.game.map_window.alpha_window

        self.x, self.y = x, y

    def advancement(self):
        return (self.game.time - self.start_time) / self.life_time

    def alpha_color(self, alpha):
        return self.color + tuple([alpha])

    def anime(self):
        pass

    def over(self):
        self.game.animations_bin.add(self)

    def __repr__(self):
        return f"{self.type} at x:{self.x}, y:{self.y}\n"


class CircularExplosion(Animation):
    def __init__(self, origin):
        self.from_origin(origin, origin.game.config.animation.circular_explosion)

        self.color = self.origin.color
        self.expansion_life_time = self.config.expansion_life_time
        self.disappear_life_time = self.config.disappear_life_time
        self.life_time = self.expansion_life_time + self.disappear_life_time

        if isinstance(self.origin, towerClass.HomeTower):
            self.explosion = self.game.complete_destruction
            self.size = self.config.complete_destruction_size / self.game.zoom
        else:
            self.explosion = self.origin.damaging
            self.size = self.origin.range

        self.exploded = False
        self.expansion_factor = self.expansion_life_time / self.life_time
        self.disappear_factor = self.disappear_life_time / self.life_time

    def anime(self):
        advancement = self.advancement()
        if advancement < self.expansion_factor:
            advancement /= self.expansion_factor
            pygame.draw.circle(
                self.screen,
                self.color,
                (self.game.view_x(self.x), self.game.view_y(self.y)),
                self.size * math_functions.root(advancement) * self.game.zoom,
            )
        elif advancement < 1:
            if not self.exploded:
                self.explosion()
                self.exploded = True
            advancement -= self.expansion_factor
            advancement /= self.disappear_factor
            pygame.draw.circle(
                self.alpha_screen,
                self.alpha_color(int(255 * math_functions.decreasing_cube(advancement))),
                (self.game.view_x(self.x), self.game.view_y(self.y)),
                self.size * self.game.zoom,
            )
        else:
            self.over()


class ViewMove(Animation):
    def __init__(self, game, x_end, y_end, zoom_end, speed, tracking=False):
        super().__init__(game, game.config.animation.view_move, 0, 0)
        self.x_end = x_end
        self.y_end = y_end
        self.zoom_end = zoom_end
        self.speed = speed

        self.num_frames = self.config.frames // self.speed

        self.x_move = (self.x_end - self.game.view_center_x) / self.num_frames
        self.y_move = (self.y_end - self.game.view_center_y) / self.num_frames
        self.zoom_move = (self.zoom_end / self.game.zoom) ** (1 / self.num_frames)

        self.frame_count = 0
        self.tracking = tracking
        self.game.tracking = False

    def anime(self):
        if self.frame_count < self.num_frames:
            self.frame_count += 1
            self.game.zoom *= self.zoom_move
            self.game.add_view_coord(self.x_move, self.y_move)

        else:
            self.game.tracking = self.tracking
            self.over()


class Particle(Animation):
    def __init__(self, group, origin):
        self.from_origin(origin, group.config.particle)
        self.group = group
        self.size = self.config.size_factor * origin.size
        self.color = tuple(min(255, max(0, c + int(self.config.color_variation))) for c in origin.color)
        self.original_speed = self.config.speed
        self.speed = self.original_speed
        self.speed_decrease = self.config.speed_decrease
        self.alpha = self.config.alpha
        self.alpha_decrease = self.config.alpha_decrease

        theta = random.random() * 2 * pi
        self.x_move = cos(theta)
        self.y_move = sin(theta)

    def anime(self):
        advancement = self.advancement()
        if advancement <= 1:
            self.x += self.speed * self.x_move * self.game.moving_action
            self.y += self.speed * self.y_move * self.game.moving_action
            self.speed = self.original_speed * (1 - self.speed_decrease * advancement)
            pygame.draw.circle(
                self.alpha_screen,
                self.alpha_color(self.alpha * (1 - self.alpha_decrease * advancement)),
                (self.game.view_x(self.x), self.game.view_y(self.y)),
                self.size * self.game.zoom,
            )
        else:
            self.group.particles_bin.add(self)


class ParticleExplosion(Animation):

    def __init__(self, origin):
        config = origin.game.config.animation.get_val(
            "particle_explosion_zombie" if origin.game.recognize(origin, "zombie") else
            "particle_explosion_tower")
        self.from_origin(origin, config)

        self.particles = set(Particle(self, origin) for _ in range(int(self.config.num_particles)))
        self.particles_bin = set()

    def anime(self):
        if len(self.particles) == 0:
            self.over()
        else:
            for particle in self.particles:
                particle.anime()
            self.clean()

    def clean(self):
        if len(self.particles_bin) > 0:
            for particle in self.particles_bin:
                self.particles.discard(particle)
                del particle
            self.particles_bin.clear()


class TowerBop(Animation):

    def __init__(self, origin):
        self.from_origin(origin, origin.game.config.animation.tower_bop)

        self.original_size = self.origin.original_size
        self.size_increase = self.config.size_increase

    def anime(self):
        advancement = self.advancement()
        if advancement <= 1:
            self.origin.size = self.original_size * (1 + self.size_increase * math_functions.inverse_mid_square(advancement))
        else:
            self.origin.size = self.original_size
            self.over()


class CircularEffect(Animation):

    def __init__(self, origin, size):
        self.from_origin(origin, origin.game.config.animation.circular_effect)
        self.screen = origin.alpha_screen
        self.color = origin.color
        self.size = size
        self.alpha = self.config.alpha

    def anime(self):
        advancement = self.advancement()
        if advancement <= 1:
            self.screen.fill(0)
            alpha = int(self.alpha * math_functions.ql_1_4(advancement))

            pygame.draw.circle(
                self.screen,
                color.make_alpha(color.BLACK, alpha),
                (self.game.view_x(self.x), self.game.view_y(self.y)),
                self.size * self.game.zoom + 1,
            )
            pygame.draw.circle(
                self.screen,
                self.alpha_color(alpha),
                (self.game.view_x(self.x), self.game.view_y(self.y)),
                self.size * self.game.zoom,
            )
            pygame.draw.circle(
                self.screen,
                color.mix(self.color, color.GREY) + tuple([min(255, alpha * 2)]),
                (self.game.view_x(self.x), self.game.view_y(self.y)),
                self.size * self.game.zoom * advancement,
                int(4 * self.game.zoom),
            )
            self.game.map_window.window.blit(self.screen, (0, 0))
        else:
            self.over()


class ShowText(Animation):
    texts = []

    def __init__(self, game, text):
        super().__init__(game, game.config.animation.show_text, 0, 0)
        self.texts.append(self)
        self.text = text

        self.pop_life_time = self.config.pop_life_time
        self.shade_life_time = self.config.shade_life_time
        self.color = self.config.color
        self.policy = self.config.policy
        self.max_size = self.config.max_size
        self.anti_alias = self.config.anti_alias

        self.size = max(self.config.min_size, min(self.max_size, self.max_size - len(text) / 5 + 20))
        self.font = pygame.font.SysFont(self.policy, self.size)
        self.pop_factor = self.pop_life_time / self.life_time
        self.shade_factor = self.shade_life_time / self.life_time

    def anime(self):
        advancement = self.advancement()
        if advancement <= self.pop_factor:
            advancement /= self.pop_factor
            text = self.font.render(self.text, self.anti_alias, self.color)
            text.set_alpha(int(math_functions.square(advancement) * 255))
        elif advancement <= 1 - self.shade_factor:
            text = self.font.render(self.text, self.anti_alias, self.color)
        elif advancement <= 1:
            advancement = 1 - self.life_time / self.shade_life_time
            text = self.font.render(self.text, self.anti_alias, self.color)
            text.set_alpha(int(math_functions.decreasing_square(advancement) * 255))
        else:
            self.texts.remove(self)
            self.over()
            return None
        text_rect = text.get_rect()
        text_rect.center = self.game.width // 2, self.game.height // 2 + self.texts.index(self) * 100
        self.game.main_window.window.blit(text, text_rect)


class UpgradableTower(Animation):

    def __init__(self, origin):
        self.from_origin(origin, origin.game.config.animation.upgradable_tower)
        self.size = self.config.size
        self.period = self.config.period
        self.num_shade = self.config.num_shade
        self.max_lightness = self.config.max_lightness
        self.func = staticmethod(math_functions.ql_1_4)

    def anime(self):
        advancement = self.game.time % self.period / self.period
        for shade in range(self.num_shade):
            pygame.draw.circle(self.game.map_window.window, color.lighter_compensative(self.origin.color, shade / self.num_shade * self.max_lightness), self.game.view((self.x, self.y)), int(self.game.zoom * (min(self.origin.size, (2 * self.size + self.origin.size) * self.func(advancement) - shade / self.num_shade * self.size))))
        for shade in range(self.num_shade):
            pygame.draw.circle(self.game.map_window.window, color.lighter_compensative(self.origin.color, (1 - shade / self.num_shade) * self.max_lightness), self.game.view((self.x, self.y)), int(self.game.zoom * (min(self.origin.size, (2 * self.size + self.origin.size) * self.func(advancement) - (1 + shade / self.num_shade) * self.size))))





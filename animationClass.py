import pygame
import random

import color
import math_functions
import towerClass

from math import pi, cos, sin


class Animation:
    def anime(self):
        pass

    def over(self):
        self.game.animations_bin.add(self)

    def __repr__(self):
        return f"{self.type} at x:{self.x}, y:{self.y}\n"


class CircularExplosion(Animation):
    def __init__(self, origin):
        self.game = origin.game
        self.config = self.game.config.animation.circular_explosion
        self.x = origin.x
        self.y = origin.y
        self.color = origin.color
        self.expansion_life_time = self.config.expansion_life_time
        self.disappear_life_time = self.config.disappear_life_time
        self.life_time = self.expansion_life_time + self.disappear_life_time

        if isinstance(origin, towerClass.HomeTower):
            self.explosion = self.game.complete_destruction

            self.size = 2000 * 1 / self.game.zoom
            self.screen = origin.alpha_screen
        else:
            self.explosion = origin.damaging
            self.size = origin.range
            self.screen = self.game.map_window.window

        self.exploded = False
        self.type = "CircularExplosion"

    def anime(self):
        self.screen.fill(0)
        self.life_time -= self.game.moving_action
        if self.life_time > self.disappear_life_time:
            advancement = (
                1
                - (self.life_time - self.disappear_life_time) / self.expansion_life_time
            )
            pygame.draw.circle(
                self.screen,
                self.color + tuple([255]),
                (self.game.view_x(self.x), self.game.view_y(self.y)),
                self.size * math_functions.root(advancement) * self.game.zoom,
            )
        elif self.life_time >= 0:
            if not self.exploded:
                self.explosion()
                self.exploded = True

            advancement = 1 - self.life_time / self.disappear_life_time
            pygame.draw.circle(
                self.screen,
                self.color
                + tuple([int(255 * math_functions.decreasing_cube(advancement))]),
                (self.game.view_x(self.x), self.game.view_y(self.y)),
                self.size * self.game.zoom,
            )
        else:
            self.over()
        self.game.screen.blit(self.screen, (0, 0))


class ViewMove(Animation):
    def __init__(self, game, x_end, y_end, zoom_end, speed, tracking=False):
        self.game = game
        self.x_end = x_end
        self.y_end = y_end
        self.zoom_end = zoom_end

        self.speed = speed

        self.num_frames = 60 // self.speed
        self.c = 0

        self.x, self.y = None, None
        self.x_move = (self.x_end - self.game.view_center_x) / self.num_frames
        self.y_move = (self.y_end - self.game.view_center_y) / self.num_frames
        self.zoom_move = (self.zoom_end / self.game.zoom) ** (1 / self.num_frames)

        self.tracking = tracking
        self.game.tracking = False
        self.type = "ViewMove"

    def anime(self):
        if self.c < self.num_frames:
            self.c += 1
            self.game.zoom *= self.zoom_move
            self.game.add_view_coord(self.x_move, self.y_move)

        else:
            self.game.tracking = self.tracking
            self.over()


class Particle:
    def __init__(self, group, origin):
        self.game = origin.game
        self.config = group.config.particle
        self.x = origin.x
        self.y = origin.y
        self.origin = group
        self.original_life_time = self.config.get_val("life_time")
        self.life_time = self.original_life_time
        self.size = self.config.get_val("size_factor") * origin.size
        self.color = tuple(
            min(
                255,
                max(
                    0,
                    color_comp
                    + self.config.get_val("color_variation", integer_only=True),
                ),
            )
            for color_comp in origin.color
        )
        self.original_speed = self.config.get_val("speed")
        self.original_alpha = self.config.get_val("alpha")
        self.speed = self.original_speed
        self.alpha = self.original_alpha
        theta = random.random() * 2 * pi
        self.x_move = cos(theta)
        self.y_move = sin(theta)
        self.speed_decrease = self.config.get_val("speed_decrease")
        self.alpha_decrease = self.config.get_val("alpha_decrease")
        self.type = "Particle"

    def move(self):
        self.x += self.speed * self.x_move * self.game.moving_action
        self.y += self.speed * self.y_move * self.game.moving_action
        self.speed = self.original_speed * (
            1 - self.speed_decrease * (1 - self.life_time / self.original_life_time)
        )
        self.alpha = self.original_alpha * (
            1 - self.alpha_decrease * (1 - self.life_time / self.original_life_time)
        )
        self.life_time -= self.game.moving_action

    def display(self):
        pygame.draw.circle(
            self.game.map_window.window,
            (self.color[0], self.color[1], self.color[2], int(self.alpha)),
            (self.game.view_x(self.x), self.game.view_y(self.y)),
            self.size * self.game.zoom,
        )

    def clean(self):
        if self.life_time <= 0:
            self.origin.particles_bin.add(self)


class ParticleExplosion(Animation):
    def __init__(self, origin):
        self.game = origin.game
        if self.game.recognize(origin, "zombie"):
            self.config = self.game.config.animation.particle_explosion_zombie
        else:
            self.config = self.game.config.animation.particle_explosion
        self.particles = set(
            Particle(self, origin)
            for _ in range(self.config.get_val("num_particles", integer_only=True))
        )
        self.particles_bin = set()
        self.type = "ParticleExplosion"

    def anime(self):
        if len(self.particles) == 0:
            self.over()
        else:
            for particle in self.particles:
                particle.move()
                particle.display()
                particle.clean()
            self.clean()

    def clean(self):
        if len(self.particles_bin) > 0:
            for particle in self.particles_bin:
                self.particles.discard(particle)
                del particle
            self.particles_bin.clear()


class TowerBop:
    id = 0

    def __init__(self, origin):
        self.id += 1
        self.origin = origin
        self.game = self.origin.game
        self.config = self.game.config.animation.tower_bop
        self.original_life_time = self.config.life_time
        self.life_time = self.original_life_time
        self.original_size = self.origin.original_size
        self.size_increase = self.config.size_increase
        self.type = "TowerBop"

    def anime(self):
        self.life_time -= self.game.moving_action
        if self.life_time >= 0:
            advancement = 1 - self.life_time / self.original_life_time
            self.origin.size = self.original_size * (
                1 + self.size_increase * math_functions.inverse_mid_square(advancement)
            )
        else:
            self.origin.size = self.original_size
            self.game.animations_bin.add(self)


class CircularEffect:
    def __init__(self, origin, size):
        self.game = origin.game
        self.screen = origin.alpha_screen
        self.config = self.game.config.animation.circular_effect
        self.x = origin.x
        self.y = origin.y
        self.color = origin.color
        self.size = size
        self.original_alpha = self.config.alpha
        self.alpha = self.original_alpha
        self.original_life_time = self.config.life_time
        self.life_time = self.original_life_time
        self.type = "CircularEffect"

    def anime(self):
        self.life_time -= self.game.moving_action
        if self.life_time >= 0:
            self.screen.fill(0)
            advancement = 1 - self.life_time / self.original_life_time
            self.alpha = int(self.original_alpha * math_functions.ql_1_4(advancement))

            pygame.draw.circle(
                self.screen,
                (0, 0, 0, self.alpha),
                (self.game.view_x(self.x), self.game.view_y(self.y)),
                self.size * self.game.zoom + 1,
            )
            pygame.draw.circle(
                self.screen,
                (self.color[0], self.color[1], self.color[2], self.alpha),
                (self.game.view_x(self.x), self.game.view_y(self.y)),
                self.size * self.game.zoom,
            )
            pygame.draw.circle(
                self.screen,
                color.mix(self.color, color.GREY) + tuple([min(255, self.alpha * 2)]),
                (self.game.view_x(self.x), self.game.view_y(self.y)),
                self.size * self.game.zoom * advancement,
                int(4 * self.game.zoom),
            )
            self.game.map_window.window.blit(self.screen, (0, 0))
        else:
            self.game.animations_bin.add(self)


class ShowText(Animation):
    policy = "Arial"
    max_size = 40
    fonts_size = dict(
        (str(size), pygame.font.SysFont("Arial", size)) for size in range(1, 101)
    )
    texts = []
    type = "ShowText"
    x, y = 0, 0

    def __init__(self, game, text):
        self.texts.append(self)

        self.game = game
        self.config = self.game.config.animation.show_text
        self.text = text
        self.original_life_time = self.config.life_time
        self.life_time = self.original_life_time
        self.pop_life_time = self.config.pop_life_time
        self.shade_life_time = self.config.shade_life_time
        self.color = self.config.color

        self.size = min(self.max_size, 2 * self.max_size - len(text))
        self.font = self.fonts_size[str(self.size)]

    def anime(self):
        self.life_time -= self.game.moving_action
        if self.life_time >= 0:
            if self.life_time >= self.original_life_time - self.pop_life_time:
                advancement = (
                    self.original_life_time - self.life_time
                ) / self.pop_life_time
                text = self.fonts_size[
                    str(max(1, int(self.size * math_functions.linear(advancement))))
                ].render(self.text, True, self.color)
            elif self.life_time <= self.shade_life_time:
                advancement = 1 - self.life_time / self.shade_life_time
                text = self.font.render(self.text, True, self.color)
                text.set_alpha(int(math_functions.decreasing_square(advancement) * 255))
            else:
                text = self.font.render(self.text, True, self.color)

            text_rect = text.get_rect()
            text_rect.center = self.game.width // 2, self.game.height // 2 + self.texts.index(self) * 100
            self.game.main_window.window.blit(text, text_rect)
        else:
            self.over()
            self.texts.pop(0)


class UpgradableTower(Animation):

    func = staticmethod(math_functions.ql_1_4)
    type = "UpgradableTower"

    def __init__(self, origin):
        self.game = origin.game
        self.origin = origin
        self.config = self.game.config.animation.upgradable_tower
        self.size = self.config.size
        self.time = self.config.time
        self.x = origin.x
        self.y = origin.y
        self.alpha = 100
        self.life_time = 0
        self.num_shade = self.config.num_shade
        self.max_lightness = self.config.max_lightness



    def anime(self):
        self.life_time += self.game.moving_action
        advancement = self.life_time % self.time / self.time
        for shade in range(self.num_shade):
            pygame.draw.circle(self.game.map_window.window, color.lighter_compensative(self.origin.color, shade / self.num_shade * self.max_lightness), (self.game.view_x(self.x), self.game.view_y(self.y)), int(self.game.zoom * (min(self.origin.size, (2 * self.size + self.origin.size) * (self.func)(advancement) - shade / self.num_shade * self.size))))
        for shade in range(self.num_shade):
            pygame.draw.circle(self.game.map_window.window, color.lighter_compensative(self.origin.color, (1 - shade / self.num_shade) * self.max_lightness), (self.game.view_x(self.x), self.game.view_y(self.y)), int(self.game.zoom * (min(self.origin.size, (2 * self.size + self.origin.size) * (self.func)(advancement) - (1 + shade / self.num_shade) * self.size))))





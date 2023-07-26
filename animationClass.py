import pygame
import random
from math import exp, log



class CircularExplosion:
    def __init__(self, game, x, y, color, size, ticks, origin=None):
        self.origin = origin
        self.game = game
        self.ticks = ticks
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.exploded = False
        self.radius = 1
        self.speed = self.size * self.game.moving_action / self.ticks
        self.alpha = 255

    def anime(self):
        if not self.exploded:
            if self.radius + self.speed < self.size:
                self.radius += self.speed
            else:
                self.exploded = True
                self.radius = self.size
                if self.origin is None:
                    self.game.complete_destruction()
                else:
                    self.origin.damaging()
            pygame.draw.circle(
                self.game.alpha_screen,
                self.color,
                (self.game.view_x(self.x), self.game.view_y(self.y)),
                self.radius * self.game.zoom,
            )
        else:
            if self.alpha > 0:
                pygame.draw.circle(
                    self.game.alpha_screen,
                    (self.color[0], self.color[1], self.color[2], int(self.alpha)),
                    (self.game.view_x(self.x), self.game.view_y(self.y)),
                    self.radius * self.game.zoom,
                )
                self.alpha -= 255 / (self.ticks * 3)
            else:
                self.game.animations_bin.add(self)


class ViewMove:
    def __init__(self, game, x_end, y_end, zoom_end, speed, tracking=False):
        self.game = game
        self.x_end = x_end
        self.y_end = y_end
        self.zoom_end = zoom_end

        self.speed = speed

        self.num_frames = 60 // self.speed
        self.c = 0

        self.x_move = (self.x_end - self.game.view_center_x) / self.num_frames
        self.y_move = (self.y_end - self.game.view_center_y) / self.num_frames
        self.zoom_move = (self.zoom_end / self.game.zoom) ** (1 / self.num_frames)

        self.tracking = tracking
        self.game.tracking = False

    def anime(self):
        if self.c < self.num_frames:
            self.c += 1
            self.game.view_center_x += self.x_move
            self.game.view_center_y += self.y_move
            self.game.zoom *= self.zoom_move
        else:
            self.game.tracking = self.tracking
            self.game.animations_bin.add(self)



class Particle:

    def __init__(self, game, config, x, y, origin, color, size):
        self.game = game
        self.config = config
        self.x = x
        self.y = y
        self.origin = origin
        self.original_life_time = self.config.get_val("life_time")
        self.life_time = self.original_life_time
        self.size = self.config.get_val("size_factor") * size
        self.color = tuple(min(255,max(0,color_comp + self.config.get_val("color_variation", integer_only=True))) for color_comp in color)
        self.original_speed = self.config.get_val("speed")
        self.original_alpha = self.config.get_val("alpha")
        self.speed = self.original_speed
        self.alpha = self.original_alpha
        self.x_move = random.uniform(-1,1)
        self.y_move = random.uniform(-1,1)
        self.speed_decrease = self.config.get_val("speed_decrease")
        self.alpha_decrease = self.config.get_val("alpha_decrease")


    def move(self):
        self.x += self.speed * self.x_move * self.game.moving_action
        self.y += self.speed * self.y_move * self.game.moving_action
        self.speed = self.original_speed * (1 - self.speed_decrease * self.life_time / self.original_life_time)
        self.alpha = self.original_alpha * (1 - self.alpha_decrease * self.life_time / self.original_life_time)
        self.life_time -= self.game.moving_action

    def display(self):
        pygame.draw.circle(
            self.game.alpha_screen,
            (self.color[0], self.color[1], self.color[2], int(self.alpha)),
            (self.game.view_x(self.x), self.game.view_y(self.y)),
            self.size * self.game.zoom,
        )

    def clean(self):
        if self.life_time <= 0:
            self.origin.particles_bin.add(self)



class ParticleExplosion:
    def __init__(self, game, x, y, color, size):
        self.game = game
        self.config = self.game.config.animation.particle_explosion
        self.particles = set(Particle(game, self.config.particle, x, y, self, color, size) for _ in range(self.config.get_val("num_particles",integer_only=True)))
        self.particles_bin = set()

    def anime(self):
        if len(self.particles) == 0:
            self.game.animations_bin.add(self)
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
            self.particles_bin.clear



class TowerBop:

    def __init__(self, game, origin):
        self.game = game
        self.origin = origin
        self.config = game.config.animation.tower_bop
        self.x = self.origin.x
        self.y = self.origin.y
        self.original_life_time = self.config.life_time
        self.life_time = self.original_life_time
        self.original_size = self.origin.size / 2
        self.size = self.original_size
        self.size_increase = self.config.size_increase
        self.color = self.origin.color


    def anime(self):
        self.life_time -= self.game.moving_action
        if self.life_time >= 0:
            self.size = self.original_size * (1 + self.size_increase * (1 - abs(2 * self.life_time - self.original_life_time) / self.original_life_time))
            pygame.draw.circle(
                self.game.alpha_screen,
                self.color,
                (self.game.view_x(self.origin.x), self.game.view_y(self.origin.y)),
                self.size * self.game.zoom,
            )
        else:
            self.game.animations_bin.add(self)
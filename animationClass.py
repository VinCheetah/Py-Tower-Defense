import pygame
from math import exp, log


class Explosion:

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
            pygame.draw.circle(self.game.alpha_screen, self.color,
                               (self.game.view_x(self.x), self.game.view_y(self.y)), self.radius * self.game.zoom)
        else:
            if self.alpha > 0:
                pygame.draw.circle(self.game.alpha_screen,
                                   (self.color[0], self.color[1], self.color[2], int(self.alpha)),
                                   (self.game.view_x(self.x), self.game.view_y(self.y)), self.radius * self.game.zoom)
                self.alpha -= 255 / (self.ticks * 3)
            else:
                self.game.animations_bin.add(self)


class ViewMove:

    def __init__(self, game, x_end, y_end, zoom_end, speed):
        self.game = game
        self.x_end = x_end
        self.y_end = y_end
        self.zoom_end = zoom_end

        self.speed = speed

        self.num_frames = 60 // self.speed
        self.c = 0

        self.x_move = (self.x_end - self.game.view_center_x) / self.num_frames
        self.y_move = (self.y_end - self.game.view_center_y) / self.num_frames
        self.zoom_move = (self.zoom_end / self.game.zoom) ** (1/self.num_frames)

    def anime(self):
        if self.c < self.num_frames:
            self.c += 1
            self.game.view_center_x += self.x_move
            self.game.view_center_y += self.y_move
            self.game.zoom *= self.zoom_move
        else:
            self.game.animations_bin.add(self)

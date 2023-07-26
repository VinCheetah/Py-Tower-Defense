import pygame
import os

os.environ["SDL_VIDEO_CENTERED"] = "1"
info = pygame.display.Info()

width, height = info.current_w, info.current_h - 50


class View:
    def __init__(self, controller):
        self.controller = controller

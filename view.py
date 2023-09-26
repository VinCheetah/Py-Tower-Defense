import pygame
import os

os.environ["SDL_VIDEO_CENTERED"] = "1"
info = pygame.display.Info()

width, height = info.current_w, info.current_h - 50


class View:
    def __init__(self, controller):
        self.controller = controller


    def interaction(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.controller.quit()

            if event.type == pygame.VIDEORESIZE:
                self.controller.window_resize()

            if event.type == pygame.KEYDOWN:
                self.controller.key_press(event.type)

            if event.type == pygame.MOUSEBUTTONUP:
                self.controller.button_press(event.button)
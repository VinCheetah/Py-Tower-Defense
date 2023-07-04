import pygame

import color


class Printable(pygame.sprite.Sprite):

    def __init__(self, game, image, width, height, x, y):
        # Initialise la classe Sprite
        super().__init__()
        self.game = game
        self.screen = self.game.screen
        self.color = image
        self.width = width
        self.height = height

        # self.image = pygame.transform.scale(pygame.image.load(image), (im_long, im_larg))
        # self.rect = self.image.get_rect()
        self.x = x
        self.y = y

        # self.rect = pygame.Rect(0, 0, self.width, self.height)
        # self.rect.x, self.rect.y = x - self.width / 2, y - self.height / 2

    def print_game(self):
        pygame.draw.circle(self.screen, self.color, (self.view_x(), self.view_y()), max(1,self.game.zoom*self.width//2))
        pygame.draw.circle(self.screen, color.BLACK, (self.view_x(), self.view_y()), max(1,self.game.zoom*self.width//2)+1, 1)

        # pygame.draw.ellipse(self.screen, self.color, self.rect)
        # pygame.draw.ellipse(self.screen, color.BLACK, self.rect, 1)
        # self.game.screen.blit(self.image, self.rect)

    def show(self):
        pygame.draw.ellipse(self.screen, color.RED, self.rect)
        pygame.draw.ellipse(self.screen, color.BLACK, self.rect, 1)

    def dist(self, printable):
        return pow(pow(printable.x - self.x, 2) + pow(printable.y - self.y, 2), .5)

    def dist_point(self, x, y):
        return pow(pow(x - self.x, 2) + pow(y - self.y, 2), .5)

    def view_x(self):
        return int((self.x - self.game.view_center_x) * self.game.zoom + self.game.width / 2)

    def view_y(self):
        return int((self.y - self.game.view_center_y) * self.game.zoom + self.game.height / 2)
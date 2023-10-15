import pygame

class Wall:

    def __init__(self, game, config, p1, p2):
        self.game = game
        self.config = self.game.config.wall | config
        self.p1 = p1
        self.p2 = p2
        self.b1 = p1
        self.b2 = p2
        self.color = self.config.color


    def display(self):
        pygame.draw.line(self.game.map_window.window, self.color, self.game.view(self.p1), self.game.view(self.p2), max(1, 10 * int(self.game.zoom)))


    def intersect(self, A, B):
        AB = B[0] - A[0], B[1] - A[1]
        CA = A[0] - self.p1[0], A[1] - self.p1[1]
        CB = B[0] - self.p1[0], B[1] - self.p1[1]
        AC = self.p1[0] - A[0], self.p1[1] - A[1]
        AD = self.p2[0] - A[0], self.p2[1] - A[1]
        CD = self.p2[0] - self.p1[0], self.p2[1] - self.p1[1]
        return self.vecto(AB, AC) * self.vecto(AB, AD) < 0 and self.vecto(CD, CA) * self.vecto(CD, CB) < 0

    @staticmethod
    def vecto(p1, p2):
        return p1[0] * p2[1] - p1[1] * p2[0]



    def merge(self, wall):
        for p in [self.p1, self.p2]:
            for p_ in [self.p1, self.p2]:
                pass



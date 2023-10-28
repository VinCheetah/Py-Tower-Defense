import pygame
import color
import math


class Wall:

    auxiliary = set()

    def __init__(self, game, config, p1, p2):
        self.game = game
        self.config = self.game.config.wall | config
        self.p1 = p1
        self.p2 = p2
        self.dist = self.game.dist(self.p1, self.p2)
        self.p1_borders = {self}
        self.p2_borders = {self}
        self.vector = self.p2[0] - self.p1[0], self.p2[1] - self.p1[1]
        self.epsi_p1 = self.p1[0] - self.vector[0] / 20, self.p1[1] - self.vector[1] / 20
        self.epsi_p2 = self.p2[0] + self.vector[0] / 20, self.p2[1] + self.vector[1] / 20
        self.color = self.config.color
        self.merge()
        self.update_extremums_wall()

        self.extremity = None
        self.chain = None


    def update_extremums_wall(self):
        self.game.max_x_wall = max(self.p1[0], self.p2[0], self.game.max_x_wall)
        self.game.min_x_wall = min(self.p1[0], self.p2[0], self.game.min_x_wall)
        self.game.max_y_wall = max(self.p1[1], self.p2[1], self.game.max_y_wall)
        self.game.min_y_wall = min(self.p1[1], self.p2[1], self.game.min_y_wall)


    @classmethod
    def merged(cls, game, config, p1, p2):
        new_wall = cls(game, config, p1, p2)
        for wall in new_wall.game.walls:
            if wall.p1 == new_wall.p1:
                wall.p1_borders.add(new_wall)
                new_wall.p1_borders = wall.p1_borders
            if wall.p1 == new_wall.p2:
                wall.p1_borders.add(new_wall)
                new_wall.p2_borders = wall.p1_borders
            if wall.p2 == new_wall.p1:
                wall.p2_borders.add(new_wall)
                new_wall.p1_borders = wall.p2_borders
            if wall.p2 == new_wall.p2:
                wall.p2_borders.add(new_wall)
                new_wall.p2_borders = wall.p2_borders
        return new_wall

    def borders_set(self):
        return self.p1_borders.union(self.p2_borders)

    def _actu_chain(self, start=True):
        self.auxiliary.add(self)
        p1_chain = [wall for b_wall in self.p1_borders if b_wall not in self.auxiliary for wall in b_wall._actu_chain(False)]
        p2_chain = [wall for b_wall in self.p2_borders if b_wall not in self.auxiliary for wall in b_wall._actu_chain(False)]
        if start:
            self.auxiliary.clear()
        return p1_chain + [self] + p2_chain


    def actu_chain(self):
        self.chain = self._actu_chain()


    def _actu_extremity(self):
        ext = []
        for wall in self.chain:
            if len(wall.p1_borders) == 1:
                ext.append(wall.epsi_p1)
            if len(wall.p2_borders) == 1:
                ext.append(wall.epsi_p2)
        return ext

    def actu_extremity(self):
        self.extremity = self._actu_extremity()

    def destruct(self):
        self.p1_borders.discard(self)
        self.p2_borders.discard(self)
        self.game.walls.discard(self)





        # ext_1, ext_2 = [], []
        # if self not in self.auxiliary:
        #     self.auxiliary.add(self)
        #     if visited_p != self.p1:
        #         if len(self.p1_borders) == 1:
        #             ext_1 = [self.epsi_p1]
        #         else:
        #             ext_1 = [wall for border_wall in self.p1_borders for wall in border_wall.extremity(self.p1)]
        #             print(f"\n\nborder1 : {self.p1_borders}\n  visited :{visited_p}, p1 : {self.p1}\n returned : {ext_1}")
        #     elif visited_p != self.p2:
        #         if len(self.p2_borders) == 1:
        #             ext_2 = [self.epsi_p2]
        #         else:
        #             ext_2 = [wall for border_wall in self.p2_borders for wall in border_wall.extremity(self.p2)]
        #             print(f"\n\nborder2 : {self.p2_borders}\n  visited :{visited_p}, p2 : {self.p2}\n returned : {ext_2}")
        #     print(f"border1 : {self.p1_borders}\nborder2:{self.p2_borders}\n  visited :{visited_p}, p1 : {self.p1}, p2 : {self.p2}\n returned : {ext_1 + ext_2}")
        # return ext_1 + ext_2


    def display(self):
        pygame.draw.circle(self.game.map_window.window, self.color, self.game.view(self.p1), max(1, int(10 * self.game.zoom)))
        pygame.draw.circle(self.game.map_window.window, self.color, self.game.view(self.p2), max(1, int(10 * self.game.zoom)))
        pygame.draw.line(self.game.map_window.window, self.color, self.game.view(self.p1), self.game.view(self.p2), max(1, int(10 * self.game.zoom)))

    def intersect(self, q1, q2):
        return self.game.intersect_seg(self.p1, self.p2, q1, q2)

    def merge(self):
        for wall in self.game.walls:
            if wall.p1 == self.p1:
                wall.p1_borders.add(self)
                self.p1_borders = wall.p1_borders
            elif wall.p1 == self.p2:
                wall.p1_borders.add(self)
                self.p2_borders = wall.p1_borders
            elif wall.p2 == self.p1:
                wall.p2_borders.add(self)
                self.p1_borders = wall.p2_borders
            elif wall.p2 == self.p2:
                wall.p2_borders.add(self)
                self.p2_borders = wall.p2_borders

    def dist_point(self, x, y):
        return self.game.dist_seg_point(self.p1, self.p2, (x, y))

    def dist_segment(self, q1, q2):
        return self.game.dist_seg_seg(self.p1, self.p2, q1, q2)

    def mid(self):
        return (self.p1[0] + self.p2[0]) / 2, (self.p1[1] + self.p2[1]) / 2

    def selected(self):
        pygame.draw.circle(self.game.map_window.window, color.RED, self.game.view(self.p1), max(1, int(10 * self.game.zoom)))
        pygame.draw.circle(self.game.map_window.window, color.RED, self.game.view(self.p2), max(1, int(10 * self.game.zoom)))
        pygame.draw.line(self.game.map_window.window, color.RED, self.game.view(self.p1), self.game.view(self.p2), max(1, int(10 * self.game.zoom)))

    def __repr__(self):
        return f"Wall between ({self.p1[0]:.2f}, {self.p1[1]:.2f}) and ({self.p2[0]:.2f}, {self.p2[1]:.2f})"

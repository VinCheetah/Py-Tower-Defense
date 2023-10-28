import numpy as np
import heapq
import time
import pygame


class Node:
    def __init__(self, x, y, cost, heuristic, parent=None):
        self.x = x
        self.y = y
        self.cost = cost
        self.heuristic = heuristic
        self.parent = parent

    def total_cost(self):
        return self.cost + self.heuristic

    def __lt__(self, other):
        return self.total_cost() < other.total_cost()


def astar(zombie, start, end):
    last_frame = 0
    clock = 0
    open_set = []
    closed_set = set()
    start = Node(start[0], start[1], 0, 0)
    end = Node(end[0], end[1], 0, 0)
    d = 10
    heapq.heappush(open_set, start)


    max_x = max(zombie.game.max_x_wall, start.x, end.x) + 3 * d
    min_x = min(zombie.game.min_x_wall, start.x, end.x) - 3 * d
    max_y = max(zombie.game.max_y_wall, start.y, end.y) + 3 * d
    min_y = min(zombie.game.min_y_wall, start.y, end.y) - 3 * d

    while open_set and zombie.game.running:
        zombie.game.interactions()
        while time.time() - last_frame < clock:
            zombie.game.interactions()
        last_frame = time.time()
        current_node = heapq.heappop(open_set)
        if abs(current_node.x - end.x) <= d and abs(current_node.y - end.y) <= d:
            path = []
            while current_node:
                path.append((current_node.x, current_node.y))
                current_node = current_node.parent
            return path[::-1]

        closed_set.add((current_node.x, current_node.y))

        for dx in [-d, 0, d]:
            for dy in [-d, 0, d]:
                if dx == 0 and dy == 0:
                    continue

                neighbor_x = current_node.x + dx
                neighbor_y = current_node.y + dy

                if not (min_x < neighbor_x < max_x and min_y < neighbor_y < max_y):
                    continue

                stop = False

                for wall in zombie.game.walls:
                    if wall.dist_point(neighbor_x, neighbor_y) < max(d * 1.5, zombie.size):
                        stop = True
                        break

                if stop:
                    continue

                if (neighbor_x, neighbor_y) in closed_set:
                    continue

                neighbor_cost = current_node.cost + np.sqrt(dx ** 2 + dy ** 2)
                neighbor_heuristic = np.sqrt(
                    (neighbor_x - end.x) ** 2 + (neighbor_y - end.y) ** 2
                )
                neighbor = Node(
                    neighbor_x, neighbor_y, neighbor_cost, neighbor_heuristic, current_node
                )

                if (neighbor_x, neighbor_y) not in [(node.x, node.y) for node in open_set]:
                    heapq.heappush(open_set, neighbor)
                else:
                    for node in open_set:
                        if node.x == neighbor.x and node.y == neighbor.y:
                            if node.total_cost() > neighbor.total_cost():
                                open_set.remove(node)
                                open_set.append(neighbor)
                                heapq.heapify(open_set)
        if zombie.game.astar_display:
            zombie.game.display()
            for node in closed_set:
                pygame.draw.circle(zombie.game.screen, (255, 255, 255), zombie.game.view(node), d * .3 * zombie.game.zoom)
            pygame.display.flip()
    return None


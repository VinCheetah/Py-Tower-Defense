import pygame
import os
import time
import gameClass

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
info = pygame.display.Info()

width, height = info.current_w, info.current_h - 50
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.update()

pygame.display.set_caption("Tower Defense")
# pygame.display.set_icon(pygame.image.load("tetris_icon.png"))

spawn = 10
running = True
game = gameClass.Game(screen, width, height)
last_frame = 0

while running:

    game.actu_action()
    game.clean()
    game.display()

    one_loop = False

    while not one_loop or time.time() - last_frame < 1 / game.frame_rate:
        one_loop = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    for _ in range(spawn):
                        game.new_zombie()
                elif event.key == pygame.K_p:
                    game.change_speed(1.5)
                elif event.key == pygame.K_m:
                    game.change_speed(2/3)
                elif event.key == pygame.K_u:
                    game.change_frame_rate(1.2)
                elif event.key == pygame.K_j:
                    game.change_frame_rate(5/6)
                elif event.key == pygame.K_o:
                    game.frame_rate = game.original_frame_rate
                elif event.key == pygame.K_h:
                    game.view_move(0, 0)
                elif event.key == pygame.K_k:
                    game.zoom = game.original_zoom
                elif event.key == pygame.K_i:
                    print(game.game_stats())
                elif event.key == pygame.K_z:
                    spawn *= 5
                elif event.key == pygame.K_a:
                    spawn //= 5
                elif event.key == pygame.K_c:
                    game.complete_destruction()
                elif event.key == pygame.K_DOLLAR:
                    game.money_prize(10000)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 4:
                    game.zoom = min(20, game.zoom * 1.03)
                elif event.button == 5:
                    game.zoom = max(.01, game.zoom / 1.03)
                elif game.buildable:
                    x, y = pygame.mouse.get_pos()
                    for tower in game.attack_towers.union(game.effect_towers):
                        if tower.dist_point(game.unview_x(x), game.unview_y(y)) < tower.size:
                            game.selected = tower
                            game.view_move(tower.x, tower.y,  game.height/(3*tower.range), 1.5)
                            break
                    else:
                        if game.selected is None:
                            if event.button == 1:
                                game.new_attack_tower(x, y)
                            elif event.button == 3:
                                game.new_effect_tower(x, y)
                        elif event.button == 1 or event.button == 3:
                            game.selected = None

        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            x, y = pygame.mouse.get_pos()
            if not game.moving_map:
                game.moving_map = True
                ex_pos_x = x
                ex_pos_y = y
            game.view_center_x -= game.unview_x(x) - game.unview_x(ex_pos_x)
            game.view_center_y -= game.unview_y(y) - game.unview_y(ex_pos_y)
            if x != ex_pos_x or y != ex_pos_y:
                game.buildable = False
            ex_pos_x = x
            ex_pos_y = y
        else:
            if not game.moving_map:
                game.buildable = True
            game.moving_map = False

    pygame.display.flip()
    last_frame = time.time()

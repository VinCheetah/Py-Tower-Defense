import pygame
pygame.init()
import gameClass


game = gameClass.Game()
game.start()

        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         running = False
        #     if event.type == pygame.VIDEORESIZE:
        #         game.actu_dimensions()
        #         game.display()
        #         pygame.display.flip()
        #     elif event.type == pygame.KEYDOWN:
        #         print(event.__dict__)
        #         if event.key == pygame.K_ESCAPE:
        #             running = False
        #         elif event.key == pygame.K_SPACE:
        #             game.spawn_random_zombie(spawn)
        #         elif event.key == pygame.K_p:
        #             game.change_time_speed(1.5)
        #         elif event.key == pygame.K_m:
        #             game.change_time_speed(2 / 3)
        #         elif event.key == pygame.K_u:
        #             game.upgrade_selected()
        #         elif event.key == pygame.K_j:
        #             game.change_frame_rate(-5)
        #         elif event.key == pygame.K_o:
        #             game.frame_rate = game.original_frame_rate
        #         elif event.key == pygame.K_h:
        #             game.view_move(0, 0)
        #         elif event.key == pygame.K_k:
        #             game.zoom = game.original_zoom
        #         elif event.key == pygame.K_i:
        #             if game.selected is not None:
        #                 print(game.selected.info())
        #             else:
        #                 print(game.game_stats())
        #         elif event.key == pygame.K_z:
        #             spawn *= 5
        #         elif event.key == pygame.K_a:
        #             spawn //= 5
        #         elif event.key == pygame.K_g:
        #             game.god_mode()
        #         elif event.key == pygame.K_c:
        #             game.complete_destruction()
        #         elif event.key == pygame.K_DOLLAR:
        #             game.money_prize(10000)
        #         elif event.key == pygame.K_t:
        #             game.pausing()
        #         elif event.key == pygame.K_q:
        #             game.new_window()
        #         elif event.key == pygame.K_r:
        #             game.windows[-1].lock_target()
        #         elif event.key == pygame.K_x:
        #             game.test = not game.test
        #         elif event.key == pygame.K_w:
        #             game.new_wave()
        #         elif event.key == pygame.K_BACKSPACE:
        #             game.delete_selected()
        #         elif event.key == pygame.K_y:
        #             game.selected.experience_reward(1000000)
        #             game.print_text("Exp Boost")
        #     elif event.type == pygame.MOUSEBUTTONUP:
        #         if event.button == 4:
        #             game.zoom_move()
        #         elif event.button == 5:
        #             game.unzoom_move()
        #         elif game.buildable or not game.moving_map:
        #             x, y = pygame.mouse.get_pos()
        #             for zombie in game.zombies:
        #                 if zombie.dist_point(
        #                         game.unview_x(x), game.unview_y(y)
        #                 ) < zombie.size * (1 - int(zombie.tower_reach) / 2):
        #                     game.selected = zombie
        #                     game.view_move(zombie.x, zombie.y, speed=3, tracking=True)
        #                     break
        #             else:
        #                 for tower in game.attack_towers.union(game.effect_towers):
        #                     if (
        #                             tower.dist_point(game.unview_x(x), game.unview_y(y))
        #                             < tower.size
        #                     ):
        #                         game.selected = tower
        #                         game.view_move(
        #                             tower.x,
        #                             tower.y,
        #                             game.height / (3 * tower.range),
        #                             1.5,
        #                         )
        #                         break
        #                 else:
        #                     if game.selected is None:
        #                         if event.button == 1:
        #                             game.new_attack_tower(x, y)
        #                         elif event.button == 3:
        #                             game.new_effect_tower(x, y)
        #                     elif event.button == 1 or event.button == 3:
        #                         game.selected = None
        #
        #
        # game.mouse_actions()

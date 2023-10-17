import pygame
import color
import boundedValue
import controllerClass
import wallClass


class Window:

    def __init__(self, game, config):
        self.game = game
        self.config = game.config.window.basics | config

        self.x = self.config.x
        self.y = self.config.y

        self.view_x = boundedValue.BoundedValue(0, 0, 0)
        self.view_y = boundedValue.BoundedValue(0, 0, 0)

        self.content_height = 0

        self.font = pygame.font.SysFont("Courier New", 20)
        self.width = self.config.width
        self.height = self.config.height
        self.alpha = self.config.alpha
        self.background_color = self.config.background_color
        self.writing_color = self.config.writing_color
        self.name = self.config.name
        self.border_x = self.config.border_x
        self.border_y = self.config.border_y
        self.moveable = self.config.moveable
        self.selectionable = self.config.selectionable
        self.closable = self.config.closable

        self.buttons = set()
        self.controller = self.game.window_controller

        self.window = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.active = True
        self.content = None



    def collide(self, x, y):
        return 0 <= x - self.x <= self.width and 0 <= y - self.y <= self.height

    def collide_old(self):
        return 0 <= self.game.mouse_x - self.x <= self.width and 0 <= self.game.mouse_y - self.y <= self.height


    def window_view_down(self):
        if self.moveable and self.collide_old():
            self.view_y += 4
            return True
        return False

    def window_view_up(self):
        if self.moveable and self.collide_old():
            self.view_y -= 4
            return True
        return False


    def print_window(self):
        self.window.fill(self.background_color)
        pygame.draw.rect(self.window, color.BLACK, [0, 0, self.width, self.height], 1)

        self.update_content()
        self.print_content()

        self.game.screen.blit(self.window, (self.x, self.y))
        self.clean()

    def clean(self):
        self.window.fill(self.background_color)

    def window_blit(self, content, x=0, y=0, loc=[], border_x=None, border_y=None):
        border_x = self.border_x if border_x is None else border_x
        border_y = self.border_y if border_y is None else border_y
        content_width, content_height = content.get_size()
        if "center" in loc:
            x, y = self.width / 2 - content_width / 2, self.height / 2 - content_height
        if "top" in loc:
            y = border_y
        if "bottom" in loc:
            y = self.height - content_height.height / 2 - border_y
        if "left" in loc:
            x = border_x
        if "right" in loc:
            x = self.width - content_width - border_x
        if "over" in loc:
            pygame.draw.rect(self.game.screen, self.background_color,
                             [self.x, self.y + content_height, content_width, content_height])
            self.game.screen.blit(content, (self.x, self.y + content_height))
            return None
        self.window.blit(content, (x, y))

    def update_extremum_view(self):
        self.view_x.set_max(0)
        self.view_y.set_max(max(0, self.content_height - self.content.get_size()[1]))

    def format_text(self, text, font, x_space=5, y_space=5):
        text_surface = pygame.Surface((self.width, self.height))
        text_surface.fill((0, 0, 0))
        space = font.size(' ')[0]
        line = font.size('I')[1]
        min_x, min_y = x_space, y_space
        max_x, max_y = self.width - x_space, self.height - y_space
        x, y = min_x, min_y
        for paragraph in text.split('\n'):
            for paragraph2 in paragraph.split('\t'):
                for word in paragraph2.split(' '):
                    rendered_word = self.font.render(word, 0, self.writing_color)
                    word_width = rendered_word.get_width()
                    if x + word_width >= max_x:
                        x = min_x
                        y += line
                    text_surface.blit(rendered_word, (x - self.view_x, y - self.view_y))

                    x += word_width + space
                x += 4 * space
            y += line
            x = min_x
        return text_surface, y

    def update_content(self):
        pass

    def print_content(self):
        if self.content is not None:
            self.window_blit(self.content)
        for button in self.buttons:
            button.display()

    def move(self, rel_x, rel_y):
        if self.moveable and self.collide_old():
            self.go_front()
            self.x += rel_x
            self.y += rel_y
            return True
        return False

    def go_front(self):
        if self.selectionable and self.game.windows[-1] != self:
            self.game.windows.remove(self)
            self.game.windows.append(self)

    def close(self):
        if self.closable:
            print("CLOSE")
            if self.game.windows[-1] == self:
                self.game.windows.pop()
            else:
                self.game.windows.remove(self)


    def new_button(self, button):
        self.buttons.add(button)
        self.controller.buttons.add(button)


    def select(self, x, y):
        if self.selectionable and self.collide(x, y):
            self.go_front()
            self.controller.activize()
            return True
        return False

class DebugWindow(Window):

    def __init__(self, game, target=None):
        Window.__init__(self, game, game.config.window.debug)
        self.target_lock = target is not None
        self.target = target
        self.parameters = "basics"

    def update_content(self):
        if not self.target_lock and self.game.selected is not None:
            self.target = self.game.selected
        if self.target is not None:
            self.content, self.content_height = self.format_text(self.get_brut_content(), self.font)
            self.update_extremum_view()

    def get_brut_content(self):
        if self.parameters == "all":
            parameters = self.target.__dict__
        elif self.parameters == "basics":
            parameters = self.target.config.basics_parameters
        elif type(self.parameters) == list:
            parameters = self.parameters

        return "\n".join(
            str(key) + (max(0, 10 - len(key)) * " ") + ":  " + self.game.make_str(getattr(self.target, key)) for key in
            parameters if hasattr(self.target, key))

    def get_basics_parameters(self):
        self.parameters = "basics"

    def get_all_parameters(self):
        self.parameters = "all"

    def lock_target(self):
        if self.target is not None:
            self.target_lock = not self.target_lock


class MainWindow(Window):

    def __init__(self, game):
        Window.__init__(self, game, game.config.window.main)

        self.width = self.game.width
        self.height = self.game.height
        self.controller = self.game.main_controller
        # self.new_button(controller)
        #self.window = self.game.screen
        self.window = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def print_window(self):
        self.update_content()
        self.print_content()

        self.game.screen.blit(self.window, (self.x, self.y))
        self.window.fill(0)


    def update_content(self):
        self.money_display()


    def money_display(self):
        money_content = pygame.font.Font(None, 50).render(str(self.game.money), True, color.WHITE)
        money_width, money_height = money_content.get_size()
        pygame.draw.rect(self.window, color.DARK_GREY_2, [self.width - money_width - 2 * self.border_x, 0, money_width + 2 * self.border_x, 2 * self.border_y + money_height])
        self.window_blit(money_content, loc=["top", "right"])


class MapWindow(Window):

    def __init__(self, game):
        Window.__init__(self, game, game.config.window.map)

        self.width = self.game.width
        self.height = self.game.height
        self.controller = self.game.map_controller
        # self.new_button(controller)
        #self.window = self.game.screen
        self.window = pygame.Surface((self.width, self.height))
        self.alpha_window = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def update_content(self):
        self.game.track()

        if self.game.selected is not None and self.game.recognize(self.game.selected, "tower"):
            self.game.selected.selected_background()

        for attack in self.game.attacks:
            attack.print_game()
        for tower in self.game.towers_set():
            tower.print_game()
        for zombie in self.game.zombies:
            zombie.print_game()
        for wall in self.game.walls:
            wall.display()

        if self.game.selected is not None:
            self.game.selected.selected()
            for zombie in self.game.zombies_soon_dead:
                if self.game.selected in zombie.attackers_set():
                    zombie.under_selected()

        for animation in self.game.animations:
            animation.anime()

        for show in self.game.show:
            if type(show) is tuple and type(show[0]) is type(show[1]) is int:
                pygame.draw.circle(self.window, color.RED, show, int(3 * self.game.zoom))
            else:
                pygame.draw.line(self.window, color.RED, show[0], show[1], int(max(3, 2 * self.game.zoom)))


        self.window.blit(self.alpha_window, (0, 0))

    def clean(self):
        super().clean()
        self.alpha_window.fill(0)



class ShopWindow(Window):

    def __init__(self, game):
        Window.__init__(self, game, game.config.window.shop)

        self.width = self.game.width
        self.height = self.game.height - self.y


class BuildWindow(Window):

    def __init__(self, game):
        Window.__init__(self, game, game.config.window.build)

        self.width = self.game.width
        self.height = self.game.height

        self.build1 = None
        self.window = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.build_pos = None


    def update_content(self):
        self.window.fill((0, 0, 0, 50))
        if self.build_pos is None:
            pygame.draw.circle(self.window, color.BLACK, (self.game.mouse_x, self.game.mouse_y), 10 * self.game.zoom)
        else:
            pygame.draw.circle(self.window, color.BLACK, self.build_pos, 10 * self.game.zoom)
        if self.build1 is not None:
            if self.build_pos is None:
                pygame.draw.line(self.window, color.BLACK, self.build1, (self.game.mouse_x, self.game.mouse_y), max(1, int(10*self.game.zoom)))
            else:
                pygame.draw.line(self.window, color.BLACK, self.build1, self.build_pos,
                                 max(1, int(10 * self.game.zoom)))


    def wall_build(self,x ,y):
        if self.build1 is None:
            if self.build_pos is None:
                self.build1 = x, y
            else:
                self.build1 = self.build_pos
        else:
            self.game.walls.add(wallClass.Wall(self.game, {}, self.game.unview(self.build1), self.game.unview((x, y))))
            self.stop_wall_build()
        return True

    def stop_wall_build(self):
        self.build1 = None
        self.game.build_wall_controller.unactivize()


    def check_merge(self, *args):
        x, y = self.game.mouse_x, self.game.mouse_y
        for wall in self.game.walls:
            for p in [wall.p1, wall.p2]:
                if self.game.dist(self.game.view(p), (x, y)) < 50:
                    self.build_pos = self.game.view(p)
                    return True
        self.build_pos = None










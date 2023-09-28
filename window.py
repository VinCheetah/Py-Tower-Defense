import pygame
import color
import boundedValue


class Window:

    def __init__(self, game, config):
        self.game = game
        self.config = game.config.window | config

        self.x = 0
        self.y = 0

        self.view_x = boundedValue.BoundedValue(0, 0, 0)
        self.view_y = boundedValue.BoundedValue(0, 0, 0)

        self.content_height = 0

        self.font = pygame.font.SysFont("Arial", 20)
        self.width = self.config.width
        self.height = self.config.height
        self.background_color = self.config.background_color
        self.writing_color = self.config.writing_color
        self.name = self.config.name

        self.window = pygame.Surface((self.width, self.height), pygame.RESIZABLE)
        self.active = True
        self.content = None

    def collide(self, x, y):
        return 0 <= x - self.x <= self.width and 0 <= y - self.y <= self.height

    def collide_old(self):
        return 0 <= self.game.mouse_x - self.x <= self.width and 0 <= self.game.mouse_y - self.y <= self.height


    def window_view_down(self):
        if self.collide_old():
            self.view_y += 4
            return True
        return False

    def window_view_up(self):
        if self.collide_old():
            self.view_y -= 4
            return True
        return False


    def print_window(self):
        self.window.fill(self.background_color)
        pygame.draw.rect(self.window, color.BLACK, [0, 0, self.width, self.height], 1)
        # Title
        # text = self.font.render(self.name, 0, color.WHITE)
        # self.window_blit(text, loc=["center", "over"], border_y=3)
        # Content
        self.update_content()
        self.print_content()

        self.game.screen.blit(self.window, (self.x, self.y))

    def window_blit(self, content, x=0, y=0, loc=[], border_x=0, border_y=0):
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
        print(self.content_height, self.content.get_size()[1])
        self.view_y.set_max(max(0, self.content_height - self.content.get_size()[1]))
        print(self.view_y)

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

    def move(self, rel_x, rel_y):
        if self.collide_old():
            self.go_front()
            self.x += rel_x
            self.y += rel_y
            return True
        return False

    def go_front(self):
        if self.game.windows[-1] != self:
            self.game.windows.remove(self)
            self.game.windows.append(self)

    def close(self):
        if self.game.windows[-1] == self:
            self.game.windows.pop()
        else:
            self.game.windows.remove(self)


class DebugWindow(Window):

    def __init__(self, game):
        Window.__init__(self, game, game.config.window.debug)
        self.target_lock = False
        self.target = None
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
            str(key) + " :  " + self.game.make_str(getattr(self.target, key)) for key in
            parameters)

    def get_basics_parameters(self):
        self.parameters = "basics"

    def get_all_parameters(self):
        self.parameters = "all"

    def lock_target(self):
        if self.target is not None:
            self.target_lock = not self.target_lock

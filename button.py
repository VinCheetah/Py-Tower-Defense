import color
import pygame


class Button:


    def __init__(self, window, config):
        self.window = window
        self.game = window.game
        self.config = self.game.config.buttons.classic | config
        self.label = self.config.label
        self.height = self.config.height
        self.width = self.config.width
        self.value = self.config.value
        
        self.line_color = self.config.LIGHT_GREY
        self.clicked_color = self.config.DARK_GREY_3
        self.under_mouse_color = self.config.DARK_GREY_2
        self.unclicked_color = self.config.unclicked_color
        self.color = self.unclicked_color

        self.screen = self.get_config_screen()
        self.x, self.y = self.get_config_coordonates()

        self.rect = pygame.Rect((self.x, self.y), (self.width, self.height))
        self.clicked = False


    def get_config_screen(self):
        if self.config.screen =

    def display(self):
        police = pygame.font.SysFont("monospace", 30)
        pygame.draw.rect(self.screen, self.color, self.rect)
        pygame.draw.line(self.screen, self.line_color, (self.x, self.y), (self.x + self.width, self.y))
        pygame.draw.line(self.screen, self.line_color, (self.x, self.y), (self.x, self.y + self.height))
        pygame.draw.line(self.screen, self.line_color, (self.x, self.y + self.height),
                         (self.x + self.width, self.y + self.height))
        pygame.draw.line(self.screen, self.line_color, (self.x + self.width, self.y),
                         (self.x + self.width, self.y + self.height))
        text = police.render(self.label, 1, color.WHITE)
        self.screen.blit(text, (self.x + self.width / 2 - text.get_width() / 2,
                                self.y + self.height / 2 - text.get_height() / 2))
        
    def collide(self, x, y):
        return 0 <= x - self.x - self.window.x <= self.width and 0 <= y - self.y - self.window.y <= self.height

    def collide_old(self):
        return self.collide(self.game.mouse_x, self.game.mouse_y)

    def is_clicked(self, x, y):
        if not self.clicked and self.collide(x, y):
            self.clicked = True
            self.color = self.clicked_color
            self.action()

    def under_mouse(self, x, y):
        if self.clicked and self.collide(x, y):
            self.color = self.under_mouse_color
        elif not self.clicked:
            self.color = self.unclicked_color     
            
    def action(self):
        pass


class MultiButton(Button):
    info = {}

    def __init__(self, window, config):
        Button.__init__(self, window, window.game.config.buttons.multi | config)

        self.key = self.config.key
        self.clicked = self.config.clicked

        if self.clicked:
            self.info[self.key] = self.value, self
            self.color = self.clicked_color

    def action(self):
        self.info.get(self.key)[1].unselect()
        self.info[self.key] = (self.value, self)


    def unselect(self):
        self.clicked = False
        self.color = self.unclicked_color


class SoloButton(Button):

    @classmethod
    def new_button(cls, name, window):
        pass
    
    
    def __init__(self, window, config):
        Button.__init__(window, window.game.config.buttons.solo | config)
        

    def action(self):
        self.value = not self.value

    def reset(self):
        self.value = not self.value
        self.clicked = False
        self.color = self.unclicked_color

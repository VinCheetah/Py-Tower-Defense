class Window:

    def __init__(self, game, config):
        self.game = game
        self.config = game.config.window | config

        self.x = 0
        self.y = 0

        self.width = self.config.width
        self.height = self.config.height
        self.background_color = self.config.background_color
        self.name = self.config.name

    def collide(self, x, y):
        return 0 <= x - self.x <= self.width and 0 <= y - self.y <= self.height

    def print_content(self):
        pass

    def move(self):


    def close(self):
        self.game.windows.remove(self)






class DebugWindow(Window):

    def __init__(self, game, selected):
        Window.__init__(self, game, game.config.window.debug)

    def print_debug(self):

    def close(self):
        self.over()
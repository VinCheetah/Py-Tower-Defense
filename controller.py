import view


class Controller:
    def __init__(self, game):
        self.game = game
        self.view = view.View()

    def display(self):
        ...

    def key_handling(self, char, fun):
        ...

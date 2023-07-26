class Wave:
    def __init__(self, game, num, difficulty):
        self.composition = []
        self.zombies = []

        self.init_composition()

    def init_composition(self):
        pass

    def over(self):
        self.game.new_wave()

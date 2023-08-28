class Wave:
    def __init__(self, game):
        self.game = game
        self.num = self.game.num_wave
        self.wave_config = self.game.config.wave
        self.config = self.find_config()

        self.game.set_map_parameters(self.config)

        self.composition = self.init_composition()
        self.zombies = []

        self.init_composition()


    def init_composition(self):
        return self

    def find_config(self):
        for key in self.wave_config:
            key_split = list(map(int, key.split('-')))
            if len(key_split) == 1 and key_split[0] == self.num:
                return self.wave_config[key]
            if len(key_split) == 2 and key_split[0] <= self.num <= key_split[1]:
                return self.wave_config[key]

    def over(self):
        self.game.new_wave()

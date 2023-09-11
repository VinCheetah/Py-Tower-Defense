import random
from config import Config


class Wave:
    def __init__(self, game):
        self.game = game
        self.num = self.game.num_wave
        self.wave_config = self.game.config.wave
        self.config = self.find_config()

        self.life_time = self.config.life_time

        self.game.set_map_parameters(self.config)
        self.continuous_spawning_zombies = []
        self.continuous_spawning_weights = []
        self.init_continuous_spawning()
        self.spawn_list = self.init_spawn_list()


    def init_continuous_spawning(self):
        for key in self.config:
            if key.startswith("continuous_spawning_weight_"):
                self.continuous_spawning_zombies.append(key[27:])
                self.continuous_spawning_weights.append(self.config[key])

    def init_spawn_list(self):
        spawn_list = []
        if self.config.continuous_spawn:
            fictive_time = 0
            while fictive_time < self.life_time:
                spawn_list.append((fictive_time, self.continuous_spawning_choice()))
                fictive_time += self.config.continuous_spawning_rest_time
        return spawn_list

    def continuous_spawning_choice(self):
        return random.choices(
            self.continuous_spawning_zombies, self.continuous_spawning_weights
        )[0]

    def find_config(self):
        config = {}
        for key in self.wave_config:
            key_split = key.split("-")
            if key_split[1] == "":
                key_split[1] = "inf"
            if len(key_split) == 2 and float(key_split[0]) <= self.num <= float(key_split[1]):
                    config |= self.wave_config[key]
        for key in self.wave_config:
            if key.isnumeric() and int(key) == self.num:
                config |= self.wave_config[key]
        return Config(config)

    def action(self):
        self.life_time -= self.game.moving_action
        if self.life_time >= 0:
            while len(self.spawn_list) > 0 and self.spawn_list[-1][0] >= self.life_time:
                self.spawn(self.spawn_list.pop()[1])
        else:
            self.over()

    def spawn(self, zombie):
        self.game.spawn_zombie(self.game.recognize_dico[zombie].out_of_view(self.game))

    def over(self):
        if self.game.auto_wave:
            self.game.new_wave()
        else:
            self.game.wave = None

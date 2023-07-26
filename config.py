import towerClass
import zombieClass
import toml
import collections.abc
import random

from collections import UserDict


class Config(UserDict):

    def __getattr__(self, attr):
        if attr in self.data and isinstance(self.data[attr], collections.abc.Mapping):
                return Config(**self.data[attr])
        return self.get_val(attr)

    def __repr__(self):
        return "Config " + super(Config, self).__repr__()

    @classmethod
    def get_default(cls):
        with open("default_config.toml", "r") as config_file:
            config = toml.load(config_file)
        return cls.add_complement(config)

    @classmethod
    def add_complement(cls, config):
        config["types"] = {
           "attack_towers": [
            towerClass.ArcheryTower,
            towerClass.MagicTower,
            towerClass.BombTower,
            ],
            "effect_towers": [
            towerClass.DamageBoostTower,
            towerClass.AtkRateBoostTower,
            towerClass.RangeBoostTower,
            ],
            "zombies": [
            zombieClass.ClassicZombie,
            zombieClass.TankZombie,
            zombieClass.SpeedyZombie,
            zombieClass.RandomZombie,
            #zombieClass.RandomTanky,
            #zombieClass.RandomTanky2,
            ]
        }
        return cls(config)


    def get_val(self, name, integer_only=False):
        if name in self.data:
            return self.data[name]
        elif "mini_"+name in self.data and "maxi_"+name in self.data:
            return (random.randint if integer_only else random.uniform)(self.data["mini_" + name], self.data["maxi_" + name])
        else:
            raise AttributeError(name)

# DEFAULT = Config(
#     {
#         "original_frame_rate": 60,
#         "max_frame_rate": 90,
#         "original_zoom": 1,
#         "min_frame_rate": 15,
#         "original_speed": 1,
#         "attack_towers_types": {
#             towerClass.ArcheryTower,
#             towerClass.MagicTower,
#             towerClass.BombTower,
#         },
#         "effect_towers_types": {
#             towerClass.DamageBoostTower,
#             towerClass.AtkRateBoostTower,
#             towerClass.RangeBoostTower,
#         },
#         "zombies_types": {
#             zombieClass.ClassicZombie,
#             zombieClass.TankZombie,
#             zombieClass.SpeedyZombie,
#             zombieClass.RandomZombie,
#             #zombieClass.RandomTanky,
#             #zombieClass.RandomTanky2,
#         },
#     }
# )

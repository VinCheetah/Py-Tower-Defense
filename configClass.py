import towerClass
import zombieClass
import attackClass
import toml
import color
import collections.abc
import random

from collections import UserDict


class Config(UserDict):
    library = []

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
                towerClass.CanonSpeedBoostTower,
            ],
            "zombies": [
                zombieClass.ClassicZombie,
                zombieClass.TankZombie,
                zombieClass.SpeedyZombie,
                zombieClass.RandomZombie,
                zombieClass.HealerZombie,
                zombieClass.SpawnerZombie,
                # zombieClass.RandomTanky,
                # zombieClass.RandomTanky2,
            ],
        }
        return cls(config)

    def get_val(self, name):
        if "mini_" + name in self.data and "maxi_" + name in self.data:
            return random.uniform(self.data["mini_" + name], self.data["maxi_" + name])
        elif name in self.data:
            if isinstance(self.data[name], str) and self.data[name] in color.__dict__:
                return getattr(color, self.data[name])
            if name == "attack" and self.data[name] in attackClass.__dict__:
                return getattr(attackClass, self.data[name])
            return self.data[name]

        elif name == "special_parameters":
            return []
        else:
            raise AttributeError(name)


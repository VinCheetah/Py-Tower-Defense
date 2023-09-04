import animationClass
import color
import towerClass
import zombieClass
import wave
import random
import pygame
from config import Config
from boundedValue import BoundedValue


class Game:
    config = Config.get_default()
    recognize_dico = {
        "zombie": zombieClass.Zombie,
        "tower": towerClass.Tower,
        "attack_tower": towerClass.AttackTower,
        "effect_tower": towerClass.EffectTower
    }

    def __init__(self, screen):
        self.test = False

        self.pause = False
        self.moving_action = None
        self.buildable = True
        self.moving_map = False
        self.tracking = False

        self.original_zoom = self.config.general.original_zoom
        self.zoom = BoundedValue(self.original_zoom, self.config.general.min_zoom, self.config.general.max_zoom)
        self.zoom_speed = self.config.general.zoom_speed
        self.time_speed = self.config.general.original_time_speed
        self.original_frame_rate = self.config.general.original_frame_rate
        self.frame_rate = self.original_frame_rate
        self.background_col = color.DARK_GREY

        self.width = None
        self.height = None
        self.actu_dimensions()

        self.alpha_screen = self.create_alpha_screen()
        self.money_rect = pygame.Rect(self.width - 40, self.height - 20, 40, 20)
        self.screen = screen

        self.view_center_x = BoundedValue(0)
        self.view_center_y = BoundedValue(0)
        self.time = 0
        self.money = 1000
        self.lives = 100
        self.wave = None
        self.num_wave = 0

        self.zombies = set()
        self.attack_towers = set()
        self.effect_towers = set()
        self.attacks = set()
        self.animations = set()
        self.zombies_bin = set()
        self.zombies_soon_dead = set()
        self.attack_towers_bin = set()
        self.effect_towers_bin = set()
        self.attacks_bin = set()
        self.animations_bin = set()

        self.new_animations = set()

        self.set_map_parameters(self.config.general)

        self.selected = None

        self.actu_moving_action()
        self.home = towerClass.HomeTower(self)
        self.attack_towers.add(self.home)

    def actu_dimensions(self):
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h

    def actu_moving_action(self):
        self.moving_action = (
                                     self.time_speed * self.original_frame_rate / self.frame_rate
                             ) * (1 - self.pause)

    def pausing(self):
        self.pause = not self.pause
        self.actu_moving_action()

    def change_time_speed(self, multiplicative):
        self.time_speed *= multiplicative
        self.actu_moving_action()

    def create_alpha_screen(self):
        return pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def change_frame_rate(self, additional):
        self.frame_rate += additional
        self.frame_rate = max(self.config.general.min_frame_rate, self.frame_rate)
        self.frame_rate = min(self.config.general.max_frame_rate, self.frame_rate)
        self.actu_moving_action()

    def new_attack_tower(self, x, y):
        chosen_tower = random.choice(self.config.types.attack_towers)(self, x, y)
        if self.transaction(chosen_tower.price):
            self.attack_towers.add(chosen_tower)
            self.check_zombies_target([chosen_tower])
        else:
            del chosen_tower

    def new_effect_tower(self, x, y):
        chosen_tower = random.choice(self.config.types.effect_towers)(self, x, y)
        if self.transaction(chosen_tower.price):
            self.effect_towers.add(chosen_tower)
            chosen_tower.init_effecting()
            self.check_zombies_target([chosen_tower])
        else:
            del chosen_tower

    def check_zombies_target(self, new_tower=None):
        for zombie in self.zombies:
            zombie.find_target(new_tower)

    def zoom_move(self, closer):
        self.zoom *= (self.zoom_speed if closer else 1 / self.zoom_speed)
        self.view_center_x.set_extremum(-self.max_x + self.width / 2 / self.zoom,
                                        self.max_x - self.width / 2 / self.zoom)
        self.view_center_y.set_extremum(-self.max_y + self.height / 2 / self.zoom,
                                        self.max_y - self.height / 2 / self.zoom)

    def set_map_parameters(self, config):
        if "max_x" in config:
            self.max_x = config["max_x"]
        if "max_y" in config:
            self.max_y = config["max_y"]

        if "min_zoom" in config:
            self.zoom.min = max(config["min_zoom"], self.width / (2 * self.max_x), self.height / (2 * self.max_y))
        if "max_zoom" in config:
            self.zoom.max = config["max_zoom"]
        if "max_x" in config:
            self.view_center_x.set_extremum(-self.max_x + self.width / 2 / self.zoom,
                                            self.max_x - self.width / 2 / self.zoom)
        if "max_y" in config:
            self.view_center_y.set_extremum(-self.max_y + self.height / 2 / self.zoom,
                                            self.max_y - self.height / 2 / self.zoom)

        # for attr in ["max_x", "max_y", "max_zoom", "min_zoom"]:
        #     if attr in config:
        #         self.
        #         if attr == "min_zoom":
        #             self.view_center_x.max =
        #             print(self.zoom)
        #             self.zoom.min = max(config[attr], self.width / (2 * self.max_x), self.height / (2 * self.max_y))
        #         else:
        #             self
        #             setattr(self, attr, config[attr])

    def new_zombie(self):
        self.zombies.add(
            (
                random.choice(self.config.types.zombies)(
                    self,
                    self.unview_x(random.randint(0, self.width)),
                    self.unview_y(random.randint(0, self.height)),
                )
            )
        )

    def print_money(self):
        txt_surface = (pygame.font.Font(None, 50)).render(
            str(self.money), True, color.WHITE
        )
        self.screen.blit(txt_surface, (self.width - txt_surface.get_width(), 10))

    def display(self):
        self.track()
        self.screen.fill(self.background_col)
        self.alpha_screen.fill(0)
        if self.selected is not None:
            self.selected.selected()
            for zombie in self.zombies_soon_dead:
                if self.selected in zombie.attackers:
                    zombie.under_selected()

        for att in self.attacks:
            att.print_game()
        for tow in self.attack_towers.union(self.effect_towers):
            tow.print_game()
        for zom in self.zombies:
            zom.print_game()
        for ani in self.animations:
            ani.anime()
        self.screen.blit(self.alpha_screen, (0, 0))
        self.print_money()

    def actu_action(self):
        if not self.pause:
            self.time += self.time_speed / self.frame_rate * self.original_frame_rate
        for tower in self.attack_towers:
            tower.tow_attack()
        for zombie in self.zombies:
            zombie.move()
        for attack in self.attacks:
            attack.move()

    def track(self):
        if self.tracking and self.selected is not None:
            self.set_view_coord(self.selected.x, self.selected.y)

    def add_view_coord(self, x, y):
        self.view_center_x += x
        self.view_center_y += y

    def set_view_coord(self, x, y):
        self.view_center_x.set_value(x)
        self.view_center_y.set_value(y)

    def view_move(self, x_end, y_end, zoom_end=None, speed=1, tracking=False):
        self.animations.add(
            animationClass.ViewMove(
                self,
                x_end,
                y_end,
                zoom_end if zoom_end is not None else self.zoom,
                speed,
                tracking=tracking,
            )
        )

    def new_wave(self):
        self.num_wave += 1
        self.wave = wave.Wave(self)

    def clean(self):
        if len(self.attacks_bin) > 0:
            for attack in self.attacks_bin:
                self.attacks.discard(attack)
                del attack
            self.attacks_bin.clear()
        if len(self.zombies_bin) > 0:
            for zombie in self.zombies_bin:
                self.zombies.discard(zombie)
                del zombie
            self.zombies_bin.clear()
        if len(self.attack_towers_bin) > 0:
            for tower in self.attack_towers_bin:
                self.attack_towers.discard(tower)
                del tower
            self.attack_towers_bin.clear()
        if len(self.effect_towers_bin) > 0:
            for tower in self.effect_towers_bin:
                self.effect_towers.discard(tower)
                del tower
        if len(self.animations_bin) > 0:
            for animation in self.animations_bin:
                self.animations.discard(animation)
                del animation
            self.animations_bin.clear()
        if len(self.new_animations) > 0:
            for animation in self.new_animations:
                self.animations.add(animation)
            self.new_animations.clear()
        for tower in self.attack_towers:
            tower.clean()

    def complete_destruction(self):
        self.selected = None
        self.zombies_bin = self.zombies.copy()
        self.attack_towers_bin = self.attack_towers.copy()
        self.effect_towers_bin = self.effect_towers.copy()
        self.attacks_bin = self.attacks.copy()
        self.animations_bin = self.animations.copy()

    def money_prize(self, value):
        self.money += value

    def unselect(self):
        self.selected = None

    def transaction(self, value):
        if self.money >= value:
            self.money -= value
            return True
        return False

    def view_x(self, x):
        return int((x - self.view_center_x) * self.zoom + self.width / 2)

    def view_y(self, y):
        return int((y - self.view_center_y) * self.zoom + self.height / 2)

    def unview_x(self, x):
        return (x - self.width / 2) / self.zoom + self.view_center_x

    def unview_y(self, y):
        return (y - self.height / 2) / self.zoom + self.view_center_y

    def game_stats(self):
        return (
            f"Frame rate : {self.frame_rate}\n"
            f"Zoom : {self.zoom}\n"
            f"Ticks : {self.time}\n"
            f"Center : {self.view_center_x, self.view_center_y}\n"
            f"Towers : {len(self.attack_towers) + len(self.effect_towers)}\n"
            f"Zombies : {len(self.zombies)}\n"
            f"Money : {self.money}\n"
            f"Wave : {self.wave}\n"
        ) + "\nCOMPLETE DESCRIPTION\n" + "\n".join(
            (str(key) + " : " + str(getattr(self, key))) for key in self.__dict__)

    def recognize(self, object, potential_class):
        print(type(self.recognize_dico.get(potential_class)))
        return isinstance(object, self.recognize_dico.get(potential_class))

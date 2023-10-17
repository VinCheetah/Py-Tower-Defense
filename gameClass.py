import os
import random
import time
import pygame

import animationClass
import boundedValue
import towerClass
import zombieClass
import waveClass
import windowClass
import controllerClass
from configClass import Config
from boundedValue import BoundedValue


class Game:

    config = Config.get_default()
    recognize_dico = {
        "zombie": zombieClass.Zombie,
        "tower": towerClass.Tower,
        "attack_tower": towerClass.AttackTower,
        "effect_tower": towerClass.EffectTower,
        "classic": zombieClass.ClassicZombie,
    }

    @staticmethod
    def god_function(function):
        def wrapper(*args):
            self = args[0]
            if self.god_mode_active:
                function(*args)
            else:
                self.print_text("God Mode Required")
        return wrapper

    def __init__(self):
        os.environ["SDL_VIDEO_CENTERED"] = "1"

        pygame.display.set_caption("Tower Defense")
        pygame.display.set_icon(pygame.image.load("icon.png"))

        # self.test = False

        self.running = True
        self.pause = False
        self.buildable = True
        self.tracking = False
        self.god_mode_active = True
        self.moving_map = False
        self.compact_string = False
        self.zoom_change = False

        self.original_zoom = self.config.general.original_zoom
        self.min_zoom = self.config.general.min_zoom
        self.max_zoom = self.config.general.max_zoom
        self.zoom = BoundedValue(self.original_zoom, self.min_zoom, self.max_zoom)
        self.zoom_speed = self.config.general.zoom_speed
        self.time_speed = self.config.general.original_time_speed
        self.auto_wave = self.config.wave.auto_wave
        self.original_frame_rate = self.config.general.original_frame_rate
        self.frame_rate = self.original_frame_rate

        self.width = 0
        self.height = 0
        self.actu_dimensions()

        self.money_rect = pygame.Rect(self.width - 40, self.height - 20, 40, 20)
        self.screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)

        self.view_center_x = BoundedValue(0)
        self.view_center_y = BoundedValue(0)
        self.moving_action = 0
        self.time = 0
        self.money = 1000
        self.lives = 100
        self.zombie_spawn_number = 1
        self.num_wave = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.ex_mouse_x = 0
        self.ex_mouse_y = 0
        self.wave = None
        self.selected = None
        self.screen_ratio = self.width / self.height

        self.zombies = set()
        self.new_zombies = set()
        self.zombies_bin = set()
        self.zombies_soon_dead = set()

        self.attack_towers = set()
        self.effect_towers = set()
        self.attack_towers_bin = set()
        self.effect_towers_bin = set()

        self.attacks = set()
        self.attacks_bin = set()

        self.animations = set()
        self.new_animations = set()
        self.animations_bin = set()

        self.walls = set()

        self.show = set()

        self.windows = list()

        self.set_map_parameters(self.config.general)

        self.actu_moving_action()
        self.home = towerClass.HomeTower(self)
        self.attack_towers.add(self.home)

        self.controllers = list()
        self.build_wall_controller = controllerClass.WallBuildController(self)
        self.zombie_controller = controllerClass.ZombieController(self)
        self.tower_controller = controllerClass.TowerController(self)
        self.selection_controller = controllerClass.SelectionController(self)
        self.debug_window_controller = controllerClass.DebugWindowController(self)
        self.window_controller = controllerClass.WindowController(self)
        self.map_controller = controllerClass.MapController(self)
        self.main_controller = controllerClass.MainController(self)

        self.window_controller.activize()
        self.map_window = windowClass.MapWindow(self)
        self.new_window(self.map_window)
        self.main_window = windowClass.MainWindow(self)
        self.new_window(self.main_window)
        self.shop_window = windowClass.ShopWindow(self)

        self.build_window = windowClass.BuildWindow(self)

        for controller in self.controllers:
            controller.link_window()

    # BASICS

    def start(self):
        last_frame = 0

        while self.running:
            self.clean()
            self.actu_action()
            self.display()
            one_loop_done = False

            while not one_loop_done or time.time() - last_frame < 1 / self.frame_rate:
                one_loop_done = True
                self.interactions()

            pygame.display.flip()
            last_frame = time.time()

    def interactions(self):
        self.update_mouse_pos()
        for event in pygame.event.get():
            translated_event = self.main_controller.translate(event)
            arg = []
            if translated_event is None:
                continue
            if type(translated_event) is tuple:
                translated_event, arg = translated_event
            for controller in self.controllers:
                if controller.apply(translated_event, *arg):
                    if controller.controller_debug:
                        print(f"I have applied {translated_event} with {controller.name}")
                    break
                elif controller.controller_debug:
                    print(f"Couldn't apply {translated_event} with {controller.name}")
            else:
                if translated_event is not None and self.main_controller.controller_debug:
                    print(f"Couldn't match event {translated_event}")

    def clean(self):
        for set_name in ["attacks", "zombies", "attack_towers", "effect_towers", "animations"]:
            bin_set = self.__getattribute__(set_name + "_bin")
            if len(bin_set) > 0:
                for item in bin_set:
                    self.__getattribute__(set_name).discard(item)
                    del item
                bin_set.clear()
        for set_name in ["animations", "zombies"]:
            new_set = self.__getattribute__("new_" + set_name)
            if len(new_set) > 0:
                for item in new_set:
                    self.__getattribute__(set_name).add(item)
                new_set.clear()
        for tower in self.attack_towers:
            tower.clean()

    def display(self):
        for window in self.windows:
            window.print_window()

    def actu_action(self):
        self.time += self.moving_action
        if self.wave is not None:
            self.wave.action()
        for tower in self.attack_towers:
            tower.tow_attack()
        for zombie in self.zombies:
            zombie.move()
        for attack in self.attacks:
            attack.move()

    def complete_destruction(self):
        self.unselect()
        self.zombies_bin = self.zombies.copy()
        self.attack_towers_bin = self.attack_towers.copy()
        self.effect_towers_bin = self.effect_towers.copy()
        self.attacks_bin = self.attacks.copy()
        self.animations_bin = self.animations.copy()

    # TOWERS

    def towers_set(self):
        return self.attack_towers.difference(self.attack_towers_bin).union(self.effect_towers.difference(self.effect_towers_bin))

    @god_function
    def new_attack_tower(self, x, y):
        self.new_tower(random.choice(self.config.types.attack_towers)(self, x, y))

    @god_function
    def new_effect_tower(self, x, y):
        self.new_tower(random.choice(self.config.types.effect_towers)(self, x, y))

    def new_tower(self, chosen_tower):
        if self.buildable:
            for tower in self.towers_set():
                if chosen_tower.dist(tower) <= tower.size + chosen_tower.size:
                    self.new_animations.add(animationClass.TowerBop(tower))
                    self.new_animations.add(animationClass.ShowText(self, "Cannot build here"))
                    break
            else:
                if self.transaction(chosen_tower.price):
                    chosen_tower.build()
                else:
                    del chosen_tower
            return True
        return False

    def upgrade_selected(self):
        if self.recognize(self.selected, "tower"):
            self.selected.upgrade()

    def forced_upgrade(self):
        self.selected.new_level()

    # ZOMBIES

    def spawn_zombie(self, zombie):
        self.new_zombies.add(zombie)

    @god_function
    def spawn_random_zombie(self, number=1):
        for _ in range(number):
            self.spawn_zombie(random.choice(self.config.types.zombies)(self,
                                                                       self.unview_x(random.randint(0, self.width)),
                                                                       self.unview_y(random.randint(0, self.height)))
                              )

    def multi_spawn_random_zombie(self):
        self.spawn_random_zombie(self.zombie_spawn_number)

    def check_zombies_target(self, new_tower=None):
        for zombie in self.zombies:
            zombie.find_target(new_tower)

    def new_wave(self):
        self.num_wave += 1
        self.wave = waveClass.Wave(self)
        self.print_text("Wave " + str(self.num_wave) + " is comming ... ")

    # WINDOWS

    def new_window(self, new_window):
        self.windows.append(new_window)

    def new_debug_window(self, target=None):
        self.new_window(windowClass.DebugWindow(self, target))
        self.debug_window_controller.activize()

    def find_window(self, x, y):
        if not self.moving_map:
            for window in reversed(self.windows):
                if window.select(x, y):
                    return True
        return False

    def move_window(self, rel_x, rel_y):
        if pygame.mouse.get_pressed()[0] and not self.moving_map:
            for window in reversed(self.windows):
                if window.move(rel_x, rel_y):
                    return True
        return False

    def window_view_up(self, *args):
        return self.windows[-1].window_view_up()

    def window_view_down(self, *args):
        return self.windows[-1].window_view_down()

    def get_basics_parameters(self):
        self.windows[-1].get_basics_parameters()

    def get_all_parameters(self):
        self.windows[-1].get_all_parameters()

    def lock_target(self):
        self.windows[-1].lock_target()

    def delete_selected_window(self):
        self.windows[-1].close()

    # CONTROLLERS

    def add_controllers(self, new_controller):
        self.controllers.append(new_controller)

    # MAP CONTROLL

    def set_view_coord(self, x, y):
        self.view_center_x.set_value(x)
        self.view_center_y.set_value(y)

    def add_view_coord(self, x, y):
        self.view_center_x += x
        self.view_center_y += y

    def set_map_parameters(self, config):
        if "max_coord" in config:
            self.max_x = config["max_coord"]
            self.max_y = self.max_x / self.screen_ratio
        else:
            if "max_x" in config:
                self.max_x = config["max_x"]
            if "max_y" in config:
                self.max_y = config["max_y"]
        if "min_zoom" in config:
            self.min_zoom = max(config["min_zoom"], self.width / (2 * self.max_x), self.height / (2 * self.max_y))
        if "max_zoom" in config:
            self.max_zoom = config["max_zoom"]

        if not self.god_mode_active:
            self.active_map_parameters()

    def active_map_parameters(self):
        self.zoom.set_extremum(self.min_zoom, self.max_zoom)
        self.view_center_x.set_extremum(
            -self.max_x + self.width / 2 / self.zoom,
            self.max_x - self.width / 2 / self.zoom,
        )
        self.view_center_y.set_extremum(
            -self.max_y + self.height / 2 / self.zoom,
            self.max_y - self.height / 2 / self.zoom,
        )

    def move_map(self, rel_x, rel_y):
        if pygame.mouse.get_pressed()[0]:
            self.add_view_coord(- rel_x / self.zoom, - rel_y / self.zoom)
            self.buildable = False
            self.moving_map = True
            return True
        return False

    def view_move(self, x_end, y_end, zoom_end=None, speed=1, tracking=False):
        self.animations.add(animationClass.ViewMove(self,
                                                    x_end,
                                                    y_end,
                                                    zoom_end if zoom_end is not None else self.zoom,
                                                    speed,
                                                    tracking=tracking))

    def zoom_move(self, *args):
        self.zoom *= self.zoom_speed
        if not self.god_mode_active:
            self.active_map_parameters()
        return True

    def unzoom_move(self, *args):
        self.zoom /= self.zoom_speed
        if not self.god_mode_active:
            self.active_map_parameters()
        return True

    def view_home(self):
        self.view_move(0, 0)

    def track(self):
        if self.tracking and self.selected is not None:
            self.set_view_coord(self.selected.x, self.selected.y)

# GAME CONTROLL

    def actu_dimensions(self):
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h

    def screen_resize(self):
        self.actu_dimensions()
        self.display()
        pygame.display.flip()

    def actu_moving_action(self):
        self.moving_action = (not self.pause) * self.time_speed * self.original_frame_rate / self.frame_rate

    def stop_running(self):
        self.running = False

    def pausing(self, forced=False):
        if self.god_mode_active or forced:
            self.pause = not self.pause
            self.actu_moving_action()
        else:
            self.print_text("God Mode Required")

    @god_function
    def change_time_speed(self, multiplicative):
        self.time_speed *= multiplicative
        self.actu_moving_action()

    def change_frame_rate(self, additional):
        self.frame_rate += additional
        self.frame_rate = max(self.config.general.min_frame_rate, self.frame_rate)
        self.frame_rate = min(self.config.general.max_frame_rate, self.frame_rate)
        self.actu_moving_action()

    def god_mode(self):
        self.god_mode_active = not self.god_mode_active
        if self.god_mode_active:
            self.print_text("God Mode Activated")
            self.zoom.unbound()
            self.view_center_x.unbound()
            self.view_center_y.unbound()
        else:
            self.print_text("God Mode Deactivated")
            self.active_map_parameters()

    def update_mouse_pos(self):
        self.ex_mouse_x = self.mouse_x
        self.ex_mouse_y = self.mouse_y
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

    # MONEY

    def money_prize(self, value):
        self.money += value

    def transaction(self, value):
        if self.money >= value:
            self.money -= value
            return True
        else:
            self.print_text(f"Price is {value} and you have {self.money} ...")
        return False

    # SELECT

    def select(self, selected):
        self.unselect()
        self.selection_controller.activize()
        if self.recognize(selected, "zombie"):
            self.zombie_controller.activize()
        elif self.recognize(selected, "tower"):
            self.tower_controller.activize()
        self.selected = selected

    def unselect(self):
        if self.selected is not None:
            if self.recognize(self.selected, "zombie"):
                self.zombie_controller.unactivize()
            elif self.recognize(self.selected, "tower"):
                self.tower_controller.unactivize()
            self.selection_controller.unactivize()
            self.selected = None

    @god_function
    def delete_selected(self):
        if self.selected is not None:
            if self.recognize(self.selected, "tower"):
                self.selected.destroyed()
            elif self.recognize(self.selected, "zombie"):
                self.selected.killed()

    def find_canon(self, *args):
        for canon in self.selected.canons():
            if canon.collide(*args):
                self.print_text("I got a Canon")
                return True
        return False

    # COMMUNICATION

    def create_alpha_screen(self):
        return pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def print_text(self, text):
        self.animations.add(animationClass.ShowText(self, text))

    def make_str(self, item):
        if type(item) is set or type(item) is list:
            if len(item) == 0:
                return "None"
            if self.compact_string:
                composition = dict()
                for element in item:
                    if element.type not in composition:
                        composition[element.type] = 1
                    else:
                        composition[element.type] += 1
                return "\n\t" + "\n\t".join(
                    (elt_type + (composition[elt_type] > 1) * (" (x" + str(composition[elt_type]) + ")")) for elt_type
                    in composition)
            else:
                return "\n\t" + "\n\t".join(str(element) for element in item)
        if type(item) is boundedValue.BoundedValue:
            if self.compact_string:
                return self.make_str(item.value)
        if type(item) is float:
            if self.compact_string:
                return "%.2f" % item
            else:
                return "%.4f" % item
        return str(item)

    def game_stats(self):
        return ((f"Frame rate : {self.frame_rate}\n"
                 f"Zoom : {self.zoom}\n"
                 f"Ticks : {self.time}\n"
                 f"Center : {self.view_center_x, self.view_center_y}\n"
                 f"Towers : {len(self.attack_towers) + len(self.effect_towers)}\n"
                 f"Zombies : {len(self.zombies)}\n"
                 f"Money : {self.money}\n"
                 f"Wave : {self.wave}\n")
                + "\nCOMPLETE DESCRIPTION\n" + "\n".join(
            (str(key) + " : " + str(getattr(self, key))) for key in self.__dict__))

    def __repr__(self):
        return "G.A.M.E"

    # OTHERS

    @staticmethod
    def dist(p1, p2):
        return pow(pow(p1[0] - p2[0], 2) + pow(p1[1] - p2[1], 2), .5)

    def view_x(self, x):
        return int((x - self.view_center_x) * self.zoom + self.width / 2)

    def view_y(self, y):
        return int((y - self.view_center_y) * self.zoom + self.height / 2)

    def view(self, p):
        return self.view_x(p[0]), self.view_y(p[1])

    def unview_x(self, x):
        return (x - self.width / 2) / self.zoom + self.view_center_x

    def unview_y(self, y):
        return (y - self.height / 2) / self.zoom + self.view_center_y

    def unview(self, p):
        return self.unview_x(p[0]), self.unview_y(p[1])

    def recognize(self, obj, potential_class):
        return isinstance(obj, self.recognize_dico.get(potential_class))


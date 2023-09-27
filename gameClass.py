import animationClass
import color
import towerClass
import zombieClass
import wave
import random
import pygame
import window
import controller
from config import Config
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

    def god_function(function):
        def wrapper(*args):
            self = args[0]
            if self.god_mode_active:
                function(*args)
            else:
                self.print_text("God Mode Required")

        return wrapper

    def __init__(self, screen):
        self.test = False

        self.running = True
        self.pause = False
        self.moving_action = None
        self.buildable = True
        self.tracking = False
        self.god_mode_active = True
        self.moving_map = False


        self.original_zoom = self.config.general.original_zoom
        self.min_zoom = self.config.general.min_zoom
        self.max_zoom = self.config.general.max_zoom
        self.zoom = BoundedValue(self.original_zoom, self.min_zoom, self.max_zoom)
        self.zoom_speed = self.config.general.zoom_speed
        self.time_speed = self.config.general.original_time_speed
        self.auto_wave = self.config.wave.auto_wave
        self.background_color = self.config.general.background_color
        self.original_frame_rate = self.config.general.original_frame_rate
        self.frame_rate = self.original_frame_rate

        self.width = 0
        self.height = 0
        self.actu_dimensions()

        self.alpha_screen = self.create_alpha_screen()
        self.money_rect = pygame.Rect(self.width - 40, self.height - 20, 40, 20)
        self.screen = screen

        self.view_center_x = BoundedValue(0)
        self.view_center_y = BoundedValue(0)
        self.time = 0
        self.money = 1000
        self.lives = 100
        self.zombie_spawn_number = 5
        self.wave = None
        self.num_wave = 0
        self.mouse_x = 0
        self.mouse_y = 0
        self.ex_mouse_x = 0
        self.ex_mouse_y = 0
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

        self.windows = list()

        self.set_map_parameters(self.config.general)

        self.selected = None

        self.actu_moving_action()
        self.home = towerClass.HomeTower(self)
        self.attack_towers.add(self.home)

        self.main_controller = controller.MainController(self)
        self.map_controller = controller.MapController(self)
        self.selection_controller = controller.SelectionController(self)
        self.debug_window_controller = controller.DebugWindowController(self)
        self.zombie_controller = controller.ZombieController(self)
        self.tower_controller = controller.TowerController(self)
        self.controllers = [self.debug_window_controller, self.zombie_controller, self.tower_controller, self.main_controller, self.selection_controller, self.map_controller]

    def actu_dimensions(self):
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h

    def window_resize(self):
        self.actu_dimensions()
        self.display()
        pygame.display.flip()

    def actu_moving_action(self):
        self.moving_action = (
            self.time_speed * self.original_frame_rate / self.frame_rate
        ) * (1 - self.pause)

    def stop_running(self):
        self.running = False

    @god_function
    def pausing(self):
        if self.god_mode_active:
            self.pause = not self.pause
            self.actu_moving_action()
        else:
            self.print_text("God Mode Required")

    @god_function
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

    def view_home(self):
        self.view_move(0, 0)

    def new_attack_tower(self, x, y):
        if self.buildable:
            chosen_tower = random.choice(self.config.types.attack_towers)(self, x, y)
            if self.transaction(chosen_tower.price):
                self.attack_towers.add(chosen_tower)
                self.check_zombies_target([chosen_tower])
            else:
                del chosen_tower
            return True
        return False

    @god_function
    def new_effect_tower(self, x, y):
        if self.buildable:
            chosen_tower = random.choice(self.config.types.effect_towers)(self, x, y)
            if self.transaction(chosen_tower.price):
                self.effect_towers.add(chosen_tower)
                chosen_tower.init_effecting()
                self.check_zombies_target([chosen_tower])
            else:
                del chosen_tower
            return True
        return False

    def check_zombies_target(self, new_tower=None):
        for zombie in self.zombies:
            zombie.find_target(new_tower)

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
            self.min_zoom = max(
                config["min_zoom"],
                self.width / (2 * self.max_x),
                self.height / (2 * self.max_y),
            )
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

    @god_function
    def spawn_random_zombie(self, number=1):
        for _ in range(number):
            self.spawn_zombie(
                random.choice(self.config.types.zombies)(
                    self,
                    self.unview_x(random.randint(0, self.width)),
                    self.unview_y(random.randint(0, self.height)),
                )
            )

    def multi_spawn_random_zombie(self):
        self.spawn_random_zombie(self.zombie_spawn_number)

    def print_text(self, text):
        self.animations.add(animationClass.ShowText(self, text))

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

    def print_money(self):
        txt_surface = (pygame.font.Font(None, 50)).render(
            str(self.money), True, color.WHITE
        )
        self.screen.blit(txt_surface, (self.width - txt_surface.get_width(), 10))

    def display(self):
        self.track()
        self.screen.fill(self.background_color)
        self.alpha_screen.fill(0)

        if self.selected is not None:
            self.selected.selected_background()

        for attack in self.attacks:
            attack.print_game()
        for tower in self.attack_towers.union(self.effect_towers):
            tower.print_game()
        for zombie in self.zombies:
            zombie.print_game()

        if self.selected is not None:
            self.selected.selected()
            for zombie in self.zombies_soon_dead:
                if self.selected in zombie.attackers_list():
                    zombie.under_selected()

        for animation in self.animations:
            animation.anime()
        for window in self.windows:
            window.print_window()
        self.screen.blit(self.alpha_screen, (0, 0))
        self.print_money()

    def actu_action(self):
        if not self.pause:
            self.time += self.time_speed / self.frame_rate * self.original_frame_rate
        if self.wave is not None:
            self.wave.action()
        for tower in self.attack_towers:
            tower.tow_attack()
        for zombie in self.zombies:
            zombie.move()
        for attack in self.attacks:
            attack.move()

    def interactions(self):
        self.update_mouse_pos()
        for event in pygame.event.get():
            translated_event = self.main_controller.translate(event)
            arg = []
            if translated_event is None:
                continue
            if type(translated_event) == tuple:
                translated_event, arg = translated_event
            for controler in self.controllers:
                if controler.apply(translated_event, *arg):
                    if controler.controller_debug:
                        print(f"I have applied {translated_event} with {controler.name}")
                    break
                elif controler.controller_debug:
                    print(f"Couldn't apply {translated_event} with {controler.name}")

            else:
                if translated_event is not None and self.main_controller.controller_debug:
                    print(f"Couldn't match event {translated_event}")


    def track(self):
        if self.tracking and self.selected is not None:
            self.set_view_coord(self.selected.x, self.selected.y)

    def lock_target(self):
        self.windows[-1].lock_target()

    def add_view_coord(self, x, y):
        self.view_center_x += x
        self.view_center_y += y

    def set_view_coord(self, x, y):
        self.view_center_x.set_value(x)
        self.view_center_y.set_value(y)

    def update_mouse_pos(self):
        self.ex_mouse_x = self.mouse_x
        self.ex_mouse_y = self.mouse_y
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

    def find_window(self, x, y):
        if not self.moving_map:
            for window in reversed(self.windows):
                if window.collide(x, y):
                    window.go_front()
                    self.debug_window_controller.activize()
                    return True
        return False

    def move_window(self, rel_x, rel_y):
        if pygame.mouse.get_pressed()[0] and not self.moving_map:
            for window in reversed(self.windows):
                if window.move(rel_x, rel_y):
                    return True
        return False


    def unselect(self):
        if self.selected is not None:
            if self.recognize(self.selected, "zombie"):
                self.zombie_controller.unactivize()
            if self.recognize(self.selected, "tower"):
                self.tower_controller.unactivize()
            self.selection_controller.unactivize()
            self.selected = None



    def mouse_actions(self):
        if pygame.mouse.get_pressed()[0] and (self.mouse_x != self.ex_mouse_x or self.mouse_y != self.ex_mouse_y):
            self.buildable = False
            if self.moving_map:
                self.move_map()
            else:
                for window in reversed(self.windows):
                    if window.move():
                        break
                else:
                    self.move_map()
        else:
            self.moving_map = False


    def move_map(self, rel_x, rel_y):
        if pygame.mouse.get_pressed()[0]:
            self.add_view_coord(- rel_x / self.zoom, - rel_y / self.zoom)
            self.buildable = False
            self.moving_map = True
            return True
        return False


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

    @god_function
    def delete_selected(self):
        if self.selected is not None:
            if self.recognize(self.selected, "tower"):
                self.selected.destroyed()
            elif self.recognize(self.selected, "zombie"):
                self.selected.killed()

    def spawn_zombie(self, zombie):
        self.new_zombies.add(zombie)

    def new_wave(self):
        self.num_wave += 1
        self.wave = wave.Wave(self)
        self.print_text("Wave " + str(self.num_wave) + " ... ")

    def new_window(self):
        self.windows.append(window.DebugWindow(self))

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
        if len(self.new_zombies) > 0:
            for zombie in self.new_zombies:
                self.zombies.add(zombie)
            self.new_zombies.clear()
        for tower in self.attack_towers:
            tower.clean()

    def upgrade_selected(self):
        if self.recognize(self.selected, "tower"):
            self.selected.upgrade()

    def complete_destruction(self):
        self.unselect()
        self.zombies_bin = self.zombies.copy()
        self.attack_towers_bin = self.attack_towers.copy()
        self.effect_towers_bin = self.effect_towers.copy()
        self.attacks_bin = self.attacks.copy()
        self.animations_bin = self.animations.copy()

    def money_prize(self, value):
        self.money += value


    def transaction(self, value):
        if self.money >= value:
            self.money -= value
            return True
        else:
            self.print_text(f"Price is {value} and you have {self.money} ...")
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
            (
                f"Frame rate : {self.frame_rate}\n"
                f"Zoom : {self.zoom}\n"
                f"Ticks : {self.time}\n"
                f"Center : {self.view_center_x, self.view_center_y}\n"
                f"Towers : {len(self.attack_towers) + len(self.effect_towers)}\n"
                f"Zombies : {len(self.zombies)}\n"
                f"Money : {self.money}\n"
                f"Wave : {self.wave}\n"
            )
            + "\nCOMPLETE DESCRIPTION\n"
            + "\n".join(
                (str(key) + " : " + str(getattr(self, key))) for key in self.__dict__
            )
        )

    def recognize(self, obj, potential_class):
        return isinstance(obj, self.recognize_dico.get(potential_class))

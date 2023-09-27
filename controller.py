import pygame


class Controller:

    name = "Default Controller"

    controller_debug = False

    def __init__(self, game):
        self.game = game
        self.active = True

        self.active_commands, self.commands, self.inactive_commands = self.create_commands()

    def apply(self, command, *arg):
        if self.active and command in self.active_commands:
            return self.active_commands.get(command)(*arg) or str(command)[0] != "_"
        elif command in self.commands:
            return self.commands.get(command)(*arg) or str(command)[0] != "_"
        elif not self.active and command in self.inactive_commands:
            return self.inactive_commands.get(command)(*arg) or str(command)[0] != "_"
        else:
            if command in self.inactive_commands and self.controller_debug:
                print(f"WARNING: The command ({command}) is in inactive_commands of {self.name}")
            return False

    def translate(self, event):
        if event.type == pygame.QUIT:
            return "QUIT"
        elif event.type == pygame.VIDEORESIZE:
            return "RESIZE"
        elif event.type == pygame.MOUSEMOTION:
            return "_MOUSE_MOTION", event.rel
        elif event.type == pygame.KEYDOWN:
            return self.key_down_translate(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            return self.mouse_button_up_translate(event)

    def key_down_translate(self, event):
        if 97 <= event.key <= 122:
            return event.unicode
        else:
            return event.key

    def mouse_button_up_translate(self, event):
        return {1: "_l_click", 2: "_m_click", 3: "_r_click", 4: "_d_up_click", 5: "_d_down_click"}.get(event.button), event.pos


    def create_commands(self):
        return {}, {}, {}


    def activize(self):
        self.active = True
    def unactivize(self):
        self.active = False







class MainController(Controller):

    name = "Main Controller"
    controller_debug = True

    def create_commands(self):
        return ({
                    pygame.K_ESCAPE: self.game.stop_running,
                    pygame.K_SPACE: self.game.multi_spawn_random_zombie,
                    pygame.K_DOLLAR: self.money_bonus,

                    "g": self.game.god_mode,
                    "t": self.game.pausing,
                    "w": self.game.new_wave,
                    "c": self.game.complete_destruction,

                    "p": self.increase_time_speed,
                    "m": self.reduce_time_speed,
                },
                {
                    "QUIT": self.game.stop_running,
                    "RESIZE": self.game.window_resize,
                },
                {}
        )

    def money_bonus(self):
        self.game.money_prize(10000)

    def increase_time_speed(self):
        self.game.change_time_speed(1.5)

    def reduce_time_speed(self):
        self.game.change_time_speed(2 / 3)








class MapController(Controller):

    name = "Map Controller"
    controller_debug = True

    def create_commands(self):
        return (
            {
                "_d_up_click": self.game.zoom_move,
                "_d_down_click": self.game.unzoom_move,
                "_l_click": self.attack_tower_build,
                "_r_click": self.effect_tower_build,

                "_MOUSE_MOTION": self.game.move_map,

                "h": self.game.view_home
            },
            {},
            {}
        )

    def attack_tower_build(self, *args):
        if not self.game.moving_map:
            if self.game.selected is None:
                self.game.new_attack_tower(*args)
            else:
                self.game.unselect()
        else:
            self.game.buildable = True
            self.game.moving_map = False
        return True

    def effect_tower_build(self, *args):
        if self.game.selected is None:
            self.game.new_effect_tower(*args)
        else:
            self.game.unselect()
        return True

class WindowController(Controller):

    name = "Window Controller"
    controller_debug = True

    def __init__(self, game):
        super().__init__(game)
        self.unactivize()

    def create_commands(self):

        return (
            {

            },
            {
                "_MOUSE_MOTION": self.game.move_window,
                "_l_click": self.game.find_window,
            },
            {}
        )


class DebugWindowController(WindowController):

    name = "Debug Window Controller"

    def create_commands(self):
        active, general, inactive = super().create_commands()
        return (active | {
            "l": self.game.lock_target
        },
            general | {},
            inactive | {}
        )





class SelectionController(Controller):

    name = "Selection Controller"

    def __init__(self, game):
        super().__init__(game)
        self.unactivize()


    def create_commands(self):
        return (
            {
                pygame.K_BACKSPACE: self.game.delete_selected,

                "d": self.create_debug_window,
                "i": self.print_infos

            },
            {
                "_l_click": self.find_selected
            },
            {}
        )

    def create_debug_window(self):
        self.game.new_window()
        self.game.lock_target()

    def find_selected(self, x, y):
        for tower in self.game.attack_towers.union(self.game.effect_towers):
            if tower.dist_point(self.game.unview_x(x), self.game.unview_y(y)) < tower.size:
                self.game.selected = tower
                self.game.view_move(tower.x, tower.y, self.game.height / (3 * tower.range), 1.5)
                self.activize()
                self.game.tower_controller.activize()
                return True
        else:
            for zombie in self.game.zombies:
                if zombie.dist_point(self.game.unview_x(x), self.game.unview_y(y)) < zombie.size:
                    self.game.selected = zombie
                    self.game.view_move(zombie.x, zombie.y, speed=3, tracking=True)
                    return True
        return False


    def print_infos(self):
        assert self.game.selected is not None
        print(self.game.selected.info())


class ZombieController(Controller):

    name = "Zombie Controller"
    def create_commands(self):
        return (
            {},
            {},
            {}
        )

class TowerController(Controller):

    name = "Tower Controller"
    def create_commands(self):
        return (
            {
                "u": self.game.upgrade_selected,
            },
            {},
            {}
        )


from color import Color


class Button:
    # Liste de l'ensemble des boutons
    all_buttons = []
    # On définit les couleurs des boutons
    line_color = Color.LIGHT_GREY
    clicked_color = Color.DARK_GREY_3
    under_mouse_color = Color.DARK_GREY_2
    unclicked_color = Color.DARK_GREY_1

    def __init__(self, label, height, width, screen, pos_center_x, pos_center_y, value):
        """Initialise un boutton

        Args:
            label string: Nom ou intitlé du boutton
            height int: Hauteur du boutton
            width int: Largeur du boutton
            screen pygame.Surface: Fenêtre dans laquelle il faut l'afficher
            pos_center_x int: Position verticale
            pos_center_y int: Position horizontale
            value : Ce que le boutton permet
        """
        self.all_buttons.append(self)
        self.label = label
        self.height = height
        self.width = width
        self.screen = screen
        self.posx = pos_center_x - self.width / 2
        self.posy = pos_center_y - self.height / 2
        self.rect = pygame.Rect((self.posx, self.posy), (self.width, self.height))
        self.value = value
        self.clicked = False
        self.color = self.unclicked_color

    def display(self):
        """Affiche un boutton sur la fenêtre"""
        police = pygame.font.SysFont("monospace", 30)
        pygame.draw.rect(self.screen, self.color, self.rect)
        pygame.draw.line(
            self.screen,
            self.line_color,
            (self.posx, self.posy),
            (self.posx + self.width, self.posy),
        )
        pygame.draw.line(
            self.screen,
            self.line_color,
            (self.posx, self.posy),
            (self.posx, self.posy + self.height),
        )
        pygame.draw.line(
            self.screen,
            self.line_color,
            (self.posx, self.posy + self.height),
            (self.posx + self.width, self.posy + self.height),
        )
        pygame.draw.line(
            self.screen,
            self.line_color,
            (self.posx + self.width, self.posy),
            (self.posx + self.width, self.posy + self.height),
        )
        img_label = police.render(self.label, 1, Color.WHITE)
        screen.blit(
            img_label,
            (
                self.posx + self.width / 2 - img_label.get_width() / 2,
                self.posy + self.height / 2 - img_label.get_height() / 2,
            ),
        )

    def is_clicked(self, x, y):
        """Vérifie si le boutton a été cliqué et agit en conséquence"""
        if (
            self.posx <= x <= self.posx + self.width
            and self.posy <= y <= self.posy + self.height
            and not self.clicked
        ):
            self.clicked = True
            self.color = self.clicked_color
            self.action()

    def under_mouse(self, x, y):
        """Vérifie si la souris est sur le boutton pour changer sa couleur"""
        if (
            self.posx <= x <= self.posx + self.width
            and self.posy <= y <= self.posy + self.height
            and not self.clicked
        ):
            self.color = self.under_mouse_color
        elif not self.clicked:
            self.color = self.unclicked_color


class Multi_Button(Button):
    info = {}

    def __init__(self, label, height, width, screen, posx, posy, value, key, clicked):
        Button.__init__(self, label, height, width, screen, posx, posy, value)
        self.key = key
        self.clicked = clicked
        # Met à jour la valeur pa défault
        if self.clicked:
            self.info[key] = self.value, self
            self.color = self.clicked_color

    def action(self):
        """Met à jour les valeurs renvoyées par l'ensemble des multi bouttons après qu'un nouveau a été cliqué"""
        self.info.get(self.key)[1].clicked = False
        self.info.get(self.key)[1].color = Button.unclicked_color
        self.info[self.key] = (self.value, self)


class Solo_Button(Button):
    def action(self):
        """Change la valeur du boutton"""
        self.value = not self.value

    def reset(self):
        """Remet les variables du boutton par défault"""
        self.value = not self.value
        self.clicked = False
        self.color = self.unclicked_color

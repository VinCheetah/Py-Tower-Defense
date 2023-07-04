import pygame
import color
import time
class Page:

    def __init__(self, game, background_color, pos, height, width):
        self.game = game
        self.page = pygame.Surface((width, height))
        self.width = width
        self.height = height



class TextEntry (Page):


    def input_text(self):
        active = False
        over = False
        text = ""
        active = False
        input_box = pygame.Rect((self.width-10)/2, (self.height-40)/2, self.width-20, self.height - 30)
        while not over and self.game.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = True
                        clign = time.time()
                        cursor = True
                    else:
                        active = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
            txt_surface = (pygame.font.Font(None, 32)).render(text, True, color.WHITE)
            if active:
                if cursor:
                    pygame.draw.rect(self.surface,color.WHITE, pygame.Rect((self.width-10)/2+txt_surface.get_width()+2,(self.height-40)/2+5)

            self.page.print_game()
            # Render the current text.
            # Resize the box if the text is too long.
            width = max(self.size-30, txt_surface.get_width() + 10)
            self.surface.blit((pygame.font.Font(None, 32)).render(text, True, color.WHITE), (input_box.x + 5, input_box.y + 5))
            # Blit the input_box rect.
            pygame.draw.rect(self.surface, color.DARK_GREY, input_box, 2)

            pg.display.flip()
        return None




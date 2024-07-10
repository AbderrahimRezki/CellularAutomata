import sys
import pygame
from dataclasses import dataclass
from random import randint, sample
from slider import Slider

pygame.init()

@dataclass
class Settings:
    # window_title: str

    # screen_width: int
    # screen_height: int
    # nrows: int
    # ncols: int

    min_per_row: int
    max_per_row: int

    alive_color: tuple = (255, 255, 255)
    bg_color: tuple = (0, 0, 0)

    font_path: str = "fonts/prstart.ttf"
    font_color: tuple = (255, 255, 255)
    font_size: int = 32

    fps: int = 60
    
    # def __post_init__(self):
    #     assert self.max_per_row <= self.ncols, "max_per_row can't be greater than grid width."
    #     assert self.min_per_row <= self.max_per_row, "min_per_row can't be greater than max_per_row."


class Game:
    def __init__(self, settings: Settings, window_title = "", screen_width = 3000, screen_height = 2000, nrows = 100, ncols = 100):
        self.settings = settings
        self.set_settings(settings=settings)

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.main_screen_width = self.screen_width * 2 // 3
        self.main_screen_height = self.screen_height

        self.settings_screen_width = self.screen_width - self.main_screen_width
        self.settings_screen_height = self.screen_height

        self.nrows = nrows
        self.ncols = ncols

        self.cell_width = self.main_screen_width // self.ncols
        self.cell_height = self.main_screen_height // self.nrows

        pygame.display.set_caption(window_title)
        self.display = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen = pygame.Surface((self.main_screen_width, self.main_screen_height))
        self.settings_screen = pygame.Surface((self.settings_screen_width, self.settings_screen_height))
        self.min_per_row_slider = Slider((50, 50), (500, 100), self.min_per_row / self.nrows, 0, self.nrows)

        self.is_paused = True
        self.is_drawing = False
        self.clock = pygame.time.Clock()
        self.state = self.initialize_state()


    def set_settings(self, settings):
        self.min_per_row = settings.min_per_row
        self.max_per_row = settings.max_per_row

        self.alive_color = self.settings.alive_color
        self.bg_color = self.settings.bg_color

        self.font_size = settings.font_size
        self.font = pygame.freetype.Font(settings.font_path, settings.font_size)
        self.font_color = settings.font_color

        self.fps = settings.fps

    def initialize_state(self):
        width = self.ncols
        height = self.nrows
        min_per_row = max(self.min_per_row, 0)
        max_per_row = min(self.max_per_row, self.ncols)

        state = [[0 for _ in range(width)] for _ in range(height)]
        
        for i, row in enumerate(state):
            n_choices = randint(min_per_row, max_per_row)
            active = sample(range(width), n_choices)

            for i_active in active:
                row[i_active] = 1

        return state

    def reset(self):
        self.state = self.initialize_state()
        self.is_paused = True

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.is_drawing = True
                # self.is_paused = True

            if event.type == pygame.MOUSEBUTTONUP:
                self.is_drawing = False

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    self.is_paused = not self.is_paused

            if self.is_drawing:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                x, y = mouse_x // self.cell_width, mouse_y // self.cell_height
                try: self.state[x][y] = 1
                except: pass


    def count_neighbours(self, x, y):
        xmin = max(x - 1, 0)
        xmax = min(x + 1, self.ncols - 1)

        ymin = max(y - 1, 0)
        ymax = min(y + 1, self.nrows - 1)

        neighbours_count = 0

        for i in range(xmin, xmax + 1):
            for j in range(ymin, ymax + 1):
                neighbours_count += self.state[j][i]

        return neighbours_count
    
    def handle_cell(self, i, j):
        neighbours_count = self.count_neighbours(i, j)

        if neighbours_count <= 2:
            self.state[j][i] = 0
        elif neighbours_count == 3 and not self.state[j][i]:
            self.state[j][i] = 1
        elif neighbours_count > 3:
            self.state[j][i] = 0

    def update(self):
        for i in range(self.nrows):
            for j in range(self.ncols):
                self.handle_cell(j, i)

    def draw_cell(self, i, j):
        x, y = i * self.cell_height, j * self.cell_width
        color = self.alive_color if self.state[i][j] else self.bg_color
        cell = pygame.rect.Rect(x, y, self.cell_width, self.cell_height)
        pygame.draw.rect(self.screen, color=color, rect=cell)

    def draw_paused_screen(self):
        screen_width, screen_height = self.screen.get_width(), self.screen.get_height()

        surf = pygame.Surface((screen_width,screen_height))
        surf.fill((0, 0,0))
        surf.set_alpha(200)
        self.screen.blit(surf, (0, 0))
        
        message = "Press [SPACE] to resume"
        offsetx = len(message) * self.font_size
        offsety = 50
        fontx, fonty = (screen_width  - offsetx) // 2, screen_height // 2 - offsety

        self.font.render_to(self.screen, (fontx, fonty), message, self.font_color)

    def draw(self):
        self.screen.fill(self.settings.bg_color)

        for i, row in enumerate(self.state):
            for j, col in enumerate(row):
                self.draw_cell(i, j)

        if self.is_paused:
            self.draw_paused_screen()


        mousex, mousey = pygame.mouse.get_pos()[0] - self.main_screen_width, pygame.mouse.get_pos()[1]
        self.settings_screen.fill("black")

        if self.min_per_row_slider.container.collidepoint((mousex, mousey)):
            new_min_per_row = self.min_per_row_slider.move_slider((mousex, mousey))

            if new_min_per_row != self.min_per_row and new_min_per_row <= self.max_per_row: 
                self.settings.min_per_row = new_min_per_row
                self.set_settings(self.settings)
                self.reset()

        self.min_per_row_slider.render(self.settings_screen)

        self.display.blit(self.screen, (0, 0))
        self.display.blit(self.settings_screen, (self.screen_width * 2 // 3, 0))

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(self.fps)
            self.event_handler()
            self.draw()

            if not self.is_paused: self.update()


if __name__ == "__main__":
    settings = Settings(
        min_per_row=10, max_per_row=40,
        fps=5,
        alive_color=(80, 64, 110),
        bg_color=(216, 209, 232)
    )

    Game(settings=settings).run()
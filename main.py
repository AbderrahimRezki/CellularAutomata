import sys
import pygame
from dataclasses import dataclass
from random import randint, sample

pygame.init()

@dataclass
class Settings:
    window_title: str

    screen_width: int
    screen_height: int

    nrows: int
    ncols: int

    min_per_row: int
    max_per_row: int

    alive_color: tuple = (255, 255, 255)
    bg_color: tuple = (0, 0, 0)

    font_path: str = "fonts/prstart.ttf"
    font_color: tuple = (255, 255, 255)
    font_size: int = 32

    fps: int = 60
    
    def __post_init__(self):
        assert self.max_per_row <= self.ncols, "max_per_row can't be greater than grid width."
        assert self.min_per_row <= self.max_per_row, "min_per_row can't be greater than max_per_row."


class Game:
    def __init__(self, settings: Settings):
        self.settings = settings

        self.screen_width = settings.screen_width
        self.screen_height = settings.screen_height

        self.nrows = settings.nrows
        self.ncols = settings.ncols

        self.min_per_row = settings.min_per_row
        self.max_per_row = settings.max_per_row

        self.cell_width = self.screen_width // self.ncols
        self.cell_height = self.screen_height // self.nrows

        self.alive_color = self.settings.alive_color
        self.bg_color = self.settings.bg_color

        self.font_size = settings.font_size
        self.font = pygame.freetype.Font(settings.font_path, settings.font_size)

        self.font_color = settings.font_color

        self.fps = settings.fps
        self.clock = pygame.time.Clock()

        self.is_paused = True

        self.state = self.initialize_state()
        pygame.display.set_caption(settings.window_title)
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

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
                mouse_x, mouse_y = pygame.mouse.get_pos()
                x, y = mouse_x // self.cell_width, mouse_y // self.cell_height
                self.state[x][y] = int(not self.state[x][y])

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    self.is_paused = not self.is_paused


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
        screen_width, screen_height = pygame.display.get_window_size()

        surf = pygame.Surface((screen_width,screen_height))
        surf.fill((0, 0,0))
        surf.set_alpha(200)
        self.screen.blit(surf, (0, 0))
        
        message = "Press [SPACE] to resume"
        offsetx = len(message) * self.font_size
        offsety = 50
        fontx, fonty = (screen_width - offsetx) // 2, screen_height // 2 - offsety

        self.font.render_to(self.screen, (fontx, fonty), message, self.font_color)

    def draw(self):
        self.screen.fill(self.settings.bg_color)

        for i, row in enumerate(self.state):
            for j, col in enumerate(row):
                self.draw_cell(i, j)

        if self.is_paused:
            self.draw_paused_screen()

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(self.fps)
            self.event_handler()
            self.draw()

            if not self.is_paused: self.update()


if __name__ == "__main__":
    settings = Settings(
        window_title="The Game of Life",
        screen_width=1000, screen_height=1000, 
        nrows=100, ncols=100, 
        min_per_row=20, max_per_row=70,
        fps=10,
        alive_color=(80, 64, 110),
        bg_color=(216, 209, 232)
    )

    Game(settings=settings).run()
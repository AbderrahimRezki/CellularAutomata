import pygame

class Slider:
    def __init__(self, pos: tuple, size: tuple, initial_value: float, min_value: int, max_value: int):
        self.pos = pos
        self.size = size

        self.left = self.pos[0]
        self.right = self.pos[0] + self.size[0]
        self.top = self.pos[1]

        self.min_value = min_value 
        self.max_value = max_value

        self.initial_value = (initial_value * self.size[0])

        self.container = pygame.Rect(self.left, self.top, self.size[0], self.size[1])
        self.button = pygame.Rect(self.left + self.initial_value - 50, self.top, 100, self.size[1])

    def move_slider(self, pos):
        self.button.centerx = pos[0]

        offset = pos[0] - self.pos[0]
        self.initial_value = offset

        return int((self.initial_value / self.size[0]) * (self.max_value - self.min_value) + self.min_value)

    def render(self, screen):
        pygame.draw.rect(screen, "gray", self.container)
        pygame.draw.rect(screen, "red", self.button)
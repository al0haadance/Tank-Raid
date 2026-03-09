import pygame
from utils.observer import Observer


class ScoreLabel(Observer):
    def __init__(self):
        self.font = pygame.font.SysFont(None, 36)
        self.image = self.font.render("Score: 0", True, (255, 255, 255))

    def update(self, value):
        self.image = self.font.render(f"Score: {value}", True, (255, 255, 255))

import pygame

class BaseEntity(pygame.sprite.Sprite):
    def __init__(self, image_or_color, x, y, size=(50, 50)):
        super().__init__()
        if isinstance(image_or_color, (tuple, list)):
            self.image = pygame.Surface(size)
            self.image.fill(image_or_color)
        else:
            self.image = pygame.image.load(image_or_color)
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        pass

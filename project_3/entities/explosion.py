import pygame

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = []
        for size in range(10, 40, 10):
            surf = pygame.Surface((size, size))
            surf.fill((255, 255, 0))
            self.frames.append(surf)

        self.index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer % 5 == 0:
            self.index += 1
            if self.index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.index]


from entities.base_entity import BaseEntity
from settings import ENEMY_SPEED

class Enemy(BaseEntity):
    def __init__(self, x, y):
        super().__init__((255, 0, 0), x, y)
        self.direction = 1

    def update(self):
        self.rect.x += ENEMY_SPEED * self.direction
        if self.rect.left <= 0 or self.rect.right >= 800:
            self.direction *= -1
            self.rect.y += 20


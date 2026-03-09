from entities.enemy import Enemy

class FastEnemy(Enemy):
    def update(self):
        self.rect.x += 4 * self.direction
        if self.rect.left <= 0 or self.rect.right >= 800:
            self.direction *= -1
            self.rect.y += 30

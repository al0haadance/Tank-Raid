import random
from entities.enemy import Enemy
from entities.enemy_fast import FastEnemy

class EnemyFactory:
    @staticmethod
    def create_enemy(level=1):
        x = random.randint(0, 700)
        y = random.randint(50, 150)

        if level == 1:
            return Enemy(x, y)
        return FastEnemy(x, y)



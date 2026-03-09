import random
import pygame

from settings import (
    WIDTH,
    HEIGHT,
    PLAYER_SPEED,
    PLAYER_LIVES,
    PLAYER_SHOT_COOLDOWN,
    PLAYER_RESPAWN_INVULNERABILITY,
    ENEMY_BASE_SPEED,
    ENEMY_SHOT_COOLDOWN,
    SHELL_SPEED,
)


CARDINAL_DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
TILE_SIZE = 40
PLAYER_SPAWN = (WIDTH // 2, HEIGHT - 50)

LEVELS = [
    {
        "enemy_spawns": [(80, 80), (400, 80), (720, 80)],
        "enemy_speed_bonus": 0.0,
        "layout": [
            "....................",
            "...####......####...",
            "...#..#......#..#...",
            "...#..#..SS..#..#...",
            "....####.SS.####....",
            "..######....######..",
            "....................",
            "...###........###...",
            "...###........###...",
            "....................",
            "..####........####..",
            "....................",
            "...##..........##...",
            "....................",
            "....................",
        ],
    },
    {
        "enemy_spawns": [(80, 80), (240, 80), (560, 80), (720, 80)],
        "enemy_speed_bonus": 0.35,
        "layout": [
            "....................",
            "..SSSS......SSSS....",
            "..S..S..####..S..S..",
            "..S..S........S..S..",
            "..SSSS..####..SSSS..",
            "........####........",
            "...####......####...",
            "...#..#..SS..#..#...",
            "...####......####...",
            "....................",
            "..####.######.####..",
            "....................",
            "...SS..........SS...",
            "....................",
            "....................",
        ],
    },
    {
        "enemy_spawns": [(80, 80), (240, 80), (400, 80), (560, 80), (720, 80)],
        "enemy_speed_bonus": 0.7,
        "layout": [
            "....................",
            "..########..########",
            "..#......#..#......#",
            "..#.SSSS.#..#.SSSS.#",
            "..#......#..#......#",
            "..########..########",
            "....................",
            "....SS..######..SS..",
            "....SS..#....#..SS..",
            "....SS..######..SS..",
            "....................",
            "..####....##....####",
            "....................",
            "...######......###..",
            "....................",
        ],
    },
]


def _darker(color, amount=40):
    return (
        max(0, color[0] - amount),
        max(0, color[1] - amount),
        max(0, color[2] - amount),
    )


def _direction_to_angle(direction):
    if direction == (0, -1):
        return 0
    if direction == (1, 0):
        return -90
    if direction == (0, 1):
        return 180
    return 90


class Shell(pygame.sprite.Sprite):
    def __init__(self, center, direction, owner, color):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (5, 5), 4)
        pygame.draw.circle(self.image, (240, 240, 240), (5, 5), 2)
        self.rect = self.image.get_rect(center=center)
        self.position = pygame.Vector2(center)
        self.velocity = pygame.Vector2(direction).normalize() * SHELL_SPEED
        self.owner = owner

    def update(self):
        self.position += self.velocity
        self.rect.center = (int(self.position.x), int(self.position.y))
        if (
            self.rect.right < 0
            or self.rect.left > WIDTH
            or self.rect.bottom < 0
            or self.rect.top > HEIGHT
        ):
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, tile_x, tile_y, kind):
        super().__init__()
        self.kind = kind
        self.max_hp = 2 if kind == "brick" else -1
        self.hp = self.max_hp
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(tile_x * TILE_SIZE, tile_y * TILE_SIZE))
        self._repaint()

    def _repaint(self):
        if self.kind == "steel":
            self.image.fill((90, 100, 120))
            pygame.draw.rect(self.image, (130, 145, 165), (5, 5, 30, 30), 2)
            return

        if self.hp >= 2:
            color = (136, 80, 54)
            accent = (165, 102, 69)
        else:
            color = (110, 64, 43)
            accent = (143, 90, 62)
        self.image.fill(color)
        pygame.draw.rect(self.image, accent, (4, 4, 32, 32), 2)
        pygame.draw.line(self.image, accent, (0, 20), (40, 20), 2)
        pygame.draw.line(self.image, accent, (20, 0), (20, 40), 2)

    def hit(self):
        if self.hp < 0:
            return False
        self.hp -= 1
        if self.hp <= 0:
            self.kill()
            return True
        self._repaint()
        return False


class Tank(pygame.sprite.Sprite):
    def __init__(self, center, color, speed, shot_cooldown):
        super().__init__()
        self.base_color = color
        self.base_image = self._build_image(color)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=center)
        self.position = pygame.Vector2(self.rect.center)
        self.direction = (0, -1)
        self.speed = speed
        self.shot_cooldown_frames = shot_cooldown
        self.cooldown = 0

    def _build_image(self, color):
        body_shadow = _darker(color, 45)
        barrel_color = _darker(color, 70)
        surface = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.rect(surface, body_shadow, (5, 7, 26, 22), border_radius=5)
        pygame.draw.rect(surface, color, (7, 9, 22, 18), border_radius=5)
        pygame.draw.circle(surface, (45, 45, 45), (18, 18), 7)
        pygame.draw.circle(surface, (90, 90, 90), (18, 18), 4)
        pygame.draw.rect(surface, barrel_color, (16, 0, 4, 14), border_radius=2)
        return surface

    def set_direction(self, direction):
        if direction not in CARDINAL_DIRECTIONS:
            return
        if direction == self.direction:
            return
        self.direction = direction
        self.image = pygame.transform.rotate(self.base_image, _direction_to_angle(direction))
        current_center = self.rect.center
        self.rect = self.image.get_rect(center=current_center)

    def tick(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def _can_move_to(self, new_rect, obstacles):
        if (
            new_rect.left < 0
            or new_rect.right > WIDTH
            or new_rect.top < 0
            or new_rect.bottom > HEIGHT
        ):
            return False
        for obstacle in obstacles:
            if new_rect.colliderect(obstacle.rect):
                return False
        return True

    def move(self, direction, obstacles):
        if direction not in CARDINAL_DIRECTIONS:
            return False
        move_vector = pygame.Vector2(direction) * self.speed
        moved = False

        if move_vector.x != 0:
            next_rect_x = self.rect.move(move_vector.x, 0)
            if self._can_move_to(next_rect_x, obstacles):
                self.rect = next_rect_x
                moved = True
        if move_vector.y != 0:
            next_rect_y = self.rect.move(0, move_vector.y)
            if self._can_move_to(next_rect_y, obstacles):
                self.rect = next_rect_y
                moved = True

        self.position.update(self.rect.center)
        return moved

    def shoot(self, shells_group, color):
        if self.cooldown > 0:
            return False
        muzzle = pygame.Vector2(self.rect.center) + pygame.Vector2(self.direction) * 22
        shell = Shell((int(muzzle.x), int(muzzle.y)), self.direction, self, color)
        shells_group.add(shell)
        self.cooldown = self.shot_cooldown_frames
        return True


class EnemyTank(Tank):
    def __init__(self, center, speed, level):
        shot_cooldown = max(26, int(ENEMY_SHOT_COOLDOWN - level * 5))
        super().__init__(center, (210, 74, 74), speed, shot_cooldown)
        self.turn_timer = random.randint(18, 70)
        self.shoot_timer = random.randint(35, 95)
        self.set_direction(random.choice(CARDINAL_DIRECTIONS))

    def _choose_direction(self, player):
        if random.random() < 0.55:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            if abs(dx) > abs(dy):
                return (1, 0) if dx > 0 else (-1, 0)
            return (0, 1) if dy > 0 else (0, -1)
        return random.choice(CARDINAL_DIRECTIONS)

    def update_ai(self, player, obstacles, shells_group):
        self.tick()
        self.turn_timer -= 1
        moved = self.move(self.direction, obstacles)
        if not moved or self.turn_timer <= 0:
            self.set_direction(self._choose_direction(player))
            self.turn_timer = random.randint(22, 75)

        self.shoot_timer -= 1
        aligned = (
            abs(self.rect.centerx - player.rect.centerx) < 18
            or abs(self.rect.centery - player.rect.centery) < 18
        )

        should_shoot = False
        if aligned and random.random() < 0.05:
            should_shoot = True
        elif self.shoot_timer <= 0:
            should_shoot = True

        if should_shoot and self.shoot(shells_group, (255, 150, 120)):
            self.shoot_timer = random.randint(35, 95)


class GameScene:
    def __init__(self, game):
        self.game = game
        self.hud_font = pygame.font.SysFont("consolas", 24, bold=True)
        self.big_font = pygame.font.SysFont("consolas", 56, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 24)

        self.player = Tank(PLAYER_SPAWN, (86, 188, 108), PLAYER_SPEED, PLAYER_SHOT_COOLDOWN)
        self.player_invulnerability = 0
        self.lives = PLAYER_LIVES
        self.score = 0
        self.level_index = 0
        self.state = "playing"
        self.transition_timer = 0

        self.obstacles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.shells = pygame.sprite.Group()
        self.sparkles = []
        self.background_particles = []
        for _ in range(70):
            self.background_particles.append(
                [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.2, 0.8)]
            )

        self._load_level(self.level_index, keep_player_position=False)

    def _load_level(self, level_index, keep_player_position):
        self.obstacles.empty()
        self.enemies.empty()
        self.shells.empty()
        self.sparkles.clear()

        level_data = LEVELS[level_index]
        for y, row in enumerate(level_data["layout"]):
            for x, cell in enumerate(row):
                if cell == "#":
                    self.obstacles.add(Obstacle(x, y, "brick"))
                elif cell == "S":
                    self.obstacles.add(Obstacle(x, y, "steel"))

        enemy_speed = ENEMY_BASE_SPEED + level_data["enemy_speed_bonus"]
        for spawn in level_data["enemy_spawns"]:
            enemy = EnemyTank(spawn, enemy_speed, level_index + 1)
            self.enemies.add(enemy)

        if keep_player_position:
            self.player.rect.center = PLAYER_SPAWN
        else:
            self.player = Tank(PLAYER_SPAWN, (86, 188, 108), PLAYER_SPEED, PLAYER_SHOT_COOLDOWN)
        self.player.position.update(self.player.rect.center)
        self.player.set_direction((0, -1))
        self.player_invulnerability = PLAYER_RESPAWN_INVULNERABILITY
        self.state = "playing"
        self.transition_timer = 0

    def handle_events(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            from scenes.menu_scene import MenuScene

            self.game.scene_manager.change_scene(MenuScene(self.game))
            return

        if event.key == pygame.K_r and self.state == "playing":
            self._load_level(self.level_index, keep_player_position=True)
            return

        if event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.state in ("game_over", "victory"):
            from scenes.menu_scene import MenuScene

            self.game.scene_manager.change_scene(MenuScene(self.game))
            return

        if event.key == pygame.K_SPACE and self.state == "playing":
            self.player.shoot(self.shells, (130, 255, 160))

    def _read_player_move(self):
        keys = pygame.key.get_pressed()
        horizontal = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(
            keys[pygame.K_a] or keys[pygame.K_LEFT]
        )
        vertical = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(
            keys[pygame.K_w] or keys[pygame.K_UP]
        )
        if horizontal != 0:
            return (1, 0) if horizontal > 0 else (-1, 0)
        if vertical != 0:
            return (0, 1) if vertical > 0 else (0, -1)
        return None

    def _update_background(self):
        for particle in self.background_particles:
            particle[1] += particle[2]
            if particle[1] > HEIGHT:
                particle[0] = random.randint(0, WIDTH)
                particle[1] = -4
                particle[2] = random.uniform(0.2, 0.8)

    def _update_sparkles(self):
        updated = []
        for x, y, radius, ttl, color in self.sparkles:
            ttl -= 1
            if ttl <= 0:
                continue
            updated.append([x, y, radius + 0.3, ttl, color])
        self.sparkles = updated

    def _spawn_hit_effect(self, center, color):
        x, y = center
        self.sparkles.append([x, y, 6.0, 16, color])

    def _handle_shell_collisions(self):
        for shell in list(self.shells):
            if not shell.alive():
                continue

            obstacle_hit = None
            for obstacle in self.obstacles:
                if shell.rect.colliderect(obstacle.rect):
                    obstacle_hit = obstacle
                    break
            if obstacle_hit:
                obstacle_hit.hit()
                self._spawn_hit_effect(shell.rect.center, (220, 150, 90))
                shell.kill()
                continue

            if shell.owner is self.player:
                enemy = pygame.sprite.spritecollideany(shell, self.enemies)
                if enemy:
                    self.score += 100
                    self._spawn_hit_effect(enemy.rect.center, (255, 120, 120))
                    enemy.kill()
                    shell.kill()
            else:
                if self.player_invulnerability <= 0 and shell.rect.colliderect(self.player.rect):
                    self.lives -= 1
                    self._spawn_hit_effect(self.player.rect.center, (255, 90, 90))
                    shell.kill()
                    if self.lives <= 0:
                        self.state = "game_over"
                    else:
                        self.player.rect.center = PLAYER_SPAWN
                        self.player.position.update(self.player.rect.center)
                        self.player_invulnerability = PLAYER_RESPAWN_INVULNERABILITY

        if self.player_invulnerability <= 0 and pygame.sprite.spritecollideany(self.player, self.enemies):
            self.lives -= 1
            self._spawn_hit_effect(self.player.rect.center, (255, 90, 90))
            if self.lives <= 0:
                self.state = "game_over"
            else:
                self.player.rect.center = PLAYER_SPAWN
                self.player.position.update(self.player.rect.center)
                self.player_invulnerability = PLAYER_RESPAWN_INVULNERABILITY

    def update(self):
        self._update_background()
        self._update_sparkles()

        if self.state == "playing":
            move_direction = self._read_player_move()
            if move_direction is not None:
                self.player.set_direction(move_direction)
                self.player.move(move_direction, self.obstacles)

            self.player.tick()
            if self.player_invulnerability > 0:
                self.player_invulnerability -= 1

            for enemy in self.enemies:
                enemy.update_ai(self.player, self.obstacles, self.shells)

            self.shells.update()
            self._handle_shell_collisions()

            if len(self.enemies) == 0:
                if self.level_index + 1 < len(LEVELS):
                    self.state = "level_clear"
                    self.transition_timer = 110
                else:
                    self.state = "victory"

        elif self.state == "level_clear":
            self.transition_timer -= 1
            if self.transition_timer <= 0:
                self.level_index += 1
                self._load_level(self.level_index, keep_player_position=True)

    def _draw_background(self, screen):
        top = (20, 38, 26)
        bottom = (13, 20, 15)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            color = (
                int(top[0] * (1 - ratio) + bottom[0] * ratio),
                int(top[1] * (1 - ratio) + bottom[1] * ratio),
                int(top[2] * (1 - ratio) + bottom[2] * ratio),
            )
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

        for x in range(0, WIDTH, TILE_SIZE):
            pygame.draw.line(screen, (33, 48, 36), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, TILE_SIZE):
            pygame.draw.line(screen, (33, 48, 36), (0, y), (WIDTH, y), 1)

        for x, y, size in self.background_particles:
            pygame.draw.circle(screen, (85, 115, 95), (int(x), int(y)), int(size) + 1)

    def _draw_player(self, screen):
        if self.player_invulnerability > 0 and (self.player_invulnerability // 8) % 2 == 0:
            return
        screen.blit(self.player.image, self.player.rect)

    def _draw_hud(self, screen):
        panel = pygame.Rect(8, 8, WIDTH - 16, 42)
        pygame.draw.rect(screen, (18, 24, 20), panel, border_radius=8)
        pygame.draw.rect(screen, (88, 120, 96), panel, 2, border_radius=8)

        hud_text = (
            f"Level: {self.level_index + 1}/{len(LEVELS)}    "
            f"Lives: {self.lives}    "
            f"Score: {self.score}    "
            f"Enemies: {len(self.enemies)}"
        )
        text_surface = self.hud_font.render(hud_text, True, (224, 235, 225))
        screen.blit(text_surface, (20, 16))

    def _draw_overlay(self, screen, title, subtitle):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 8, 10, 120))
        screen.blit(overlay, (0, 0))

        title_surface = self.big_font.render(title, True, (240, 240, 200))
        subtitle_surface = self.small_font.render(subtitle, True, (200, 210, 225))
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, HEIGHT // 2 - 60))
        screen.blit(
            subtitle_surface,
            (WIDTH // 2 - subtitle_surface.get_width() // 2, HEIGHT // 2 + 12),
        )

    def draw(self, screen):
        self._draw_background(screen)
        self.obstacles.draw(screen)
        self.enemies.draw(screen)
        self._draw_player(screen)
        self.shells.draw(screen)

        for x, y, radius, _, color in self.sparkles:
            pygame.draw.circle(screen, color, (int(x), int(y)), int(radius), 2)

        self._draw_hud(screen)

        if self.state == "level_clear":
            self._draw_overlay(screen, "LEVEL CLEAR", "Hold position... next wave incoming")
        elif self.state == "game_over":
            self._draw_overlay(screen, "GAME OVER", "Press Enter/Space to return to menu")
        elif self.state == "victory":
            self._draw_overlay(screen, "VICTORY", "Campaign complete. Press Enter/Space")

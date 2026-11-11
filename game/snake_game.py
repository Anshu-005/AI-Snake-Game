import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()

# Game colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Game configuration
BLOCK_SIZE = 20
SPEED = 15
HEADER_HEIGHT = 60

FONT = pygame.font.SysFont('arial', 25)
HEADER_LABEL_FONT = pygame.font.SysFont('arial', 11, bold=True)
HEADER_VALUE_FONT = pygame.font.SysFont('arial', 16, bold=True)

Point = namedtuple('Point', 'x, y')

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

class SnakeGame:

    def __init__(self, width=640, height=480, speed=SPEED, window_pos=None):
        self.width = width
        self.height = height
        self.header_height = HEADER_HEIGHT
        self.speed = speed
        self.mode_label = "CLASSIC"
        self.difficulty_label = "MEDIUM"
        self.progressive_speed = False

        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('AI Snake Game')
        if window_pos is not None:
            self.set_window_pos(window_pos[0], window_pos[1])
        self.clock = pygame.time.Clock()

        # Load saved high score
        self.high_score = self.load_high_score()

        self.reset()

    def set_window_pos(self, x, y):
        try:
            import ctypes
            wm = pygame.display.get_wm_info()
            hwnd = wm.get('window', 0)
            if not hwnd:
                hwnd = ctypes.windll.user32.FindWindowW(None, 'AI Snake Game')
            if hwnd:
                # SWP_NOZORDER = 0x0004, SWP_SHOWWINDOW = 0x0040
                ctypes.windll.user32.SetWindowPos(
                    hwnd, 0, int(x), int(y), self.width, self.height, 0x0004 | 0x0040
                )
        except Exception:
            pass

    def load_high_score(self):
            try:
                with open("highscore.txt", "r") as file:
                    return int(file.read())
            except (FileNotFoundError, ValueError):
                return 0


    def save_high_score(self):
            with open("highscore.txt", "w") as file:
                file.write(str(self.high_score))

        

    def reset(self):
        self.direction = Direction.RIGHT

        # Center snake within the playable area below header
        play_h = self.height - self.header_height
        start_y = self.header_height + ((play_h // 2) // BLOCK_SIZE) * BLOCK_SIZE

        self.head = Point(
            self.width // 2,
            start_y
        )

        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)
        ]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _get_distance(self, point1, point2):
        return abs(point1.x - point2.x) + abs(point1.y - point2.y)     

    def _place_food(self):
        play_h = self.height - self.header_height
        x = random.randint(0, (self.width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = self.header_height + random.randint(0, (play_h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def _move(self, action=None):
        if action is not None:
            clockwise = [
                Direction.RIGHT,
                Direction.DOWN,
                Direction.LEFT,
                Direction.UP
            ]

            idx = clockwise.index(self.direction)

            if list(action) == [1, 0, 0]:
                new_direction = clockwise[idx]
            elif list(action) == [0, 1, 0]:
                new_direction = clockwise[(idx + 1) % 4]
            elif list(action) == [0, 0, 1]:
                new_direction = clockwise[(idx - 1) % 4]
            else:
                raise ValueError(f"Invalid action: {action}")

            self.direction = new_direction

        else:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_UP] and self.direction != Direction.DOWN:
                self.direction = Direction.UP
            elif keys[pygame.K_DOWN] and self.direction != Direction.UP:
                self.direction = Direction.DOWN
            elif keys[pygame.K_LEFT] and self.direction != Direction.RIGHT:
                self.direction = Direction.LEFT
            elif keys[pygame.K_RIGHT] and self.direction != Direction.LEFT:
                self.direction = Direction.RIGHT

        x = self.head.x
        y = self.head.y

        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE

        self.head = Point(x, y)

    def is_collision(self, point=None):
        if point is None:
            point = self.head

        # Wall collision (respects header area as top barrier)
        if (
            point.x > self.width - BLOCK_SIZE
            or point.x < 0
            or point.y > self.height - BLOCK_SIZE
            or point.y < self.header_height
        ):
            return True

        # Body collision
        if point in self.snake[1:]:
            return True

        return False

    _is_collision = is_collision

    def _update_ui(self):
        self.display.fill(BLACK)

        # Draw subtle grid strictly in the playable area
        for x in range(0, self.width, BLOCK_SIZE):
            pygame.draw.line(
                self.display, (25, 25, 35),
                (x, self.header_height), (x, self.height)
            )

        for y in range(self.header_height, self.height, BLOCK_SIZE):
            pygame.draw.line(
                self.display, (25, 25, 35),
                (0, y), (self.width, y)
            )

        # Draw snake
        for point in self.snake:
            pygame.draw.rect(
                self.display,
                GREEN,
                pygame.Rect(
                    point.x, point.y,
                    BLOCK_SIZE, BLOCK_SIZE
                ),
                border_radius=5
            )

        # Draw food
        pygame.draw.circle(
            self.display,
            RED,
            (
                self.food.x + BLOCK_SIZE // 2,
                self.food.y + BLOCK_SIZE // 2
            ),
            BLOCK_SIZE // 2 - 2
        )

        # ==========================================================
        # SEPARATE HEADER SECTION FOR GAME STATS (NO OVERLAP WITH GAMEPLAY)
        # ==========================================================
        # 1. Header bar background panel
        header_bar = pygame.Rect(0, 0, self.width, self.header_height)
        pygame.draw.rect(self.display, (18, 20, 28), header_bar)

        # 2. Accent divider separating header from play area
        pygame.draw.line(
            self.display,
            (50, 55, 75),
            (0, self.header_height - 1),
            (self.width, self.header_height - 1),
            2
        )

        # 3. Four cards: SCORE, BEST, MODE, DIFFICULTY
        card_w = 140
        card_h = 44
        card_y = 8
        spacing = 16

        def draw_badge(index, label, value, value_color):
            card_x = spacing + index * (card_w + spacing)
            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

            # Card background and border
            pygame.draw.rect(self.display, (28, 31, 44), card_rect, border_radius=8)
            pygame.draw.rect(self.display, (55, 60, 80), card_rect, width=1, border_radius=8)

            # Card label (small uppercase)
            lbl = HEADER_LABEL_FONT.render(label, True, (135, 140, 155))
            lbl_r = lbl.get_rect(center=(card_x + card_w // 2, card_y + 13))
            self.display.blit(lbl, lbl_r)

            # Card value (bold)
            val = HEADER_VALUE_FONT.render(str(value), True, value_color)
            val_r = val.get_rect(center=(card_x + card_w // 2, card_y + 30))
            self.display.blit(val, val_r)

        # Badge 1: SCORE
        draw_badge(0, "SCORE", self.score, WHITE)

        # Badge 2: BEST (HIGH SCORE)
        draw_badge(1, "BEST", self.high_score, GREEN)

        # Badge 3: MODE
        mode_str = getattr(self, "mode_label", "CLASSIC")
        mode_color = (80, 170, 255) if "AI" in mode_str.upper() else (255, 210, 80)
        draw_badge(2, "MODE", mode_str, mode_color)

        # Badge 4: DIFFICULTY
        diff_str = getattr(self, "difficulty_label", "MEDIUM")
        if "EASY" in diff_str.upper():
            diff_color = GREEN
        elif "HARD" in diff_str.upper():
            diff_color = (255, 80, 80)
        else:
            diff_color = (255, 185, 60)
        draw_badge(3, "DIFFICULTY", diff_str, diff_color)

        pygame.display.flip()

    def play_step(self, action=None):
        self.frame_iteration += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if action is None and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN

        # Remember distance to the current food
        old_distance = self._get_distance(self.head, self.food)

        self._move(action)
        self.snake.insert(0, self.head)

        game_over = False
        reward = 0

        # Collision or timeout
        if self.is_collision() or (
            action is not None and self.frame_iteration > 100 * len(self.snake)
        ):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # Food eaten
        if self.head == self.food:
            self.score += 1
            reward = 10

            # Update high score
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

            self._place_food()

        else:
            self.snake.pop()

            # Reward for moving closer to food
            new_distance = self._get_distance(self.head, self.food)

            if new_distance < old_distance:
                reward = 0.1
            elif new_distance > old_distance:
                reward = -0.1

        self._update_ui()

        if self.speed > 0:

            current_speed = self.speed

            if self.progressive_speed:
                speed_increase = (self.score // 5) * 2
                current_speed = min(self.speed + speed_increase, 40)

            self.clock.tick(current_speed)

        return reward, game_over, self.score


if __name__ == "__main__":
    game = SnakeGame()

    while True:
        reward, game_over, score = game.play_step()

        if game_over:
            print("Game Over")
            print("Final Score:", score)
            break

    pygame.quit()

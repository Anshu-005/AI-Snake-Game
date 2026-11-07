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

FONT = pygame.font.SysFont('arial', 25)

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
        self.speed = speed

        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('AI Snake Game')
        if window_pos is not None:
            self.set_window_pos(window_pos[0], window_pos[1])
        self.clock = pygame.time.Clock()
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

    def reset(self):
        self.direction = Direction.RIGHT

        self.head = Point(
            self.width // 2,
            self.height // 2
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

    def _place_food(self):
        x = random.randint(0, (self.width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
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

            # [Straight, Right, Left]
            action_list = list(action) if hasattr(action, '__iter__') else action

            if action_list == [1, 0, 0]:
                new_direction = clockwise[idx]
            elif action_list == [0, 1, 0]:
                new_direction = clockwise[(idx + 1) % 4]
            else:
                new_direction = clockwise[(idx - 1) % 4]

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

        # Wall collision
        if (
            point.x > self.width - BLOCK_SIZE
            or point.x < 0
            or point.y > self.height - BLOCK_SIZE
            or point.y < 0
        ):
            return True

        # Body collision
        if point in self.snake[1:]:
            return True

        return False

    _is_collision = is_collision

    def _update_ui(self):
        self.display.fill(BLACK)

        for point in self.snake:
            pygame.draw.rect(
                self.display,
                GREEN,
                pygame.Rect(
                    point.x,
                    point.y,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )
            )

        pygame.draw.rect(
            self.display,
            RED,
            pygame.Rect(
                self.food.x,
                self.food.y,
                BLOCK_SIZE,
                BLOCK_SIZE
            )
        )

        text = FONT.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
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

        self._move(action)
        self.snake.insert(0, self.head)

        game_over = False
        reward = 0

        # Collision or loop timeout (for AI training)
        if self.is_collision() or (action is not None and self.frame_iteration > 100 * len(self.snake)):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()

        self._update_ui()
        if self.speed > 0:
            self.clock.tick(self.speed)

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

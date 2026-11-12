import os
import sys
import pygame
import random
from enum import Enum
from collections import namedtuple

# Ensure project root is on sys.path for direct script execution
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from game.snake_game import (
        Direction,
        Point,
        BLOCK_SIZE,
        SPEED,
        HEADER_HEIGHT,
        WHITE,
        RED,
        GREEN,
        BLACK,
        HEADER_LABEL_FONT,
        HEADER_VALUE_FONT,
    )
except ModuleNotFoundError:
    from snake_game import (
        Direction,
        Point,
        BLOCK_SIZE,
        SPEED,
        HEADER_HEIGHT,
        WHITE,
        RED,
        GREEN,
        BLACK,
        HEADER_LABEL_FONT,
        HEADER_VALUE_FONT,
    )

# Colors for Two-Snake environment
HUMAN_COLOR_OUTER = (0, 170, 255)       # Cyan / Blue
HUMAN_COLOR_INNER = (120, 220, 255)
AI_COLOR_OUTER = (0, 220, 120)          # Green
AI_COLOR_INNER = (120, 255, 170)
ELIMINATED_COLOR = (60, 65, 80)         # Dim slate gray for eliminated snake


class TwoSnakeGame:
    """
    Competitive Two-Snake environment (Human vs AI).
    Supports independent positions, directions, and scores on a shared grid
    with single shared food and complete elimination/collision mechanics.
    """

    def __init__(self, width=640, height=480, speed=SPEED, window_pos=None):
        self.width = width
        self.height = height
        self.header_height = HEADER_HEIGHT
        self.speed = speed
        self.mode_label = "HUMAN VS AI"
        self.difficulty_label = "MEDIUM"

        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Neural Network Snake - Human vs AI')
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
                hwnd = ctypes.windll.user32.FindWindowW(None, 'Neural Network Snake - Human vs AI')
            if hwnd:
                ctypes.windll.user32.SetWindowPos(
                    hwnd, 0, int(x), int(y), self.width, self.height, 0x0004 | 0x0040
                )
        except Exception:
            pass

    def reset(self):
        """Reset the environment with both snakes positioned far apart."""
        play_h = self.height - self.header_height
        start_y = self.header_height + ((play_h // 2) // BLOCK_SIZE) * BLOCK_SIZE

        # Snake 1 (Human - Left side, facing RIGHT)
        start_x1 = ((self.width // 4) // BLOCK_SIZE) * BLOCK_SIZE
        self.direction1 = Direction.RIGHT
        self.head1 = Point(start_x1, start_y)
        self.snake1 = [
            self.head1,
            Point(self.head1.x - BLOCK_SIZE, self.head1.y),
            Point(self.head1.x - (2 * BLOCK_SIZE), self.head1.y),
        ]
        self.score1 = 0
        self.alive1 = True

        # Snake 2 (AI - Right side, facing LEFT)
        start_x2 = (((3 * self.width) // 4) // BLOCK_SIZE) * BLOCK_SIZE
        self.direction2 = Direction.LEFT
        self.head2 = Point(start_x2, start_y)
        self.snake2 = [
            self.head2,
            Point(self.head2.x + BLOCK_SIZE, self.head2.y),
            Point(self.head2.x + (2 * BLOCK_SIZE), self.head2.y),
        ]
        self.score2 = 0
        self.alive2 = True

        self.frame_iteration = 0
        self.max_frames = 2500  # Safety timeout for match duration

        # Shared food
        self.food = None
        self._place_food()

    def _place_food(self):
        """
        Place food at an available grid position below the header not occupied by either snake.
        If the board is completely full, sets self.food = None.
        """
        occupied = set(self.snake1) | set(self.snake2)
        available_positions = [
            Point(x, y)
            for x in range(0, self.width, BLOCK_SIZE)
            for y in range(self.header_height, self.height, BLOCK_SIZE)
            if Point(x, y) not in occupied
        ]

        if available_positions:
            self.food = random.choice(available_positions)
        else:
            self.food = None

    def is_wall_collision(self, point):
        """Check if a point hits any wall or the top header boundary."""
        return (
            point.x < 0
            or point.x > self.width - BLOCK_SIZE
            or point.y < self.header_height
            or point.y > self.height - BLOCK_SIZE
        )

    def _next_head(self, head, direction):
        """Calculate next coordinate given head point and direction."""
        x, y = head.x, head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        return Point(x, y)

    def _resolve_direction(self, current_dir, action):
        """
        Convert action to new direction.
        Supports Direction enum, raw keys, or 3-element relative list [straight, right, left].
        """
        if action is None:
            return current_dir

        if isinstance(action, Direction):
            # Prevent reversing directly into itself
            opposites = {
                Direction.UP: Direction.DOWN,
                Direction.DOWN: Direction.UP,
                Direction.LEFT: Direction.RIGHT,
                Direction.RIGHT: Direction.LEFT,
            }
            if opposites.get(action) != current_dir:
                return action
            return current_dir

        # 3-element relative action [straight, right, left]
        clockwise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clockwise.index(current_dir)
        action_list = list(action)
        if action_list == [1, 0, 0]:
            return clockwise[idx]
        elif action_list == [0, 1, 0]:
            return clockwise[(idx + 1) % 4]
        elif action_list == [0, 0, 1]:
            return clockwise[(idx - 1) % 4]
        return current_dir

    def handle_human_input(self, key):
        """
        Handle keyboard input for the human-controlled snake.

        Arrow keys and WASD are supported.
        Prevents the snake from reversing directly.
        """

        key_directions = {
            pygame.K_UP: Direction.UP,
            pygame.K_w: Direction.UP,

            pygame.K_DOWN: Direction.DOWN,
            pygame.K_s: Direction.DOWN,

            pygame.K_LEFT: Direction.LEFT,
            pygame.K_a: Direction.LEFT,

            pygame.K_RIGHT: Direction.RIGHT,
            pygame.K_d: Direction.RIGHT
        }

        new_direction = key_directions.get(key)

        if new_direction is None:
            return

        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }

        if new_direction != opposite_directions[self.direction1]:
            self.direction1 = new_direction

    def play_step(self, action1=None, action2=None):
        """
        Execute one synchronous step for both snakes.
        action1: Human action (Direction or [straight, right, left])
        action2: AI action (Direction or [straight, right, left])
        Returns: (game_over, score1, score2, winner)
        """
        self.frame_iteration += 1

        # 1. Update directions
        if self.alive1:
            self.direction1 = self._resolve_direction(self.direction1, action1)
        if self.alive2:
            self.direction2 = self._resolve_direction(self.direction2, action2)

        # 2. Compute intended next head positions
        new_head1 = self._next_head(self.head1, self.direction1) if self.alive1 else self.head1
        new_head2 = self._next_head(self.head2, self.direction2) if self.alive2 else self.head2

        eliminated1 = False
        eliminated2 = False

        # 3. Collision Resolution

        # Determine whether either snake will eat food this frame
        snake1_eats = self.alive1 and self.food is not None and new_head1 == self.food
        snake2_eats = self.alive2 and self.food is not None and new_head2 == self.food

        eliminated1 = False
        eliminated2 = False

        # Rule A: Head-to-head collision and head swap
        if self.alive1 and self.alive2:
            if (
                new_head1 == new_head2
                or (
                    new_head1 == self.head2
                    and new_head2 == self.head1
                )
            ):
                eliminated1 = True
                eliminated2 = True

        # Rule B: Snake 1 collisions
        if self.alive1 and not eliminated1:

            # Wall collision
            if self.is_wall_collision(new_head1):
                eliminated1 = True

            # Self collision
            elif new_head1 in (
                self.snake1 if snake1_eats else self.snake1[:-1]
            ):
                eliminated1 = True

            # Opponent body collision
            elif self.alive2 and new_head1 in (
                self.snake2 if snake2_eats else self.snake2[:-1]
            ):
                eliminated1 = True

            elif not self.alive2 and new_head1 in self.snake2:
                eliminated1 = True

        # Rule C: Snake 2 collisions
        if self.alive2 and not eliminated2:

            # Wall collision
            if self.is_wall_collision(new_head2):
                eliminated2 = True

            # Self collision
            elif new_head2 in (
                self.snake2 if snake2_eats else self.snake2[:-1]
            ):
                eliminated2 = True

            # Opponent body collision
            elif self.alive1 and new_head2 in (
                self.snake1 if snake1_eats else self.snake1[:-1]
            ):
                eliminated2 = True

            elif not self.alive1 and new_head2 in self.snake1:
                eliminated2 = True

        # Apply eliminations
        if eliminated1:
            self.alive1 = False
        if eliminated2:
            self.alive2 = False

        # 4. Advance surviving snakes
        food_eaten = False

        # Advance Snake 1 if still alive
        if self.alive1:
            self.head1 = new_head1
            self.snake1.insert(0, self.head1)
            if self.head1 == self.food:
                self.score1 += 1
                food_eaten = True
            else:
                self.snake1.pop()

        # Advance Snake 2 if still alive
        if self.alive2:
            self.head2 = new_head2
            self.snake2.insert(0, self.head2)
            if self.head2 == self.food:
                self.score2 += 1
                food_eaten = True
            else:
                self.snake2.pop()

        # Respawn food if consumed
        if food_eaten:
            self._place_food()

        # 5. Check game over condition
        # Game ends when both snakes are eliminated or max match duration is reached
        game_over = False
        if (
    (not self.alive1 and not self.alive2)
    or self.frame_iteration >= self.max_frames
    or self.food is None
        ):
         game_over = True

        # Determine winner
        winner = None
        if game_over:
            winner = self.get_winner()

        # 6. Render UI
        self._update_ui()
        if self.speed > 0:
            self.clock.tick(self.speed)

        return game_over, self.score1, self.score2, winner

    def get_winner(self):
        """Determine winner based on final scores."""
        if self.score1 > self.score2:
            return "human"
        elif self.score2 > self.score1:
            return "ai"
        else:
            return "draw"

    def _draw_snake(self, snake, alive, outer_color, inner_color):
        """Draw a snake with head highlighting and eliminated state styling."""
        for i, point in enumerate(snake):
            if not alive:
                # Dim gray styling for crashed snake
                pygame.draw.rect(
                    self.display,
                    ELIMINATED_COLOR,
                    pygame.Rect(point.x, point.y, BLOCK_SIZE, BLOCK_SIZE),
                    border_radius=4,
                )
            else:
                # Active snake
                color = inner_color if i == 0 else outer_color
                pygame.draw.rect(
                    self.display,
                    color,
                    pygame.Rect(point.x, point.y, BLOCK_SIZE, BLOCK_SIZE),
                    border_radius=5,
                )

    def _update_ui(self):
        """Render two-snake playfield and dedicated stats header."""
        self.display.fill(BLACK)

        # Draw subtle grid in playable area
        for x in range(0, self.width, BLOCK_SIZE):
            pygame.draw.line(
                self.display, (25, 25, 35), (x, self.header_height), (x, self.height)
            )
        for y in range(self.header_height, self.height, BLOCK_SIZE):
            pygame.draw.line(
                self.display, (25, 25, 35), (0, y), (self.width, y)
            )

        # Draw both snakes
        self._draw_snake(self.snake1, self.alive1, HUMAN_COLOR_OUTER, HUMAN_COLOR_INNER)
        self._draw_snake(self.snake2, self.alive2, AI_COLOR_OUTER, AI_COLOR_INNER)

        # Draw shared food
        if self.food is not None:
            pygame.draw.circle(
                self.display,
                RED,
                (self.food.x + BLOCK_SIZE // 2, self.food.y + BLOCK_SIZE // 2),
                BLOCK_SIZE // 2 - 2,
            )

        # ==========================================================
        # DEDICATED 60PX HEADER SECTION (HUMAN VS AI)
        # ==========================================================
        header_bar = pygame.Rect(0, 0, self.width, self.header_height)
        pygame.draw.rect(self.display, (18, 20, 28), header_bar)
        pygame.draw.line(
            self.display,
            (50, 55, 75),
            (0, self.header_height - 1),
            (self.width, self.header_height - 1),
            2,
        )

        card_w = 140
        card_h = 44
        card_y = 8
        spacing = 16

        def draw_badge(index, label, value, value_color):
            card_x = spacing + index * (card_w + spacing)
            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
            pygame.draw.rect(self.display, (28, 31, 44), card_rect, border_radius=8)
            pygame.draw.rect(self.display, (55, 60, 80), card_rect, width=1, border_radius=8)

            lbl = HEADER_LABEL_FONT.render(label, True, (135, 140, 155))
            lbl_r = lbl.get_rect(center=(card_x + card_w // 2, card_y + 13))
            self.display.blit(lbl, lbl_r)

            val = HEADER_VALUE_FONT.render(str(value), True, value_color)
            val_r = val.get_rect(center=(card_x + card_w // 2, card_y + 30))
            self.display.blit(val, val_r)

        # Badge 0: HUMAN SCORE (Cyan/Blue)
        draw_badge(0, "HUMAN", self.score1, HUMAN_COLOR_INNER)

        # Badge 1: AI SCORE (Green)
        draw_badge(1, "AI SCORE", self.score2, AI_COLOR_INNER)

        # Badge 2: MODE
        draw_badge(2, "MODE", "HUMAN VS AI", (255, 210, 80))

        # Badge 3: DIFFICULTY
        diff_str = getattr(self, "difficulty_label", "MEDIUM")
        if "EASY" in diff_str.upper():
            diff_color = GREEN
        elif "HARD" in diff_str.upper():
            diff_color = (255, 80, 80)
        else:
            diff_color = (255, 185, 60)
        draw_badge(3, "DIFFICULTY", diff_str, diff_color)

        pygame.display.flip()


if __name__ == "__main__":
    game = TwoSnakeGame(speed=12)
    print("Testing TwoSnakeGame mechanics. Close window or wait for elimination...")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Step both snakes (using default forward motion until collision)
        game_over, s1, s2, winner = game.play_step(action1=None, action2=None)
        if game_over:
            print(f"Game Over! Final -> Human: {s1}, AI: {s2} | Winner: {winner}")
            pygame.time.wait(1500)
            break

    pygame.quit()

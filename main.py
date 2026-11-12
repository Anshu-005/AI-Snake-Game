import os
import sys
import pygame
import torch
import numpy as np
from pygame import sndarray

from game.snake_game import SnakeGame, Direction, Point, BLOCK_SIZE
from game.two_snake_game import TwoSnakeGame
from agent import Agent

# Initialize pygame
pygame.init()

# Initialize audio
try:
    pygame.mixer.init(
        frequency=44100,
        size=-16,
        channels=2
    )
    SOUND_ENABLED = True
except (pygame.error, Exception):
    SOUND_ENABLED = False


def create_tone(start_freq, end_freq, duration):
    if not SOUND_ENABLED:
        return None

    try:
        sample_rate = 44100
        samples = int(sample_rate * duration)
        if samples <= 0:
            return None

        frequencies = np.linspace(start_freq, end_freq, samples)
        phase = 2 * np.pi * np.cumsum(frequencies) / sample_rate
        envelope = np.linspace(1, 0, samples)

        wave = (np.sin(phase) * envelope * 0.25 * 32767).astype(np.int16)
        stereo = np.column_stack((wave, wave))

        return sndarray.make_sound(stereo)
    except Exception:
        return None


# Create sound effects safely
try:
    eat_sound = create_tone(650, 1000, 0.12)
    game_over_sound = create_tone(600, 140, 0.45)
    menu_sound = create_tone(500, 750, 0.08)
except Exception:
    eat_sound = None
    game_over_sound = None
    menu_sound = None


def play_effect(sound):
    if SOUND_ENABLED and sound is not None:
        try:
            sound.play()
        except Exception:
            pass


# Window configuration
WIDTH = 640
HEIGHT = 480

WHITE = (255, 255, 255)
BLACK = (15, 15, 25)
GREEN = (0, 220, 120)
BLUE = (50, 130, 255)
GRAY = (120, 120, 130)
CYAN = (0, 200, 255)
RED = (255, 75, 85)

FONT = pygame.font.SysFont("arial", 28)
SMALL_FONT = pygame.font.SysFont("arial", 22)
TITLE_FONT = pygame.font.SysFont("arial", 48, bold=True)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neural Network Snake")

clock = pygame.time.Clock()


def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)


# ---------------------------------------------------------------------------
# SCREENS
# ---------------------------------------------------------------------------

def main_menu():
    while True:
        clock.tick(30)
        screen.fill(BLACK)

        draw_text("NEURAL SNAKE", TITLE_FONT, GREEN, WIDTH // 2, 95)

        draw_text("1. Classic Mode",    FONT, WHITE,  WIDTH // 2, 205)
        draw_text("2. Human vs AI",     FONT, CYAN,   WIDTH // 2, 265)
        draw_text("3. AI Demo Mode",    FONT, BLUE,   WIDTH // 2, 325)
        draw_text("ESC. Exit",          FONT, GRAY,   WIDTH // 2, 410)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    play_effect(menu_sound)
                    return "classic"

                elif event.key in (pygame.K_2, pygame.K_KP2):
                    play_effect(menu_sound)
                    return "hvai"

                elif event.key in (pygame.K_3, pygame.K_KP3):
                    play_effect(menu_sound)
                    return "ai"

                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def select_difficulty():
    difficulties = {
        pygame.K_1: ("Easy",   8),
        pygame.K_2: ("Medium", 15),
        pygame.K_3: ("Hard",   25),
    }

    while True:
        clock.tick(30)
        screen.fill(BLACK)

        draw_text("SELECT DIFFICULTY", TITLE_FONT, GREEN, WIDTH // 2, 100)

        draw_text("1. Easy",   FONT, GREEN,         WIDTH // 2, 210)
        draw_text("2. Medium", FONT, WHITE,          WIDTH // 2, 270)
        draw_text("3. Hard",   FONT, (255, 80, 80),  WIDTH // 2, 330)
        draw_text("ESC - Back", FONT, GRAY,          WIDTH // 2, 410)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in difficulties:
                    play_effect(menu_sound)
                    return difficulties[event.key][1]

                elif event.key == pygame.K_ESCAPE:
                    return None


def pause_screen():
    paused = True

    while paused:
        clock.tick(30)
        screen.fill(BLACK)

        draw_text("PAUSED",           TITLE_FONT, GREEN, WIDTH // 2, 180)
        draw_text("Press P to Resume", FONT,      WHITE, WIDTH // 2, 270)
        draw_text("Press M for Menu",  FONT,      GRAY,  WIDTH // 2, 330)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_p, pygame.K_SPACE):
                    paused = False

                elif event.key in (pygame.K_m, pygame.K_ESCAPE):
                    return "menu"

    return "resume"


def game_over_screen(score, high_score):
    while True:
        clock.tick(30)
        screen.fill(BLACK)

        panel = pygame.Rect(100, 65, 440, 350)
        pygame.draw.rect(screen, (25, 27, 40),  panel, border_radius=20)
        pygame.draw.rect(screen, (65, 70, 90),  panel, width=2, border_radius=20)

        draw_text("GAME OVER",              TITLE_FONT, RED,   WIDTH // 2, 125)
        draw_text("YOUR SCORE",             FONT,       GRAY,  WIDTH // 2, 195)
        draw_text(str(score),               TITLE_FONT, WHITE, WIDTH // 2, 240)
        draw_text(f"PERSONAL BEST: {high_score}", FONT, GREEN, WIDTH // 2, 295)
        draw_text("R - Play Again",         FONT,       BLUE,  WIDTH // 2, 350)
        draw_text("M - Main Menu",          FONT,       GRAY,  WIDTH // 2, 390)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                elif event.key in (pygame.K_m, pygame.K_ESCAPE):
                    return "menu"


def hvai_result_screen(score1, score2, winner):
    """Display end-of-match results for Human vs AI mode."""
    if winner == "human":
        result_text  = "HUMAN WINS!"
        result_color = CYAN
    elif winner == "ai":
        result_text  = "AI WINS!"
        result_color = GREEN
    else:
        result_text  = "DRAW!"
        result_color = (255, 210, 80)

    while True:
        clock.tick(30)
        screen.fill(BLACK)

        # Panel
        panel = pygame.Rect(80, 55, 480, 370)
        pygame.draw.rect(screen, (22, 25, 38), panel, border_radius=20)
        pygame.draw.rect(screen, (65, 70, 95), panel, width=2, border_radius=20)

        # Result heading
        draw_text(result_text, TITLE_FONT, result_color, WIDTH // 2, 115)

        # Score row labels
        draw_text("HUMAN", FONT, GRAY, WIDTH // 2 - 110, 185)
        draw_text("AI",    FONT, GRAY, WIDTH // 2 + 110, 185)
        draw_text("VS",    FONT, (60, 65, 85), WIDTH // 2, 185)

        # Score values
        draw_text(str(score1), TITLE_FONT, CYAN,  WIDTH // 2 - 110, 235)
        draw_text(str(score2), TITLE_FONT, GREEN, WIDTH // 2 + 110, 235)

        # Divider line
        pygame.draw.line(screen, (55, 60, 80), (110, 275), (530, 275), 1)

        # Controls
        draw_text("R - Rematch",   FONT, BLUE, WIDTH // 2, 310)
        draw_text("M - Main Menu", FONT, GRAY, WIDTH // 2, 360)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "rematch"
                elif event.key in (pygame.K_m, pygame.K_ESCAPE):
                    return "menu"


# ---------------------------------------------------------------------------
# CACHED AI AGENT
# ---------------------------------------------------------------------------

AI_AGENT = None


def get_ai_agent():
    global AI_AGENT
    if AI_AGENT is None:
        agent = Agent(training=False)
        model_path = (
            "model.pth"
            if os.path.exists("model.pth")
            else os.path.join("model", "model.pth")
        )
        if os.path.exists(model_path):
            try:
                agent.model.load_state_dict(
                    torch.load(model_path, map_location="cpu", weights_only=True)
                )
                agent.model.eval()
                # Warm up PyTorch inference engine
                with torch.no_grad():
                    dummy = torch.zeros((1, 11), dtype=torch.float)
                    agent.model(dummy)
                print(f"Loaded trained AI model from {model_path}")
            except Exception as e:
                print(f"Error loading model: {e}")
        else:
            print(f"Model file not found at {model_path}!")
        AI_AGENT = agent
    return AI_AGENT


# ---------------------------------------------------------------------------
# AI STATE ADAPTER FOR TWO-SNAKE ENVIRONMENT
# ---------------------------------------------------------------------------

def get_ai_state_for_two_snake(game: TwoSnakeGame) -> np.ndarray:
    """
    Compute the same 11-feature state vector that agent.get_state() produces,
    but adapted for Snake 2 (the AI) inside TwoSnakeGame.

    Danger is defined as: wall OR own body OR opponent's body.
    """
    head = game.head2
    dir_ = game.direction2

    point_l = Point(head.x - BLOCK_SIZE, head.y)
    point_r = Point(head.x + BLOCK_SIZE, head.y)
    point_u = Point(head.x,              head.y - BLOCK_SIZE)
    point_d = Point(head.x,              head.y + BLOCK_SIZE)

    dir_l = dir_ == Direction.LEFT
    dir_r = dir_ == Direction.RIGHT
    dir_u = dir_ == Direction.UP
    dir_d = dir_ == Direction.DOWN

    # A cell is dangerous if it's a wall, snake2's own body, or snake1's body
    snake2_body = set(game.snake2[1:])   # exclude current head
    snake1_body = set(game.snake1)

    def is_dangerous(pt: Point) -> bool:
        return (
            game.is_wall_collision(pt)
            or pt in snake2_body
            or pt in snake1_body
        )

    # Food direction (safe when food is None)
    food = game.food
    food_left  = food.x < head.x if food else False
    food_right = food.x > head.x if food else False
    food_up    = food.y < head.y if food else False
    food_down  = food.y > head.y if food else False

    state = [
        # Danger straight
        (dir_r and is_dangerous(point_r))
        or (dir_l and is_dangerous(point_l))
        or (dir_u and is_dangerous(point_u))
        or (dir_d and is_dangerous(point_d)),

        # Danger right (clockwise turn)
        (dir_u and is_dangerous(point_r))
        or (dir_d and is_dangerous(point_l))
        or (dir_l and is_dangerous(point_u))
        or (dir_r and is_dangerous(point_d)),

        # Danger left (counter-clockwise turn)
        (dir_d and is_dangerous(point_r))
        or (dir_u and is_dangerous(point_l))
        or (dir_r and is_dangerous(point_u))
        or (dir_l and is_dangerous(point_d)),

        # Current direction
        dir_l,
        dir_r,
        dir_u,
        dir_d,

        # Food location relative to AI head
        food_left,
        food_right,
        food_up,
        food_down,
    ]

    return np.array(state, dtype=int)


# ---------------------------------------------------------------------------
# GAME RUNNERS
# ---------------------------------------------------------------------------

def run_game(mode, speed):
    """Run Classic Mode or AI Demo Mode."""
    game = SnakeGame(speed=speed)
    game.progressive_speed = True

    game.mode_label = "AI MODE" if mode == "ai" else "CLASSIC"

    if speed == 8:
        game.difficulty_label = "EASY"
    elif speed == 15:
        game.difficulty_label = "MEDIUM"
    else:
        game.difficulty_label = "HARD"

    if mode == "ai":
        agent = get_ai_agent()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    result = pause_screen()
                    if result == "menu":
                        return "menu"

                elif event.key == pygame.K_ESCAPE:
                    return "menu"

                elif mode == "classic":
                    if event.key in (pygame.K_LEFT, pygame.K_a) and game.direction != Direction.RIGHT:
                        game.direction = Direction.LEFT
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and game.direction != Direction.LEFT:
                        game.direction = Direction.RIGHT
                    elif event.key in (pygame.K_UP, pygame.K_w) and game.direction != Direction.DOWN:
                        game.direction = Direction.UP
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and game.direction != Direction.UP:
                        game.direction = Direction.DOWN

        # AI movement decision
        if mode == "ai":
            state = agent.get_state(game)
            with torch.no_grad():
                prediction = agent.model(torch.tensor(state, dtype=torch.float))
            move = torch.argmax(prediction).item()
            action = [0, 0, 0]
            action[move] = 1
        else:
            action = None

        previous_score = game.score
        _, done, score = game.play_step(action)

        if score > previous_score:
            play_effect(eat_sound)

        if done:
            play_effect(game_over_sound)
            result = game_over_screen(score, game.high_score)

            if result == "restart":
                game.reset()
                continue
            return "menu"


def run_hvai_game(speed):
    """
    Human vs AI mode.
    Human controls Snake 1 with arrow keys / WASD.
    AI controls Snake 2 using the trained model.
    """
    difficulty_map = {8: "EASY", 15: "MEDIUM", 25: "HARD"}

    game = TwoSnakeGame(speed=speed)
    game.difficulty_label = difficulty_map.get(speed, "MEDIUM")

    agent = get_ai_agent()

    # Buffer the latest human direction between frames
    pending_direction = None

    while True:
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    result = pause_screen()
                    if result == "menu":
                        return "menu"

                elif event.key == pygame.K_ESCAPE:
                    return "menu"

                # Human directional input (stored; applied once per game step)
                elif event.key in (pygame.K_LEFT,  pygame.K_a):
                    pending_direction = Direction.LEFT
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    pending_direction = Direction.RIGHT
                elif event.key in (pygame.K_UP,    pygame.K_w):
                    pending_direction = Direction.UP
                elif event.key in (pygame.K_DOWN,  pygame.K_s):
                    pending_direction = Direction.DOWN

        # --- AI decision (only when snake2 is still alive) ---
        if game.alive2:
            ai_state = get_ai_state_for_two_snake(game)
            with torch.no_grad():
                pred = agent.model(torch.tensor(ai_state, dtype=torch.float))
            ai_move = torch.argmax(pred).item()
            ai_action = [0, 0, 0]
            ai_action[ai_move] = 1
        else:
            ai_action = None

        # --- Step both snakes ---
        prev_s1 = game.score1
        prev_s2 = game.score2

        game_over, s1, s2, winner = game.play_step(
            action1=pending_direction,
            action2=ai_action,
        )
        pending_direction = None   # consume buffered direction

        # Play eat sound if either score increased
        if s1 > prev_s1 or s2 > prev_s2:
            play_effect(eat_sound)

        # --- Game-over handling ---
        if game_over:
            play_effect(game_over_sound)
            result = hvai_result_screen(s1, s2, winner)

            if result == "rematch":
                game.reset()
                game.difficulty_label = difficulty_map.get(speed, "MEDIUM")
                pending_direction = None
                continue

            return "menu"


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    # Pre-load the AI model so there's no delay when entering AI modes
    get_ai_agent()

    while True:
        mode = main_menu()

        speed = select_difficulty()
        if speed is None:
            continue   # ESC on difficulty → back to main menu

        if mode == "hvai":
            result = run_hvai_game(speed)
        else:
            result = run_game(mode, speed)

        if result == "menu":
            continue


if __name__ == "__main__":
    main()

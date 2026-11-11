import os
import sys
import pygame
import torch
import numpy as np
from pygame import sndarray

from game.snake_game import SnakeGame, Direction
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

FONT = pygame.font.SysFont("arial", 28)
TITLE_FONT = pygame.font.SysFont("arial", 48, bold=True)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neural Network Snake")

clock = pygame.time.Clock()


def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)


def main_menu():
    while True:
        clock.tick(30)
        screen.fill(BLACK)

        draw_text(
            "NEURAL SNAKE",
            TITLE_FONT,
            GREEN,
            WIDTH // 2,
            110
        )

        draw_text(
            "1. Classic Mode",
            FONT,
            WHITE,
            WIDTH // 2,
            220
        )

        draw_text(
            "2. AI Mode",
            FONT,
            BLUE,
            WIDTH // 2,
            280
        )

        draw_text(
            "ESC. Exit",
            FONT,
            GRAY,
            WIDTH // 2,
            360
        )

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
                    return "ai"

                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def select_difficulty():

        difficulties = {
            pygame.K_1: ("Easy", 8),
            pygame.K_2: ("Medium", 15),
            pygame.K_3: ("Hard", 25)
        }

        while True:
            screen.fill(BLACK)

            draw_text(
                "SELECT DIFFICULTY",
                TITLE_FONT,
                GREEN,
                WIDTH // 2,
                100
            )

            draw_text("1. Easy", FONT, GREEN, WIDTH // 2, 210)
            draw_text("2. Medium", FONT, WHITE, WIDTH // 2, 270)
            draw_text("3. Hard", FONT, (255, 80, 80), WIDTH // 2, 330)

            draw_text(
                "ESC - Back",
                FONT,
                GRAY,
                WIDTH // 2,
                410
            )

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

        draw_text(
            "PAUSED",
            TITLE_FONT,
            GREEN,
            WIDTH // 2,
            180
        )

        draw_text(
            "Press P to Resume",
            FONT,
            WHITE,
            WIDTH // 2,
            270
        )

        draw_text(
            "Press M for Menu",
            FONT,
            GRAY,
            WIDTH // 2,
            330
        )

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

        # Decorative panel
        panel = pygame.Rect(100, 65, 440, 350)

        pygame.draw.rect(
            screen,
            (25, 27, 40),
            panel,
            border_radius=20
        )

        pygame.draw.rect(
            screen,
            (65, 70, 90),
            panel,
            width=2,
            border_radius=20
        )

        # Heading
        draw_text(
            "GAME OVER",
            TITLE_FONT,
            (255, 75, 85),
            WIDTH // 2,
            125
        )

        # Final score
        draw_text(
            "YOUR SCORE",
            FONT,
            GRAY,
            WIDTH // 2,
            195
        )

        draw_text(
            str(score),
            TITLE_FONT,
            WHITE,
            WIDTH // 2,
            240
        )

        # High score
        draw_text(
            f"PERSONAL BEST: {high_score}",
            FONT,
            GREEN,
            WIDTH // 2,
            295
        )

        # Controls
        draw_text(
            "R - Play Again",
            FONT,
            BLUE,
            WIDTH // 2,
            350
        )

        draw_text(
            "M - Main Menu",
            FONT,
            GRAY,
            WIDTH // 2,
            390
        )

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


# Cached AI agent for instantaneous start
AI_AGENT = None


def get_ai_agent():
    global AI_AGENT
    if AI_AGENT is None:
        agent = Agent(training=False)
        model_path = "model.pth" if os.path.exists("model.pth") else os.path.join("model", "model.pth")
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


def run_game(mode,speed):
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
        # Handle pause, menu, and directional events
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
                prediction = agent.model(
                    torch.tensor(state, dtype=torch.float)
                )
            move = torch.argmax(prediction).item()
            action = [0, 0, 0]
            action[move] = 1
        else:
            action = None

        # Perform game step
        previous_score = game.score
        _, done, score = game.play_step(action)

        # Play food sound when score increases
        if score > previous_score:
            play_effect(eat_sound)

        # Handle game over condition
        if done:
            play_effect(game_over_sound)
            result = game_over_screen(score, game.high_score)

            if result == "restart":
                game.reset()
                continue
            return "menu"


def main():
    while True:
        mode = main_menu()

        speed = select_difficulty()

        if speed is None:
            continue

        result = run_game(mode, speed)

        if result == "menu":
            continue


if __name__ == "__main__":
    main()

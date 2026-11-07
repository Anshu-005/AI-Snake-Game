import os
import sys
import time
import tempfile

# Suppress Matplotlib cache directory warnings
os.environ.setdefault('MPLCONFIGDIR', os.path.join(tempfile.gettempdir(), 'matplotlib_cache'))

import pygame
import matplotlib.pyplot as plt
from agent import Agent
from game.snake_game import SnakeGame

plt.ion()


def get_screen_resolution():
    """Detect screen resolution on Windows with DPI scaling awareness."""
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
        user32 = ctypes.windll.user32
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        if w > 0 and h > 0:
            return w, h
    except Exception:
        pass
    return 1536, 864


# Compute non-overlapping side-by-side coordinates
SCREEN_W, SCREEN_H = get_screen_resolution()
TOP_Y = max(40, (SCREEN_H - 520) // 2)

# Left Window: Snake Game (640x480)
GAME_X = 20
GAME_Y = TOP_Y
GAME_W = 640
GAME_H = 480

# Right Window: Matplotlib Plot (placed right of Snake Game with 35px gap)
PLOT_X = GAME_X + GAME_W + 35
PLOT_W = max(550, min(780, SCREEN_W - PLOT_X - 25))
PLOT_H = 500
PLOT_Y = TOP_Y

# Initialize figure
fig = plt.figure(figsize=(7.0, 5.0))


def set_plot_position(x=PLOT_X, y=PLOT_Y, w=PLOT_W, h=PLOT_H):
    """Enforce exact window position and size for Matplotlib visualization."""
    try:
        mngr = plt.get_current_fig_manager()
        if hasattr(mngr, 'window'):
            if hasattr(mngr.window, 'geometry'):
                mngr.window.geometry(f"{int(w)}x{int(h)}+{int(x)}+{int(y)}")
                if hasattr(mngr.window, 'update'):
                    mngr.window.update()
            elif hasattr(mngr.window, 'wm_geometry'):
                mngr.window.wm_geometry(f"{int(w)}x{int(h)}+{int(x)}+{int(y)}")

            # Enforce on Win32 HWND directly
            try:
                import ctypes
                hwnd = mngr.window.winfo_id()
                if hwnd:
                    # SWP_NOZORDER = 0x0004, SWP_SHOWWINDOW = 0x0040
                    ctypes.windll.user32.SetWindowPos(
                        hwnd, 0, int(x), int(y), int(w), int(h), 0x0004 | 0x0040
                    )
            except Exception:
                pass
    except Exception:
        pass


def plot(scores, mean_scores, time_left_str=""):
    plt.clf()
    title = f'AI Snake Training ({time_left_str} remaining)' if time_left_str else 'AI Snake Training'
    plt.title(title, fontsize=12, fontweight='bold')
    plt.xlabel('Number of Games', fontsize=10)
    plt.ylabel('Score', fontsize=10)
    plt.plot(scores, label='Score', color='#2ca02c', alpha=0.8)
    plt.plot(mean_scores, label='Mean Score', color='#1f77b4', linewidth=2)
    plt.ylim(ymin=0)

    if len(scores) > 0:
        plt.text(len(scores) - 1, scores[-1], f"  {scores[-1]}", fontweight='bold', color='#2ca02c')
        plt.text(len(mean_scores) - 1, mean_scores[-1], f"  {mean_scores[-1]:.2f}", fontweight='bold', color='#1f77b4')

    plt.legend(loc='upper left')
    plt.tight_layout()

    # Re-enforce position on redraw
    set_plot_position(PLOT_X, PLOT_Y, PLOT_W, PLOT_H)

    plt.show(block=False)
    plt.pause(0.01)


def train(duration_seconds=120):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0

    print("=" * 65)
    print(f"Starting Snake AI Training for {duration_seconds // 60} minutes ({duration_seconds} seconds)")
    print(f"Detected Screen: {SCREEN_W}x{SCREEN_H}")
    print("Non-Overlapping Window Layout:")
    print(f"  • Left  : Snake Game  -> x={GAME_X}, y={GAME_Y} (width={GAME_W}, height={GAME_H})")
    print(f"  • Right : Graph Window-> x={PLOT_X}, y={PLOT_Y} (width={PLOT_W}, height={PLOT_H})")
    print("=" * 65)

    # 1. Initialize visualization window and anchor position immediately
    set_plot_position(PLOT_X, PLOT_Y, PLOT_W, PLOT_H)
    plot([], [], f"{duration_seconds // 60}m 00s")

    # 2. Initialize Snake Game and anchor position on the left
    agent = Agent()
    game = SnakeGame(speed=40, window_pos=(GAME_X, GAME_Y))
    game.set_window_pos(GAME_X, GAME_Y)

    start_time = time.time()
    steps = 0

    while True:
        elapsed = time.time() - start_time
        if elapsed >= duration_seconds:
            print("\n" + "=" * 65)
            print(f"Training timer reached ({duration_seconds // 60} minutes). Wrapping up...")
            break

        remaining = max(0, int(duration_seconds - elapsed))
        mins, secs = divmod(remaining, 60)
        time_left_str = f"{mins}m {secs:02d}s"

        # Update Pygame window title with live countdown
        pygame.display.set_caption(f'AI Snake Game - Time Left: {time_left_str} | Score: {game.score}')

        # Re-verify window positions for the first 5 frames to ensure OS placement sticks
        steps += 1
        if steps <= 5:
            game.set_window_pos(GAME_X, GAME_Y)
            set_plot_position(PLOT_X, PLOT_Y, PLOT_W, PLOT_H)

        # 1. Get old state
        state_old = agent.get_state(game)

        # 2. Get action from agent
        final_move = agent.get_action(state_old)

        # 3. Perform action
        reward, done, score = game.play_step(final_move)

        # 4. Get new state
        state_new = agent.get_state(game)

        # 5. Train short-term memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # 6. Remember experience
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games += 1

            # Train replay buffer (long-term memory)
            agent.train_long_memory()

            # Save model when record improves
            if score > record:
                record = score
                agent.model.save()

            print(f'Game: {agent.n_games:3d} | Score: {score:2d} | Record: {record:2d} | Time Left: {time_left_str}')

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)

            plot(plot_scores, plot_mean_scores, time_left_str)

    # Training completed: Finalize and display summary
    print("=" * 65)
    print("TRAINING SUMMARY:")
    print(f"  • Total Games Played: {agent.n_games}")
    print(f"  • Highest Score     : {record}")
    print(f"  • Average Score     : {total_score / max(1, agent.n_games):.2f}")
    print(f"  • Model Checkpoint  : Saved to model/model.pth")
    print("=" * 65)

    # Save final plot figure to disk
    plt.savefig('training_progress.png')
    print("Saved final training plot to 'training_progress.png'.")

    # Final plot render with 'Completed' title
    plot(plot_scores, plot_mean_scores, "Completed")
    pygame.quit()

    print("Close the graph window to exit.")
    try:
        if sys.stdin and sys.stdin.isatty():
            plt.show(block=True)
        else:
            plt.pause(1.0)
            plt.close('all')
    except Exception:
        plt.close('all')


if __name__ == '__main__':
    train()

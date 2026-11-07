import os
import torch
from agent import Agent
from game.snake_game import SnakeGame

def play():
    agent = Agent()
    game = SnakeGame(speed=15)

    # Load trained model (check model/model.pth or root model.pth)
    model_path = "model/model.pth" if os.path.exists("model/model.pth") else "model.pth"
    if os.path.exists(model_path):
        agent.model.load_state_dict(
            torch.load(model_path, map_location="cpu", weights_only=True)
        )
        agent.model.eval()
        print(f"Loaded trained model from {model_path}")
    else:
        print(f"Warning: No checkpoint found at {model_path}. Running untrained agent.")

    # Disable random exploration (100% exploitation)
    agent.n_games = 1000

    while True:
        state = agent.get_state(game)
        final_move = agent.get_action(state)
        reward, done, score = game.play_step(final_move)

        if done:
            print("Game Over! Final Score:", score)
            game.reset()

if __name__ == "__main__":
    play()

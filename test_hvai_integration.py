import numpy as np
import torch

from game.two_snake_game import TwoSnakeGame
from main import get_ai_state_for_two_snake, get_ai_agent

game = TwoSnakeGame(speed=15)

state = get_ai_state_for_two_snake(game)

print("AI State:", state)
print("State shape:", state.shape)

assert state.shape == (11,)
assert np.isfinite(state).all()

agent = get_ai_agent()

with torch.no_grad():
    prediction = agent.model(
        torch.tensor(state, dtype=torch.float32)
    )

print("AI Prediction:", prediction)
print("Prediction shape:", prediction.shape)

assert prediction.shape == (1, 3)

print("\n[PASS] Human vs AI integration test")
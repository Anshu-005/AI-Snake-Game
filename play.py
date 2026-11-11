import torch
from agent import Agent
from game.snake_game import SnakeGame

def evaluate():
    agent = Agent()
    game = SnakeGame()

    agent.model.load_state_dict(
    torch.load(
        "dueling_double_dqn_per.pth",
        map_location="cpu"
    )
)

    # Disable random exploration
    agent.epsilon = 0

    scores = []

    for episode in range(50):
        game.reset()
        done = False

        while not done:
            state = agent.get_state(game)

            with torch.no_grad():
                prediction = agent.model(
                    torch.tensor(state, dtype=torch.float)
                )

            move = prediction.argmax().item()

            action = [0, 0, 0]
            action[move] = 1

            _, done, score = game.play_step(action)

        scores.append(score)

        print(f"Episode {episode + 1}: Score = {score}")

    print("\nEvaluation Results")
    print("Highest:", max(scores))
    print("Average:", sum(scores) / len(scores))

    pygame.quit()


if __name__ == "__main__":
    import pygame
    evaluate()
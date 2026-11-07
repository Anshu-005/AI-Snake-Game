from game.snake_game import SnakeGame
from agent import Agent


def test():
    agent = Agent()
    loaded = agent.model.load('model/model.pth')
    if loaded:
        print("Successfully loaded model from model/model.pth")
    else:
        print("No trained model found at model/model.pth. Running untrained agent.")

    # Disable random moves (100% exploitation of trained policy)
    agent.epsilon = -1

    # Run at human-watchable speed
    game = SnakeGame(speed=20)
    games_played = 0

    while True:
        state = agent.get_state(game)
        action = agent.get_action(state)
        reward, done, score = game.play_step(action)

        if done:
            games_played += 1
            print(f"Game {games_played} | Score: {score}")
            game.reset()


if __name__ == '__main__':
    test()


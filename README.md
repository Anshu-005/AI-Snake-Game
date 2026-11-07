# Neural Network Snake with Deep Q-Learning

An AI-powered Snake game trained using Reinforcement Learning (Deep Q-Learning / DQN) built with PyTorch and Pygame.

## Project Structure

```
├── game/
│   ├── __init__.py
│   └── snake_game.py       # Pygame environment, game mechanics, and rendering
├── model/
│   ├── __init__.py
│   ├── neural_network.py  # Linear_QNet architecture and QTrainer optimization
│   └── model.pth          # Saved model weights checkpoint
├── agent.py               # DQN Agent with state representation, memory, and training
├── helper.py              # Real-time training progress plotting (Matplotlib)
├── train.py               # Entrypoint to run AI training
├── test.py                # Entrypoint to watch trained AI play
├── requirements.txt       # Project dependencies
└── README.md
```

## State Representation (11 inputs)
The agent observes an 11-dimensional binary vector representing:
- **Danger (3)**: Danger Straight, Danger Right, Danger Left
- **Current Direction (4)**: Moving Left, Right, Up, or Down
- **Food Location (4)**: Food is Left, Right, Up, or Down relative to the snake's head

## Actions (3 outputs)
- `[1, 0, 0]`: Continue Straight
- `[0, 1, 0]`: Turn Right
- `[0, 0, 1]`: Turn Left

## Installation & Setup

1. **Activate the virtual environment**:
   ```powershell
   .\venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

- **Train the AI Agent**:
  ```bash
  python train.py
  ```

- **Watch Trained AI Play**:
  ```bash
  python test.py
  ```

- **Play Manually**:
  ```bash
  python game/snake_game.py
  ```
  Use the Arrow Keys to steer the snake.

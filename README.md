<div align="center">

# 🐍 Neural Network Snake Game

*A classic Snake game powered by Deep Reinforcement Learning — featuring a trained AI agent, an AI Demo Mode, and a competitive Human vs AI mode.*

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.x-yellow?style=for-the-badge&logo=python&logoColor=white)](https://www.pygame.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

## 🎯 About the Project

This project combines a fully playable arcade Snake game with a **Deep Q-Learning (DQN)** agent trained using PyTorch. Rather than following hardcoded rules, the agent learns to navigate the grid, collect food, and avoid collisions entirely through trial and error across hundreds of training episodes.

The project ships with three game modes:

- **Classic Mode** — play Snake yourself with keyboard controls.
- **AI Demo Mode** — watch the trained neural network play autonomously.
- **Human vs AI Mode** — compete head-to-head against the AI on a shared grid.

---

## ✨ Features

- 🎮 **Three game modes** — Classic, AI Demo, and Human vs AI.
- 🧠 **Dueling DQN architecture** — separates state-value and action-advantage estimation for more stable learning.
- 🔁 **Double DQN updates** — decouples action selection from value evaluation to reduce overestimation.
- 📦 **Prioritized Experience Replay (PER)** — samples informative transitions more frequently with importance-sampling correction.
- 🎯 **Target network** — periodic weight synchronization for stable Q-value targets.
- 🐍 **Two-snake environment** — shared food, independent scores, full collision handling, and winner determination.
- 💾 **Model persistence** — trained weights saved and loaded automatically.
- 🖥️ **Dedicated game header** — always-visible 60 px status bar showing scores, mode, and difficulty.
- 🔊 **Sound effects** — synthesized audio feedback for food, game over, and menu events.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Core programming language |
| **Pygame** | Game loop, rendering, keyboard input, and audio |
| **PyTorch** | Neural network definition, training, and inference |
| **NumPy** | State vector construction and numerical operations |

---

## 📁 Project Structure

```text
Neural-Network-Snake/
├── game/
│   ├── __init__.py
│   ├── snake_game.py        # Single-snake RL environment (Classic & AI Demo)
│   └── two_snake_game.py    # Two-snake competitive environment (Human vs AI)
├── model/
│   ├── __init__.py
│   └── neural_network.py    # Dueling DQN architecture and Q-Trainer
├── agent.py                 # RL agent: state extraction, memory, action selection
├── train.py                 # Training loop with PER and score plotting
├── play.py                  # Standalone play script
├── test_model.py            # Model inference tests
├── test_two_snake.py        # Two-snake mechanics test suite (12 tests)
├── replay_buffer.py         # Prioritized Experience Replay buffer
├── main.py                  # Entry point: menu, difficulty, game-mode routing
├── model.pth                # Trained model checkpoint
├── requirements.txt
├── highscore.txt
└── README.md
```

---

## 🎮 Game Modes

### 1. Classic Mode
Play traditional Snake. Collect food, grow your snake, and avoid walls and your own body. Controlled entirely by the keyboard.

### 2. AI Demo Mode
The trained DQN agent controls the snake automatically. Useful for watching the learned policy in action and benchmarking the agent.

### 3. Human vs AI Mode
Two snakes share a single grid and compete for the same food.

| Rule | Detail |
|------|--------|
| **Shared food** | Only one food item exists; both snakes race for it |
| **Independent scores** | Each snake tracks its own score |
| **Wall / self collision** | Eliminates the snake that crashes |
| **Opponent body collision** | Eliminates the snake that runs into the other |
| **Head-to-head / head-swap** | Both snakes are eliminated simultaneously |
| **Survival** | If one snake is eliminated, the other continues |
| **Result** | Higher score wins; equal scores result in a draw |

---

## ⌨️ Controls

| Key | Action |
|-----|--------|
| `Arrow Keys` or `W A S D` | Move the human-controlled snake |
| `P` or `Space` | Pause / Resume |
| `M` or `Esc` | Return to main menu |
| `R` | Restart (from game-over or result screen) |

> Controls may vary slightly depending on the active screen and game mode.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or later
- Git
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Anshu-005/AI-Snake-Game.git
cd AI-Snake-Game
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Game

```bash
python main.py
```

Select a game mode from the main menu, then choose a difficulty (Easy / Medium / Hard). The AI model is loaded automatically at startup for instant entry into AI-powered modes.

---

## 🏋️ Training the Agent

```bash
python train.py
```

The training loop runs the agent through multiple game episodes, updating the network with Double DQN + PER after each step. A live score plot is displayed during training. The best model checkpoint is saved to `model.pth`.

> Training duration depends on your hardware. The included checkpoint was trained for approximately 300–400 episodes.

---

## 🧠 Reinforcement Learning Details

### State Representation (11 features)

The agent observes an 11-dimensional binary vector:

```
[ danger_straight,  danger_right,  danger_left,
  dir_left,  dir_right,  dir_up,  dir_down,
  food_left, food_right, food_up, food_down ]
```

### Action Space

The agent selects one of three **relative** actions each step:

| Index | Action |
|-------|--------|
| `0` | Continue straight |
| `1` | Turn right (clockwise) |
| `2` | Turn left (counter-clockwise) |

### Reward Signal

| Event | Reward |
|-------|--------|
| Eat food | `+10` |
| Game over (collision) | `−10` |
| Neutral move | `0` |

### Learning Components

- **Dueling DQN** — splits the network into a value stream and an advantage stream; combined to produce Q-values per action.
- **Double DQN** — the online network selects the next action; the target network evaluates it, reducing overestimation bias.
- **Prioritized Experience Replay** — transitions with higher TD error are sampled more often; importance-sampling weights correct the resulting bias.
- **Target network** — a periodically synchronized copy of the online network provides stable training targets.
- **Epsilon-greedy exploration** — starts with high randomness and decays as the agent gains experience.

> **Note on Human vs AI mode:** The AI opponent uses the trained single-snake model with an adapted state representation that also encodes the human snake's body as obstacles. The model was not specifically trained through competitive two-snake matches; its behaviour in that mode reflects a transferred single-snake policy.

---

## 🧪 Running Tests

```bash
python test_two_snake.py
```

The test suite covers 12 mechanics checks:

- Independent snake initialization and state
- Shared food consumption and score attribution
- Wall and self-collision detection
- Head-to-head and head-swap collision detection
- Winner and draw determination
- Moving-tail edge cases (tail vacates vs. stays on food)
- Valid food placement and full-board handling
- Human keyboard controls and reversal prevention

---

## 📊 Training & Evaluation Notes

A recorded evaluation run of the combined Dueling DQN + Double DQN + PER agent reported:

| Metric | Value |
|--------|-------|
| Highest score | **71** |
| Average score | **35.6** |

> These are historical results from a specific evaluation run, not a performance guarantee. Results can vary between runs, random seeds, and hardware.

---

## 💾 Model Checkpoint

The game loads the trained model from `model.pth` in the project root, with a fallback to `model/model.pth`.

If you plan to publish the checkpoint, check its file size against [GitHub's current limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files). For large checkpoints, consider [Git LFS](https://git-lfs.github.com/) or attaching the file as a [release asset](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).

---

## ⚠️ Current Limitations

- The agent was trained in a single-snake environment and has not undergone dedicated competitive training.
- Human vs AI behaviour is an adapted transfer of the existing policy, not an opponent-aware learned strategy.
- Performance varies between runs and game configurations.

---

## 🔮 Future Improvements

- [ ] Train the agent in a dedicated two-snake competitive environment.
- [ ] Add opponent-aware state features and shaped rewards for competitive play.
- [ ] Compare the transferred policy against a competitively trained agent.
- [ ] Track and visualize training rewards and evaluation metrics over time.
- [ ] Add reproducible evaluation across multiple seeds and game configurations.

---

## 🤝 Contributing

Suggestions, bug reports, and pull requests are welcome!

For substantial changes, please open an issue first to discuss the proposed improvement.

1. Fork the project
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

<div align="center">
  <p>Built with ❤️ using Python, Pygame, and PyTorch</p>
</div>

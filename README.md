# Vertex Velocity

![](https://github.com/drakes00/vertex-velocity/actions/workflows/lint.yaml/badge.svg)
![](https://github.com/drakes00/vertex-velocity/actions/workflows/ward.yaml/badge.svg)

## A Geometry Dash Recreation for Reinforcement Learning

Vertex Velocity is a recreation of the popular rhythm-based platformer, Geometry Dash, built in Python. Beyond just a game, it serves as a robust environment for training reinforcement learning (RL) agents using genetic algorithms.

## 🎮 Game Modes

### 🏃 Normal Mode
Play the game manually and test your skills.
```bash
python -m vertex_velocity.game -l maps/tilemap.json
```

### 🏗️ Level Editor
Design and build your own levels with an intuitive GUI.
```bash
python -m vertex_velocity.levelEditor -i maps/my_level.json
```

### 🤖 AI powered (RL)
Train an AI from scratch or watch a trained model play with real-time neural network visualization.
- **Training**: `python -m vertex_velocity.RLGame -l maps/tilemap.json --train`
- **Watch**: `python -m vertex_velocity.RLGame -l maps/tilemap.json -i best_player.json`

### 📜 Scripted Mode
Record your gameplay to a script or replay a previously recorded run.
- **Record**: `python -m vertex_velocity.scriptedGame -l maps/tilemap.json -o scripts/winner.json`
- **Replay**: `python -m vertex_velocity.scriptedGame -l maps/tilemap.json -i scripts/winner.json`

## ✨ Key Features

- **Genetic Algorithm AI**: Trains an AI using evolution. The AI learns to navigate obstacles by trial and error, with support for parallel training to speed up the process.
- **Neural Network Visualization**: See exactly what the AI is "thinking" with an overlay of its activated neurons (presence/absence of spikes, bricks, etc.).
- **Built-in Level Editor**: Full-featured editor to place/remove tiles, with camera navigation and JSON export/import.
- **Scripting System**: Record inputs and replay them perfectly. Useful for sharing levels and "TAS" (Tool-Assisted Speedrun) style replays.
- **Particle System**: Dynamic dust particles for a more polished feel.
- **Tilemap System**: Robust grid-based system supporting different tile types like bricks and spikes.

## ⌨️ Controls

### Game / Replay
- **UP / SPACE**: Jump
- **ESC / Q**: Quit

### Level Editor
- **Left Click**: Place current tile
- **Right Click**: Remove tile
- **Arrow Keys**: Move camera
- **CTRL + S**: Save level
- **ESC / Q**: Quit

## 🛠️ Getting Started

### Prerequisites
- Python 3.13+
- [Poetry](https://python-poetry.org/) (recommended)

### Installation
```bash
# Clone the repository
git clone https://github.com/drakes00/vertex-velocity.git
cd vertex_velocity

# Install dependencies
poetry install
```

## 🚀 AI Training

The AI uses a custom Neural Network architecture that senses its surroundings (Bricks, Spikes, Air) at specific offsets relative to the player. During training:
1. A population of 1000 agents is initialized.
2. Agents run in parallel using multiple CPU cores.
3. The best-performing agent (highest score) is saved to `best_player.json`.
4. You can then refine the training by loading that player back in using `-i best_player.json --train`.

## 🧪 Technologies Used

- **Python**: Core logic and AI.
- **Pygame**: Rendering and input handling.
- **Tqdm**: Progress visualization for parallel training.
- **Poetry**: Dependency management.
- **Ward**: Modern test runner for Python.

## 🤝 Contributing

Contributions are welcome! Whether it's adding new tile types, improving the AI architecture, or enhancing the level editor, feel free to fork and submit a PR.


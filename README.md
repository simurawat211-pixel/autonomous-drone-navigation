# 🚁 Drone Navigation AI System

A complete intelligent drone pathfinding system featuring **self-learning A* heuristics**, **reinforcement learning (PPO)**, and **interactive web visualization**.

## 🎯 Project Overview

This system combines three powerful techniques:

### 1. **Self-Learning A* Pathfinding** (`core.py`)
- **Adaptive Safety-Aware Heuristic**: Dynamically learns to avoid obstacles
- Heuristic components:
  - **Distance component**: Euclidean distance to goal
  - **Safety component**: Penalty for proximity to obstacles
  - **Self-learning**: Automatically adapts obstacle avoidance based on environment
- **Weighted A***: Trade-off between optimality and speed via weight parameter

### 2. **Reinforcement Learning with PPO** (`trainer.py`)
- **Policy**: Learns to automatically select optimal A* weight parameters
- **Agent learns to**:
  - Analyze obstacle density and distribution
  - Choose appropriate weight for efficiency
  - Balance path quality with computation speed
- **Training**: Uses Proximal Policy Optimization (PPO) from stable-baselines3

### 3. **Interactive Web Visualization** (`app.py`)
- Built with **Streamlit** for easy interaction
- **Dual modes**:
  - **Manual Mode**: You control A* weight parameter
  - **Auto Mode**: RL agent decides weight automatically
- **Real-time animation** of drone path
- **Environment analysis**: Suggests optimal parameters

## 📁 Project Structure

```
project/
├── core.py                 # A* algorithm + self-learning heuristics
├── environment.py          # Gymnasium environment for training
├── trainer.py              # PPO training and evaluation
├── app.py                  # Streamlit web interface
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### 1. **Installation**

```bash
pip install -r requirements.txt
```

### 2. **Run Interactive Demo**

Test the self-learning heuristic:

```bash
python main.py demo --episodes 5
```

### 3. **Train PPO Agent** (Optional)

Train an agent to optimize weight selection:

```bash
python main.py train --timesteps 100000
```

### 4. **Launch Web Interface**

```bash
python main.py streamlit
```

Opens interactive visualization at `http://localhost:8501`

## 💡 How It Works

### A* Weight Parameter Explained

| Weight | Behavior | Use Case |
|--------|----------|----------|
| **< 1.0** | Conservative, slower, safer paths | Complex obstacles |
| **= 1.0** | Optimal pathfinding (pure A*) | Best quality paths |
| **> 1.0** | Greedy, faster, longer paths | Simple environments |

### Self-Learning Heuristic

```
h(current, goal) = distance_to_goal + safety_penalty

safety_penalty = {
    0,                                    if dist_to_obstacle > 3
    safety_weight / (dist_to_obstacle²)   if dist_to_obstacle ≤ 3
}
```

The algorithm **learns** to:
- Detect obstacles in the immediate vicinity (3×3 neighborhood)
- Apply repulsive force to avoid them
- Adapt penalty based on obstacle proximity

### RL Training Loop

1. **Observation**: Grid map, drone position, goal position
2. **Action**: A* weight parameter (1.0 - 10.0)
3. **Reward**:
   - ✅ +500 for finding a path
   - ✅ -2 × path_length (prefer shorter paths)
   - ✅ -5 per obstacle adjacent to path (prefer safe paths)
   - ❌ -1000 if no path found

## 📊 Usage Examples

### Example 1: Manual A* Mode

```python
from core import weighted_a_star
import numpy as np

# Create grid (0 = free, 1 = obstacle)
grid = np.zeros((30, 30))
grid[10:15, 10:15] = 1  # Obstacle

start = (0, 0)
goal = (29, 29)
weight = 2.0  # You control this

path = weighted_a_star(grid, start, goal, weight)
print(f"Path found: {len(path)} steps")
```

### Example 2: Train and Use RL

```bash
# Train
python main.py train --timesteps 50000

# Evaluate
python main.py evaluate --episodes 10

# Test single episode
python trainer.py --mode test --model-path ./models/ppo_drone_final
```

### Example 3: Web Interface

```bash
python main.py streamlit
```

Then use the sidebar to:
- Adjust grid size and obstacle density
- Toggle between Manual and Auto modes
- Set start/goal positions
- Run pathfinding with visualization

## 🔧 Configuration

### Environment Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `grid_size` | 10-50 | 30 | Grid dimension (square) |
| `obstacle_density` | 0-1 | 0.2 | Fraction of cells with obstacles |
| `safety_weight` | 0-50 | 15.0 | Penalty strength for proximity |

### Training Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `total_timesteps` | 100000 | Training iterations |
| `learning_rate` | 1e-4 | PPO learning rate |
| `batch_size` | 64 | Training batch size |
| `n_epochs` | 20 | PPO training epochs |

## 📈 Performance Metrics

The system tracks:

- **Path Length**: Total distance traveled
- **Path Quality**: Ratio to optimal distance
- **Computation Time**: How fast the path was found
- **Safety Score**: How close to obstacles

Expected results:
- ✅ Obstacle avoidance: 100% (never hits obstacles)
- ✅ Path quality: 80-95% of optimal
- ✅ Speed improvement: 2-5× faster with weight > 2.0

## 🎓 Learning Resources

### Key Concepts

1. **A* Search**: Standard pathfinding algorithm with heuristic
2. **Heuristic Functions**: Guide search toward goal
3. **Weighted A***: Trade-off exploration vs optimality
4. **Gymnasium**: Standard RL environment interface
5. **PPO**: Stable policy gradient RL algorithm

### Files to Study

1. `core.py`: Study `safety_aware_heuristic()` and `weighted_a_star()`
2. `environment.py`: Understand gym.Env interface and rewards
3. `trainer.py`: See how PPO learns to optimize
4. `app.py`: Streamlit visualization patterns

## 🐛 Troubleshooting

### Issue: "No module named 'stable_baselines3'"
**Solution**: `pip install stable-baselines3`

### Issue: "Streamlit not found"
**Solution**: `pip install streamlit streamlit-drawable-canvas`

### Issue: Model training is slow
**Solutions**:
- Reduce `--timesteps` for faster training
- Increase `num_envs` in `trainer.py` for parallel training
- Use GPU: Install PyTorch with CUDA support

### Issue: No path found in some cases
This is expected behavior when obstacles block all paths. The reward becomes -1000 to penalize it.

## 📚 API Reference

### `core.py`

```python
weighted_a_star(grid, start, goal, weight=2.0) -> List[Tuple]
    """Find path using weighted A* with self-learning heuristics"""

safety_aware_heuristic(current, goal, grid, safety_weight=15.0) -> float
    """Compute adaptive heuristic based on obstacles"""

analyze_environment(grid) -> dict
    """Get environment analysis and parameter suggestions"""
```

### `environment.py`

```python
class DroneNavigationEnv(gym.Env):
    """Gymnasium environment for drone navigation"""
    
    def reset() -> Tuple[Dict, Dict]
    def step(action: np.ndarray) -> Tuple[Dict, float, bool, bool, Dict]
    def render()
```

### `trainer.py`

```python
train_ppo(...) -> PPO
    """Train PPO agent on pathfinding"""

evaluate_ppo(model_path, ...) -> Tuple[float, float]
    """Evaluate trained model, returns (mean_reward, std_reward)"""

test_single_episode(model_path, render=True)
    """Test single episode with trained model"""
```

## 🎨 Web Interface Features

### Manual Mode
- 🎮 Slider control for A* weight (1.0-10.0)
- 📍 Set custom start/goal positions
- 🔄 Generate new random grids
- 📊 Real-time performance metrics

### Auto RL Mode
- 🤖 AI chooses optimal weight automatically
- 📊 Shows which weight the model selected
- 💡 Explains why that weight was chosen

### Visualization
- 🎬 Animated path from start to goal
- 📈 Live statistics during navigation
- 🗺️ Grid, obstacles, path, and positions clearly marked

## 🔮 Future Enhancements

- [ ] 3D pathfinding visualization
- [ ] Multi-drone coordination
- [ ] Dynamic obstacle avoidance (moving obstacles)
- [ ] Custom environment upload (draw obstacles)
- [ ] Model comparison (different RL algorithms)
- [ ] Hyperparameter tuning UI

## 📝 License

Open source - feel free to use and modify!

## ✨ Summary

This project demonstrates:
- ✅ **Advanced Algorithm Design**: Self-learning heuristics
- ✅ **RL Integration**: PPO training for optimization
- ✅ **Production Code**: Proper modularization and documentation
- ✅ **User Interface**: Professional web visualization
- ✅ **Complete Pipeline**: From research to deployment

Enjoy exploring intelligent pathfinding! 🚁

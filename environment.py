"""
Gymnasium environment for drone navigation with self-learning A* pathfinding.
Integrates safety-aware heuristics and RL-ready reward structure.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Dict, Tuple, Any
from core import weighted_a_star, safety_aware_heuristic


class DroneNavigationEnv(gym.Env):
    """
    Custom Gymnasium environment for drone navigation.
    
    Action Space: Box(1.0, 10.0) - A* weight parameter
    Observation Space: Dict with grid, drone_pos, goal_pos
    Reward: Path success, length penalty, obstacle proximity penalty
    """
    
    metadata = {"render_modes": ["human"], "render_fps": 10}
    
    def __init__(
        self,
        grid_size: int = 30,
        obstacle_density: float = 0.2,
        render_mode: str = None
    ):
        super(DroneNavigationEnv, self).__init__()
        
        self.grid_size = grid_size
        self.obstacle_density = obstacle_density
        self.render_mode = render_mode
        
        # Action space: A* weight parameter
        self.action_space = spaces.Box(
            low=1.0, high=10.0, shape=(1,), dtype=np.float32
        )
        
        # Observation space
        self.observation_space = spaces.Dict({
            "map": spaces.Box(
                low=0, high=1, shape=(grid_size, grid_size), dtype=np.int8
            ),
            "drone_pos": spaces.Box(
                low=0, high=grid_size-1, shape=(2,), dtype=np.int32
            ),
            "goal_pos": spaces.Box(
                low=0, high=grid_size-1, shape=(2,), dtype=np.int32
            )
        })
        
        self.grid = None
        self.drone_pos = None
        self.goal_pos = None
        self.current_path = []
        
        # For rendering
        self.fig = None
        self.ax = None
        
        self.reset()
    
    def reset(
        self,
        seed: int = None,
        options: dict = None
    ) -> Tuple[Dict, Dict]:
        """Reset environment with new random grid and positions."""
        super().reset(seed=seed)
        
        # Generate random grid with obstacles
        self.grid = np.random.choice(
            [0, 1],
            size=(self.grid_size, self.grid_size),
            p=[1-self.obstacle_density, self.obstacle_density]
        ).astype(np.int8)
        
        # Ensure start and goal are free
        self.grid[0, 0] = 0
        self.grid[self.grid_size-1, self.grid_size-1] = 0
        
        # Set positions
        self.drone_pos = np.array([0, 0], dtype=np.int32)
        self.goal_pos = np.array(
            [self.grid_size - 1, self.grid_size - 1], dtype=np.int32
        )
        
        self.current_path = []
        
        return self._get_obs(), {}
    
    def _get_obs(self) -> Dict[str, np.ndarray]:
        """Get current observation."""
        return {
            "map": self.grid.copy(),
            "drone_pos": self.drone_pos.copy(),
            "goal_pos": self.goal_pos.copy()
        }
    
    def step(self, action: np.ndarray) -> Tuple[Dict, float, bool, bool, Dict]:
        """
        Execute one step of the environment.
        
        Action: A* weight parameter
        Computes path and rewards based on path quality and safety.
        """
        weight = float(action[0])
        
        # Plan path using A* with self-learning heuristic
        path = weighted_a_star(
            self.grid,
            self.drone_pos,
            self.goal_pos,
            weight
        )
        self.current_path = path
        
        # Reward structure
        reward = 0.0
        
        if not path:
            # No path found
            reward = -1000.0
            terminated = True
        else:
            # Path found bonus
            reward += 500.0
            
            # Path length penalty (shorter is better)
            path_length = sum(
                np.sqrt((path[i][0]-path[i-1][0])**2 + (path[i][1]-path[i-1][1])**2)
                for i in range(1, len(path))
            )
            reward -= path_length * 2.0
            
            # Safety penalty: proximity to obstacles
            obstacle_proximity_penalty = 0
            for node in path:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = node[0] + dr, node[1] + dc
                        if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                            if self.grid[nr, nc] == 1:
                                obstacle_proximity_penalty += 5
            
            reward -= obstacle_proximity_penalty
            
            # Update drone position to goal
            self.drone_pos = np.array(path[-1], dtype=np.int32)
            
            # Episode terminates after planning one path
            terminated = True
        
        if self.render_mode == "human":
            self.render()
        
        info = {
            "weight": weight,
            "path_len": len(path) if path else 0,
            "path_length_cost": path_length if path else 0
        }
        
        return self._get_obs(), reward, terminated, False, info
    
    def render(self):
        """Render the current state using matplotlib."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib not available for rendering")
            return
        
        if self.fig is None:
            self.fig, self.ax = plt.subplots(figsize=(8, 8))
            plt.ion()
        
        self.ax.clear()
        
        # Show grid
        self.ax.imshow(self.grid, cmap='Greys', origin='upper')
        
        # Goal
        self.ax.plot(
            self.goal_pos[1], self.goal_pos[0],
            'gs', markersize=12, label='Goal'
        )
        
        # Path
        if self.current_path:
            y_coords, x_coords = zip(*self.current_path)
            self.ax.plot(x_coords, y_coords, 'r-', linewidth=2, label='Path')
        
        # Drone
        self.ax.plot(
            self.drone_pos[1], self.drone_pos[0],
            'b^', markersize=10, label='Drone'
        )
        
        self.ax.legend(loc='upper right')
        self.ax.set_title('Drone Navigation - A* with Self-Learning Heuristic')
        plt.draw()
        plt.pause(0.1)
    
    def close(self):
        """Close the rendering window."""
        try:
            import matplotlib.pyplot as plt
            if self.fig is not None:
                plt.close(self.fig)
        except ImportError:
            pass

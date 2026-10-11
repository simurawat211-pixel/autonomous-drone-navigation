import gymnasium as gym
from gymnasium import spaces
import numpy as np
import heapq

# ---------- Heuristic ----------
def safety_aware_heuristic(current, goal, grid, safety_weight=15.0):
    dist = np.sqrt((current[0]-goal[0])**2 + (current[1]-goal[1])**2)

    r, c = current
    rows, cols = grid.shape
    min_dist = float('inf')

    for dr in range(-3, 4):
        for dc in range(-3, 4):
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr, nc] == 1:
                    d = np.sqrt(dr**2 + dc**2)
                    min_dist = min(min_dist, d)

    repulsion = 0
    if min_dist <= 3:
        repulsion = safety_weight / (min_dist + 0.1)**2

    return dist + repulsion


# ---------- A* ----------
def weighted_a_star(grid, start, goal, weight):
    start, goal = tuple(start), tuple(goal)

    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    closed_set = set()

    directions = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]

    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current in closed_set:
            continue
        
        closed_set.add(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]

        for dr, dc in directions:
            neighbor = (current[0]+dr, current[1]+dc)

            if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
                if grid[neighbor[0], neighbor[1]] == 1 or neighbor in closed_set:
                    continue

                step_cost = np.sqrt(dr**2 + dc**2)
                new_g = g_score[current] + step_cost

                if neighbor not in g_score or new_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = new_g

                    h = safety_aware_heuristic(neighbor, goal, grid)
                    f = new_g + weight*h

                    heapq.heappush(open_set, (f, neighbor))

    return []


# ---------- ENV ----------
class DroneNavigationEnv(gym.Env):
    def __init__(self, grid_size=30, obstacle_density=0.2):
        super().__init__()

        self.grid_size = grid_size
        self.obstacle_density = obstacle_density

        self.action_space = spaces.Box(low=1.0, high=10.0, shape=(1,), dtype=np.float32)

        self.observation_space = spaces.Box(low=0, high=max(grid_size, 10), shape=(4,), dtype=np.float32)

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.grid = np.random.choice(
            [0,1],
            size=(self.grid_size, self.grid_size),
            p=[1-self.obstacle_density, self.obstacle_density]
        )

        self.grid[0,0] = 0
        self.grid[-1,-1] = 0

        self.drone_pos = np.array([0,0])
        self.goal_pos = np.array([self.grid_size-1, self.grid_size-1])

        self.current_path = []

        return self._get_obs(), {}

    def _get_obs(self):
        return np.array([
            self.drone_pos[0], self.drone_pos[1],
            self.goal_pos[0], self.goal_pos[1]
        ], dtype=np.float32)

    def step(self, action):
        weight = float(action[0])

        path = weighted_a_star(self.grid, self.drone_pos, self.goal_pos, weight)
        self.current_path = path

        if not path:
            return self._get_obs(), -1000, True, False, {"path_len": 0}

        reward = 100 - len(path)

        return self._get_obs(), reward, True, False, {"path_len": len(path)}
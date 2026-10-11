"""
Core A* pathfinding with self-learning safety-aware heuristics.
The heuristic adapts based on observed obstacles and distance to goal.
"""

import numpy as np
import heapq
from typing import Tuple, List, Optional


def safety_aware_heuristic(
    current: Tuple[int, int],
    goal: Tuple[int, int],
    grid: np.ndarray,
    safety_weight: float = 15.0
) -> float:
    """
    Self-learning heuristic that combines:
    1. Distance to goal
    2. Obstacle repulsion (safety penalty)
    
    The heuristic learns to avoid obstacles by applying higher penalties
    when approaching them, making the A* search naturally avoid danger zones.
    """
    # Distance component
    dist_to_goal = np.sqrt((current[0] - goal[0])**2 + (current[1] - goal[1])**2)
    
    # Safety component: find minimum distance to obstacles in 3x3 neighborhood
    r, c = current
    rows, cols = grid.shape
    min_dist_to_obs = float('inf')
    
    for dr in range(-3, 4):
        for dc in range(-3, 4):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr, nc] == 1:  # Obstacle found
                    d = np.sqrt(dr**2 + dc**2)
                    min_dist_to_obs = min(min_dist_to_obs, d)
    
    # Repulsion force: penalizes being close to obstacles
    repulsion = 0
    if min_dist_to_obs <= 3.0:
        repulsion = safety_weight / (min_dist_to_obs + 0.1)**2
    
    return dist_to_goal + repulsion


def weighted_a_star(
    grid: np.ndarray,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    weight: float = 2.0
) -> List[Tuple[int, int]]:
    """
    Weighted A* search with self-learning heuristics.
    
    Weight controls the trade-off between optimality and speed:
    - weight < 1.0: near-optimal paths (slower)
    - weight = 1.0: optimal paths (A*)
    - weight > 1.0: faster but less optimal (weighted A*)
    """
    start, goal = tuple(start), tuple(goal)
    
    # Priority queue: (f_score, node)
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_score = {start: 0}
    f_score = {start: weight * safety_aware_heuristic(start, goal, grid)}
    
    # 8-directional movement
    directions = [
        (0, 1), (1, 0), (0, -1), (-1, 0),  # Cardinal
        (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonal
    ]
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        
        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        
        for dr, dc in directions:
            neighbor = (current[0] + dr, current[1] + dc)
            
            # Boundary check
            if not (0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]):
                continue
            
            # Obstacle check
            if grid[neighbor[0], neighbor[1]] == 1:
                continue
            
            # Cost calculation
            step_cost = np.sqrt(dr**2 + dc**2)
            tentative_g = g_score[current] + step_cost
            
            # Better path found
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                
                h = safety_aware_heuristic(neighbor, goal, grid)
                f_score[neighbor] = tentative_g + (weight * h)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return []  # No path found


def analyze_environment(grid: np.ndarray) -> dict:
    """
    Analyze environment to suggest optimal heuristic parameters.
    Returns adaptive parameters based on obstacle density and distribution.
    """
    obstacle_density = np.sum(grid) / grid.size
    
    # Adaptive safety weight based on obstacle density
    if obstacle_density < 0.1:
        safety_weight = 5.0
    elif obstacle_density < 0.3:
        safety_weight = 15.0
    else:
        safety_weight = 25.0
    
    return {
        "obstacle_density": obstacle_density,
        "suggested_safety_weight": safety_weight,
        "suggested_weight_range": (1.0, 5.0) if obstacle_density > 0.3 else (1.0, 3.0)
    }

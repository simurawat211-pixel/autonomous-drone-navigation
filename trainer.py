"""
RL Training module using PPO (Proximal Policy Optimization).
Trains an agent to optimize A* weight parameters for efficient pathfinding.
"""

import numpy as np
import argparse
from typing import Tuple
import os

# PPO from stable-baselines3
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import CheckpointCallback

from environment import DroneNavigationEnv


def create_vectorized_env(
    grid_size: int = 30,
    obstacle_density: float = 0.2,
    num_envs: int = 4
):
    """Create vectorized environment for parallel training."""
    return make_vec_env(
        lambda: DroneNavigationEnv(
            grid_size=grid_size,
            obstacle_density=obstacle_density
        ),
        n_envs=num_envs,
        seed=42
    )


def train_ppo(
    grid_size: int = 30,
    obstacle_density: float = 0.2,
    total_timesteps: int = 100000,
    learning_rate: float = 1e-4,
    batch_size: int = 64,
    n_epochs: int = 20,
    model_save_path: str = "./models",
    checkpoint_interval: int = 10000
) -> PPO:
    """
    Train PPO agent to optimize A* weight parameter selection.
    
    Args:
        grid_size: Size of the grid
        obstacle_density: Density of obstacles (0-1)
        total_timesteps: Total training steps
        learning_rate: PPO learning rate
        batch_size: Training batch size
        n_epochs: Number of training epochs
        model_save_path: Path to save trained models
        checkpoint_interval: Save checkpoint every N timesteps
    
    Returns:
        Trained PPO model
    """
    os.makedirs(model_save_path, exist_ok=True)
    
    # Create vectorized environments
    env = create_vectorized_env(
        grid_size=grid_size,
        obstacle_density=obstacle_density,
        num_envs=4
    )
    
    # Checkpoint callback
    checkpoint_callback = CheckpointCallback(
        save_freq=checkpoint_interval,
        save_path=model_save_path,
        name_prefix="ppo_drone"
    )
    
    # Create PPO model
    model = PPO(
        policy="MultiInputPolicy",  # For Dict observation space
        env=env,
        learning_rate=learning_rate,
        batch_size=batch_size,
        n_epochs=n_epochs,
        n_steps=2048,
        clip_range=0.2,
        verbose=1
    )
    
    print(f"Starting training for {total_timesteps} timesteps...")
    print(f"Grid Size: {grid_size}, Obstacle Density: {obstacle_density}")
    
    # Train
    model.learn(
        total_timesteps=total_timesteps,
        callback=checkpoint_callback,
        progress_bar=True
    )
    
    # Save final model
    final_path = os.path.join(model_save_path, "ppo_drone_final")
    model.save(final_path)
    print(f"\nTraining complete! Model saved to {final_path}")
    
    env.close()
    return model


def evaluate_ppo(
    model_path: str,
    grid_size: int = 30,
    num_episodes: int = 10
) -> Tuple[float, float]:
    """
    Evaluate trained PPO model.
    
    Args:
        model_path: Path to trained model
        grid_size: Size of evaluation grid
        num_episodes: Number of episodes to evaluate
    
    Returns:
        Tuple of (mean_reward, std_reward)
    """
    # Load model
    model = PPO.load(model_path)
    
    # Create evaluation environment
    env = DroneNavigationEnv(grid_size=grid_size, obstacle_density=0.2)
    
    rewards = []
    for episode in range(num_episodes):
        obs, info = env.reset()
        
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        
        rewards.append(reward)
        print(f"Episode {episode+1}: Reward = {reward:.2f}, Path Length = {info['path_len']}")
    
    env.close()
    
    mean_reward = np.mean(rewards)
    std_reward = np.std(rewards)
    
    print(f"\nEvaluation Results:")
    print(f"Mean Reward: {mean_reward:.2f} ± {std_reward:.2f}")
    
    return mean_reward, std_reward


def test_single_episode(model_path: str, render: bool = True):
    """Test a single episode with trained model and optional rendering."""
    model = PPO.load(model_path)
    env = DroneNavigationEnv(
        grid_size=30,
        obstacle_density=0.2,
        render_mode="human" if render else None
    )
    
    obs, info = env.reset()
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    
    print(f"Action (A* weight): {action[0]:.2f}")
    print(f"Reward: {reward:.2f}")
    print(f"Path Length: {info['path_len']}")
    
    if render:
        import matplotlib.pyplot as plt
        plt.show()
    
    env.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train or evaluate PPO agent for drone navigation"
    )
    parser.add_argument(
        "--mode",
        choices=["train", "evaluate", "test"],
        default="train",
        help="Mode: train, evaluate, or test"
    )
    parser.add_argument("--grid-size", type=int, default=30, help="Grid size")
    parser.add_argument("--obstacle-density", type=float, default=0.2, help="Obstacle density")
    parser.add_argument("--timesteps", type=int, default=100000, help="Training timesteps")
    parser.add_argument("--model-path", type=str, default="./models/ppo_drone_final", help="Model path")
    parser.add_argument("--episodes", type=int, default=10, help="Evaluation episodes")
    parser.add_argument("--no-render", action="store_true", help="Disable rendering")
    
    args = parser.parse_args()
    
    if args.mode == "train":
        train_ppo(
            grid_size=args.grid_size,
            obstacle_density=args.obstacle_density,
            total_timesteps=args.timesteps
        )
    
    elif args.mode == "evaluate":
        evaluate_ppo(
            model_path=args.model_path,
            grid_size=args.grid_size,
            num_episodes=args.episodes
        )
    
    elif args.mode == "test":
        test_single_episode(
            model_path=args.model_path,
            render=not args.no_render
        )

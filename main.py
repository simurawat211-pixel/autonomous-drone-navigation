"""
Main entry point for Drone Navigation AI System.
Provides CLI interface for training, testing, and running the complete system.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from environment import DroneNavigationEnv
from core import weighted_a_star, analyze_environment
from trainer import train_ppo, evaluate_ppo, test_single_episode
import numpy as np


def run_demo(
    grid_size: int = 30,
    obstacle_density: float = 0.2,
    num_episodes: int = 5,
    render: bool = True
):
    """Run demo of A* pathfinding with self-learning heuristics."""
    print("=" * 70)
    print("🚁 DRONE NAVIGATION - A* SELF-LEARNING HEURISTIC DEMO")
    print("=" * 70)
    
    env = DroneNavigationEnv(
        grid_size=grid_size,
        obstacle_density=obstacle_density,
        render_mode="human" if render else None
    )
    
    weights_to_test = [1.0, 2.0, 5.0, 10.0]
    
    for episode in range(num_episodes):
        obs, info = env.reset()
        grid = obs["map"]
        
        print(f"\n📍 Episode {episode+1}/{num_episodes}")
        print(f"Grid: {grid_size}x{grid_size}, Obstacles: {np.sum(grid)} cells")
        
        # Analyze environment
        analysis = analyze_environment(grid)
        print(f"Environment Analysis:")
        print(f"  - Obstacle Density: {analysis['obstacle_density']:.1%}")
        print(f"  - Suggested Safety Weight: {analysis['suggested_safety_weight']:.1f}")
        print(f"  - Recommended Weight Range: {analysis['suggested_weight_range']}")
        
        print(f"\nTesting different weights:")
        best_weight = None
        best_reward = float('-inf')
        
        for weight in weights_to_test:
            obs_copy = obs.copy()
            obs_copy["drone_pos"] = obs_copy["drone_pos"].copy()
            obs_copy["goal_pos"] = obs_copy["goal_pos"].copy()
            
            action = np.array([weight], dtype=np.float32)
            obs_result, reward, terminated, truncated, info_step = env.step(action)
            
            print(f"  Weight {weight:5.1f}: Reward = {reward:8.1f}, Path Length = {info_step['path_len']:3d}")
            
            if reward > best_reward:
                best_reward = reward
                best_weight = weight
        
        print(f"\n✅ Best Weight: {best_weight:.1f} (Reward: {best_reward:.1f})")
    
    env.close()
    print("\n" + "=" * 70)


def run_training(
    grid_size: int = 30,
    obstacle_density: float = 0.2,
    timesteps: int = 100000,
    learning_rate: float = 1e-4
):
    """Run PPO training."""
    print("=" * 70)
    print("🤖 TRAINING PPO AGENT FOR OPTIMAL WEIGHT SELECTION")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  - Grid Size: {grid_size}")
    print(f"  - Obstacle Density: {obstacle_density}")
    print(f"  - Total Timesteps: {timesteps}")
    print(f"  - Learning Rate: {learning_rate}")
    print("=" * 70)
    
    model = train_ppo(
        grid_size=grid_size,
        obstacle_density=obstacle_density,
        total_timesteps=timesteps,
        learning_rate=learning_rate,
        model_save_path="./models"
    )
    
    print("\n✅ Training complete!")
    return model


def run_evaluation(model_path: str = "./models/ppo_drone_final", num_episodes: int = 10):
    """Evaluate trained model."""
    print("=" * 70)
    print("📊 EVALUATING TRAINED PPO MODEL")
    print("=" * 70)
    print(f"Model: {model_path}")
    print(f"Episodes: {num_episodes}")
    print("=" * 70)
    
    mean_reward, std_reward = evaluate_ppo(
        model_path=model_path,
        num_episodes=num_episodes
    )
    
    print("\n✅ Evaluation complete!")


def run_streamlit():
    """Launch Streamlit web interface."""
    print("=" * 70)
    print("🌐 LAUNCHING STREAMLIT WEB INTERFACE")
    print("=" * 70)
    print("Opening browser at: http://localhost:8501")
    print("=" * 70)
    
    import subprocess
    import webbrowser
    import time
    
    # Start streamlit
    process = subprocess.Popen(
        ["streamlit", "run", str(PROJECT_ROOT / "app.py")]
    )
    
    # Give it time to start
    time.sleep(3)
    
    # Open browser
    try:
        webbrowser.open("http://localhost:8501")
    except Exception as e:
        print(f"Could not open browser: {e}")
    
    print("\nStreamlit is running. Press Ctrl+C to stop.")
    
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        print("\nStreamlit stopped.")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="🚁 Drone Navigation AI System - A* with Self-Learning Heuristics & RL/PPO",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run demo
  python main.py demo --episodes 5
  
  # Train PPO agent
  python main.py train --timesteps 100000
  
  # Evaluate trained model
  python main.py evaluate --episodes 10
  
  # Launch web interface
  python main.py streamlit
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run A* pathfinding demo")
    demo_parser.add_argument("--grid-size", type=int, default=30, help="Grid size")
    demo_parser.add_argument("--density", type=float, default=0.2, help="Obstacle density")
    demo_parser.add_argument("--episodes", type=int, default=5, help="Number of episodes")
    demo_parser.add_argument("--no-render", action="store_true", help="Disable rendering")
    
    # Train command
    train_parser = subparsers.add_parser("train", help="Train PPO agent")
    train_parser.add_argument("--grid-size", type=int, default=30, help="Grid size")
    train_parser.add_argument("--density", type=float, default=0.2, help="Obstacle density")
    train_parser.add_argument("--timesteps", type=int, default=100000, help="Training timesteps")
    train_parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate trained model")
    eval_parser.add_argument("--model", type=str, default="./models/ppo_drone_final", help="Model path")
    eval_parser.add_argument("--episodes", type=int, default=10, help="Evaluation episodes")
    
    # Streamlit command
    subparsers.add_parser("streamlit", help="Launch web interface")
    
    args = parser.parse_args()
    
    if args.command == "demo":
        run_demo(
            grid_size=args.grid_size,
            obstacle_density=args.density,
            num_episodes=args.episodes,
            render=not args.no_render
        )
    
    elif args.command == "train":
        run_training(
            grid_size=args.grid_size,
            obstacle_density=args.density,
            timesteps=args.timesteps,
            learning_rate=args.lr
        )
    
    elif args.command == "evaluate":
        run_evaluation(
            model_path=args.model,
            num_episodes=args.episodes
        )
    
    elif args.command == "streamlit":
        run_streamlit()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

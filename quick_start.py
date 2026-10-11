#!/usr/bin/env python3
"""
🚁 QUICK START GUIDE FOR DRONE AI NAVIGATION SYSTEM
=====================================================

This script helps you get started quickly with the system.
Run: python quick_start.py
"""

import sys
from pathlib import Path

def print_banner():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║      🚁 DRONE NAVIGATION AI SYSTEM - QUICK START          ║
    ║                                                           ║
    ║  Self-Learning A* + RL/PPO + Streamlit Visualization    ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

def print_menu():
    print("\n📋 WHAT WOULD YOU LIKE TO DO?\n")
    print("  1️⃣  View Project Overview")
    print("  2️⃣  Install Dependencies")
    print("  3️⃣  Run A* Pathfinding Demo")
    print("  4️⃣  Launch Web Interface (Streamlit)")
    print("  5️⃣  Train RL Agent (PPO)")
    print("  6️⃣  Evaluate Trained Model")
    print("  7️⃣  View All Commands")
    print("  8️⃣  Exit")
    print()

def show_overview():
    overview = """
╔═══════════════════════════════════════════════════════════════╗
║              PROJECT ARCHITECTURE OVERVIEW                   ║
╚═══════════════════════════════════════════════════════════════╝

📦 THREE MAIN COMPONENTS:

1. 🧠 SELF-LEARNING A* PATHFINDING (core.py)
   ├─ Standard A* algorithm
   ├─ Safety-aware heuristic (learns obstacle avoidance)
   ├─ Weighted A* for speed/quality trade-off
   └─ Adaptive parameters based on environment

2. 🤖 REINFORCEMENT LEARNING WITH PPO (trainer.py)
   ├─ Trains agent to select optimal A* weights
   ├─ Learns from environment analysis
   ├─ Balances path quality with speed
   └─ Uses Proximal Policy Optimization

3. 🌐 WEB INTERFACE (app.py - Streamlit)
   ├─ Manual mode: You control A* weight
   ├─ Auto mode: RL agent decides weight
   ├─ Real-time visualization & animation
   └─ Environment analysis & statistics

🔗 INTEGRATION:
   main.py → core.py + environment.py + trainer.py + app.py
   
   Each module is independent but works together seamlessly!

🎯 KEY FEATURES:
   ✅ Automatic obstacle detection & avoidance
   ✅ Self-adapting heuristic based on grid environment
   ✅ RL optimization of weight parameter
   ✅ Beautiful interactive web interface
   ✅ Complete documentation & examples
   ✅ Production-ready code structure
"""
    print(overview)

def show_commands():
    commands = """
╔═══════════════════════════════════════════════════════════════╗
║                    ALL AVAILABLE COMMANDS                    ║
╚═══════════════════════════════════════════════════════════════╝

🚀 USING main.py:
   python main.py demo
      Run A* pathfinding demonstration (5 episodes)
   
   python main.py demo --episodes 10
      Run 10 demo episodes
   
   python main.py demo --grid-size 50 --density 0.3
      Custom grid size and obstacle density
   
   python main.py train
      Train PPO agent (100k timesteps)
   
   python main.py train --timesteps 200000
      Custom training length
   
   python main.py evaluate
      Evaluate trained model (10 episodes)
   
   python main.py streamlit
      Launch interactive web interface

🐍 DIRECT PYTHON USAGE:
   
   # A* Pathfinding Example
   from core import weighted_a_star
   import numpy as np
   
   grid = np.zeros((30, 30))
   path = weighted_a_star(grid, (0,0), (29,29), weight=2.0)
   
   # Environment Testing
   from environment import DroneNavigationEnv
   env = DroneNavigationEnv(grid_size=30, obstacle_density=0.2)
   obs, info = env.reset()
   obs, reward, done, _, info = env.step([2.0])
   
   # Model Training
   from trainer import train_ppo
   model = train_ppo(total_timesteps=50000)

📊 VIEW HELP:
   python main.py --help
   python trainer.py --help
"""
    print(commands)

def install_deps():
    import subprocess
    print("\n📦 Installing dependencies from requirements.txt...\n")
    print("Running: pip install -r requirements.txt\n")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("\n✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed: {e}")
        print("\n🔧 Manual installation:")
        print("   pip install -r requirements.txt")

def run_demo():
    import subprocess
    print("\n🎮 Starting A* Pathfinding Demo...\n")
    print("This will run 5 episodes showing the self-learning heuristic.\n")
    
    try:
        subprocess.run([sys.executable, "main.py", "demo", "--episodes", "5"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Demo failed: {e}")
        print("\nMake sure all dependencies are installed: pip install -r requirements.txt")

def run_streamlit():
    import subprocess
    import time
    import webbrowser
    
    print("\n🌐 Launching Streamlit Web Interface...\n")
    print("Starting server at http://localhost:8501\n")
    print("Press Ctrl+C to stop the server.\n")
    
    try:
        process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"])
        time.sleep(3)
        
        try:
            webbrowser.open("http://localhost:8501")
            print("✅ Browser opened!")
        except:
            print("⚠️  Please open http://localhost:8501 in your browser")
        
        process.wait()
    except KeyboardInterrupt:
        print("\n\n✅ Streamlit stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nManual start:")
        print("   streamlit run app.py")

def run_training():
    import subprocess
    print("\n🤖 Starting PPO Training...\n")
    print("This trains the RL agent to optimize A* weight selection.")
    print("Model will be saved to ./models/\n")
    
    timesteps = input("How many timesteps? (default: 100000): ").strip()
    if not timesteps:
        timesteps = "100000"
    
    try:
        subprocess.run([sys.executable, "main.py", "train", "--timesteps", timesteps], 
                      check=True)
        print("\n✅ Training complete! Model saved.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Training failed: {e}")

def run_evaluation():
    import subprocess
    print("\n📊 Evaluating Trained Model...\n")
    print("This tests the trained RL agent.\n")
    
    episodes = input("How many episodes? (default: 10): ").strip()
    if not episodes:
        episodes = "10"
    
    try:
        subprocess.run([sys.executable, "main.py", "evaluate", "--episodes", episodes], 
                      check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Evaluation failed: {e}")

def main():
    print_banner()
    
    while True:
        print_menu()
        choice = input("👉 Enter your choice (1-8): ").strip()
        
        if choice == "1":
            show_overview()
        elif choice == "2":
            install_deps()
        elif choice == "3":
            run_demo()
        elif choice == "4":
            run_streamlit()
        elif choice == "5":
            run_training()
        elif choice == "6":
            run_evaluation()
        elif choice == "7":
            show_commands()
        elif choice == "8":
            print("\n👋 Goodbye! Happy pathfinding! 🚁\n")
            break
        else:
            print("\n⚠️  Invalid choice. Please enter 1-8.\n")

if __name__ == "__main__":
    main()

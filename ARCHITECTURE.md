# 🏗️ System Architecture Diagrams

## System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│           🚁 DRONE NAVIGATION AI SYSTEM - COMPLETE ARCHITECTURE          │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘


                            ┌─────────────────────────┐
                            │   USER INTERACTION      │
                            │   - CLI (main.py)       │
                            │   - Web UI (Streamlit)  │
                            └────────────┬────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
              ┌─────▼──────┐      ┌──────▼──────┐      ┌─────▼──────┐
              │   Demo      │      │  Training   │      │ Evaluation │
              │  (CLI)      │      │  (RL/PPO)   │      │  (Metrics) │
              └─────┬──────┘      └──────┬──────┘      └─────┬──────┘
                    │                    │                    │
                    └────────────────────┼────────────────────┘
                                         │
                         ┌───────────────▼────────────────┐
                         │   Environment Integration      │
                         │  (environment.py)              │
                         │  - State: grid, drone, goal    │
                         │  - Actions: A* weight          │
                         │  - Rewards: path quality       │
                         └───────────────┬────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
              ┌─────▼──────┐      ┌──────▼──────┐      ┌─────▼──────┐
              │  Core A*    │      │    RL/PPO   │      │ Streamlit  │
              │ Algorithm   │      │   Training  │      │    Web UI  │
              │(core.py)    │      │(trainer.py) │      │ (app.py)   │
              │             │      │             │      │            │
              │ • Weighted  │      │ • PPO Agent │      │ • Manual   │
              │   A*        │      │ • Training  │      │   Mode     │
              │ • Heuristic │      │   Loop      │      │ • Auto RL  │
              │ • Obstacle  │      │ • Callbacks │      │   Mode     │
              │   Avoidance │      │ • Model     │      │ • Animation│
              └─────┬──────┘      │   Save      │      └─────┬──────┘
                    │              └──────┬──────┘            │
                    │                     │                   │
                    └─────────────────────┼───────────────────┘
                                          │
                          ┌───────────────▼────────────────┐
                          │      Output & Results          │
                          │  - Path visualization          │
                          │  - Performance metrics         │
                          │  - Environment analysis        │
                          └────────────────────────────────┘
```

---

## Data Flow Diagram

```
┌──────────────────────────────────────┐
│        USER REQUEST                  │
│  (demo / train / evaluate / streamlit)│
└────────────────┬─────────────────────┘
                 │
        ┌────────▼─────────┐
        │    main.py       │
        │ (Route Command)  │
        └────────┬─────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
  ┌──▼──┐   ┌───▼──┐   ┌───▼────┐
  │DEMO │   │TRAIN │   │STREAMLIT│
  └──┬──┘   └───┬──┘   └───┬────┘
     │          │          │
     │       ┌──▼──────────┐│
     │       │environment.py││
     │       │Create Env(s) ││
     │       └──┬────────┬──┘│
     │          │        │   │
 ┌───▼──────────▼──┐ ┌──▼───▼─────────┐
 │   core.py       │ │  trainer.py    │
 │  weighted_a_star│ │  train_ppo()   │
 │  heuristic()    │ │  evaluate_ppo()│
 └───┬─────────────┘ └──┬──────┬──────┘
     │                  │      │
  ┌──▼──────────────────┴──────▼──┐
  │ Get Path & Metrics            │
  │ - path: List[tuple]           │
  │ - reward: float               │
  │ - path_length: int            │
  └──┬──────────────────────────┬─┘
     │                          │
  ┌──▼──────┐          ┌────────▼──────┐
  │CLI/Plot │          │app.py         │
  │Display  │          │Streamlit App  │
  │(matplotlib)        │Visualization  │
  └──────┬──┘          └─────┬────────┘
         │                   │
         └───────────┬───────┘
                     │
               ┌─────▼──────┐
               │   Output   │
               │ Animated   │
               │   Path &   │
               │ Metrics    │
               └────────────┘
```

---

## Component Integration

```
                          INPUT LAYER
                     ┌────────────────┐
                     │  User Controls │
                     │ - Weight param │
                     │ - Grid size    │
                     │ - Start/Goal   │
                     └────────┬───────┘
                              │
                ┌─────────────┴──────────────┐
                │                            │
        ┌───────▼──────────┐      ┌──────────▼────────┐
        │  CORE MODULE     │      │  RL MODULE       │
        │  (core.py)       │      │  (trainer.py)    │
        │                  │      │                  │
        │ weighted_a_star()├──────┤← predict_weight()│
        │      ▲           │      │                  │
        │      │           │      │  PPO Model      │
        │      │           │      │  (Learned)      │
        │ heuristic()      │      └──────────────────┘
        │      │           │
        │      │input      │
        │      │from       │
        └──────┼───────────┘
               │
        ┌──────▼──────────────────┐
        │ ENVIRONMENT MODULE       │
        │ (environment.py)         │
        │                          │
        │ - Generate Grid          │
        │ - Set Positions          │
        │ - Calculate Rewards      │
        │ - Observations           │
        └──────┬───────────────────┘
               │
        ┌──────▼──────────────────┐
        │ VISUALIZATION MODULE     │
        │ (app.py)                 │
        │                          │
        │ - Streamlit Interface    │
        │ - Animation              │
        │ - Statistics             │
        └──────────────────────────┘
```

---

## Execution Flow (Demo Mode)

```
START: python main.py demo
  │
  ├─ Create environment
  │  (grid_size=30, obstacle_density=0.2)
  │
  ├─ For each episode (1 to N):
  │
  │  ├─ Reset environment
  │  │  └─ Generate random grid
  │  │  └─ Set drone at (0, 0)
  │  │  └─ Set goal at (29, 29)
  │  │
  │  ├─ Analyze environment
  │  │  └─ Check obstacle density
  │  │  └─ Calculate safe weight range
  │  │
  │  ├─ Test different weights [1.0, 2.0, 5.0, 10.0]
  │  │
  │  │  For each weight:
  │  │  ├─ Call weighted_a_star(grid, start, goal, weight)
  │  │  │
  │  │  │  ├─ For each node in search:
  │  │  │  │  └─ Evaluate: g_score + weight × heuristic()
  │  │  │  │     └─ heuristic = dist_to_goal + obstacle_penalty
  │  │  │  │
  │  │  │  └─ Return path when goal reached
  │  │  │
  │  │  ├─ Calculate reward
  │  │  │  ├─ +500 if path found
  │  │  │  ├─ -2 × path_length
  │  │  │  ├─ -5 × adjacent obstacles
  │  │  │  └─ -1000 if no path
  │  │  │
  │  │  └─ Display: Weight | Reward | Path Length
  │  │
  │  └─ Report best weight for this episode
  │
  ├─ Close environment
  │
  └─ END: Show summary statistics
```

---

## Training Flow (RL Mode)

```
START: python main.py train
  │
  ├─ Create 4 vectorized environments (parallel)
  │
  ├─ Initialize PPO model
  │  ├─ Policy: MultiInputPolicy (handles Dict observations)
  │  ├─ Learning rate: 1e-4
  │  ├─ Batch size: 64
  │  └─ Epochs per update: 20
  │
  ├─ Training loop (100,000 timesteps):
  │
  │  Repeat:
  │  ├─ Step 1: Sample experiences from environments
  │  │  └─ For 4 parallel envs:
  │  │     ├─ Get observation (grid, drone_pos, goal_pos)
  │  │     ├─ Model predicts action (weight parameter)
  │  │     ├─ Environment executes A* with this weight
  │  │     ├─ Get reward + new observation
  │  │     └─ Store in buffer
  │  │
  │  ├─ Step 2: Update policy (every 2048 steps)
  │  │  ├─ Compute advantages
  │  │  ├─ Update policy network (20 epochs)
  │  │  ├─ Update value network
  │  │  └─ Clip gradients
  │  │
  │  └─ Step 3: Check checkpoint (every 10,000 steps)
  │     └─ Save model copy
  │
  ├─ Monitor metrics:
  │  ├─ Average reward (increasing = learning!)
  │  ├─ Policy loss (decreasing = improving)
  │  └─ Entropy (staying moderate = exploring)
  │
  └─ Save final model to ./models/ppo_drone_final
```

---

## Web Interface Flow (Streamlit)

```
User opens http://localhost:8501
  │
  ├─ Load page
  │  ├─ Initialize session state
  │  │  ├─ grid_size, obstacle_density
  │  │  ├─ drone_pos, goal_pos
  │  │  └─ model (if RL mode)
  │  │
  │  └─ Render UI:
  │     ├─ Sidebar controls
  │     │  ├─ Grid size slider
  │     │  ├─ Obstacle density slider
  │     │  ├─ Mode selection (Manual / Auto RL)
  │     │  ├─ Weight slider (if Manual)
  │     │  ├─ Animation speed
  │     │  └─ Run button
  │     │
  │     └─ Main area
  │        ├─ Environment analysis
  │        └─ Visualization area (empty initially)
  │
  ├─ User adjusts settings & clicks "Run"
  │
  ├─ On Run:
  │  ├─ Generate/load grid
  │  │
  │  ├─ Determine weight:
  │  │  ├─ Manual mode: Use slider value
  │  │  └─ Auto mode: Load model → predict → get weight
  │  │
  │  ├─ Call weighted_a_star(grid, start, goal, weight)
  │  │
  │  ├─ Get path from core.py
  │  │
  │  ├─ Animate path:
  │  │  └─ For each step in path:
  │  │     ├─ Draw grid + obstacles
  │  │     ├─ Draw path so far (cyan)
  │  │     ├─ Draw current position (red)
  │  │     ├─ Draw goal (lime)
  │  │     ├─ Display step count
  │  │     └─ Sleep for animation_speed
  │  │
  │  └─ Display metrics:
  │     ├─ Path length
  │     ├─ Number of steps
  │     ├─ Weight used
  │     └─ Quality score
  │
  └─ User can adjust & run again!
```

---

## File Dependency Graph

```
                    ┌──────────────┐
                    │  main.py     │
                    │  (Entry)     │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┬─────────────┐
        │                  │                  │             │
    ┌───▼────────┐  ┌───────▼──────┐  ┌──────▼───┐  ┌────▼──────┐
    │ core.py    │  │trainer.py    │  │app.py    │  │README.md  │
    │            │  │              │  │          │  │           │
    │ • NO DEPS  │  │  ├─core.py   │  │├─core.py │  │(doc only) │
    │            │  │  ├─environ.py│  ││         │  │           │
    │ IMPORTS:   │  │  ├─stable-b3 │  ││         │  │           │
    │ • numpy    │  │  └─argparse  │  │└─argparse│  │           │
    │ • heapq    │  │              │  │          │  │           │
    │            │  └──────┬───────┘  └──────┬───┘  │           │
    │            │         │                 │      │           │
    │            │    ┌────▼──────────────┐  │      │           │
    │            │    │environment.py     │  │      │           │
    │            │    │                   │  │      │           │
    │            │    │├─core.py          │  │      │           │
    │            │    │├─gymnasium        │  │      │           │
    │            │    │└─numpy            │  │      │           │
    │            │    │                   │  │      │           │
    │            └────┴──────────────┬────┘  │      │           │
    │                               │       │      │           │
    └───────────────────────────────┼───────┘      │           │
                                    │              │           │
                          ┌─────────▼──────────────▼───────────┘
                          │
                    DEPENDENCIES:
                    • numpy
                    • gymnasium
                    • matplotlib
                    • stable-baselines3
                    • streamlit
                    • torch
```

---

## Module Interaction Matrix

```
        │ core.py │ env.py │ train.py │ app.py │ main.py
────────┼─────────┼────────┼──────────┼────────┼─────────
core.py │    -    │   →    │    →     │   →    │   →
        │         │        │          │        │
env.py  │   ←     │    -   │    →     │   ←    │   ←
        │         │        │          │        │
train.py│   ←     │   ←    │    -     │        │   ←
        │         │        │          │        │
app.py  │   ←     │   ←    │          │    -   │   ←
        │         │        │          │        │
main.py │   ←     │   ←    │    ←     │   ←    │    -

Legend: → (uses/imports) ← (used by) - (same file)

Reading: env.py imports core.py (core → env)
         main.py imports everything (all → main)
         No circular dependencies ✓
```

---

## State Diagram (Environment)

```
    ┌─────────────────────┐
    │   NOT INITIALIZED   │
    │                     │
    │ • grid: None        │
    │ • drone_pos: None   │
    │ • goal_pos: None    │
    └──────────┬──────────┘
               │
               │ reset()
               │
    ┌──────────▼──────────┐
    │ READY               │
    │                     │
    │ • grid: Generated   │
    │ • drone_pos: (0,0)  │
    │ • goal_pos: (end)   │
    └──────────┬──────────┘
               │
               │ step(action)
               │
    ┌──────────▼──────────┐
    │ PLANNING            │
    │                     │
    │ • Running A*        │
    │ • Computing reward  │
    │ • Updating position │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │ DONE                │
    │                     │
    │ • Path found        │
    │ • Metrics computed  │
    │ • Ready for new     │
    │   episode           │
    └──────────┬──────────┘
               │
               │ reset()
               │
               └─────────────┐
                             │
                    ┌────────▼──────────┐
                    │    READY (again)  │
                    └───────────────────┘
```

---

This completes the system architecture documentation! 🎉

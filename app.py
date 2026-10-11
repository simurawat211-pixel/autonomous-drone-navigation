"""
Interactive Streamlit visualization for drone navigation system.
Supports both manual A* weight control and RL-based autonomous pathfinding.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import time
from pathlib import Path

from environment import DroneNavigationEnv
from core import weighted_a_star, analyze_environment

# Try to import stable-baselines3
try:
    from stable_baselines3 import PPO
    HAS_PPO = True
except ImportError:
    HAS_PPO = False


# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="🚁 Drone AI Navigation",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚁 Intelligent Drone Navigation System")
st.markdown("""
**Self-Learning A* Pathfinding with RL & PPO**
- 🧠 Adaptive heuristics based on obstacles
- 🤖 RL training to optimize pathfinding
- 📊 Real-time visualization
""")


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if "grid_size" not in st.session_state:
    st.session_state.grid_size = 30

if "obstacle_density" not in st.session_state:
    st.session_state.obstacle_density = 0.2

if "grid" not in st.session_state:
    st.session_state.grid = None

if "drone_pos" not in st.session_state:
    st.session_state.drone_pos = (0, 0)

if "goal_pos" not in st.session_state:
    st.session_state.goal_pos = (29, 29)

if "model" not in st.session_state:
    st.session_state.model = None

if "model_loaded" not in st.session_state:
    st.session_state.model_loaded = False


# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Grid settings
    st.subheader("🗺️ Grid Settings")
    grid_size = st.slider("Grid Size", 10, 50, 30, step=5)
    obstacle_density = st.slider("Obstacle Density", 0.0, 0.5, 0.2, step=0.05)
    
    if grid_size != st.session_state.grid_size or obstacle_density != st.session_state.obstacle_density:
        st.session_state.grid_size = grid_size
        st.session_state.obstacle_density = obstacle_density
        st.session_state.grid = None
    
    st.divider()
    
    # Mode selection
    st.subheader("🎮 Navigation Mode")
    mode = st.radio(
        "Select Mode",
        ["Manual A*", "Auto RL"],
        help="Manual: You control A* weight | Auto RL: AI decides weight"
    )
    
    # Manual mode controls
    if mode == "Manual A*":
        weight = st.slider(
            "A* Weight (Lower=Optimal, Higher=Faster)",
            1.0, 10.0, 2.0, 0.1,
            help="Weight > 1: faster but suboptimal | Weight = 1: optimal"
        )
        use_weight = weight
    else:
        use_weight = None
        if HAS_PPO:
            st.info("🤖 Using RL model to decide A* weight automatically")
        else:
            st.warning("⚠️ stable-baselines3 not installed. Using fallback mode.")
    
    st.divider()
    
    # Position controls
    st.subheader("📍 Positions")
    col1, col2 = st.columns(2)
    with col1:
        start_row = st.number_input("Start Row", 0, grid_size-1, 0)
    with col2:
        start_col = st.number_input("Start Col", 0, grid_size-1, 0)
    
    col1, col2 = st.columns(2)
    with col1:
        goal_row = st.number_input("Goal Row", 0, grid_size-1, grid_size-1)
    with col2:
        goal_col = st.number_input("Goal Col", 0, grid_size-1, grid_size-1)
    
    st.session_state.drone_pos = (start_row, start_col)
    st.session_state.goal_pos = (goal_row, goal_col)
    
    st.divider()
    
    # Visualization settings
    st.subheader("📊 Visualization")
    animation_speed = st.slider("Animation Speed", 0.01, 0.5, 0.05)
    show_stats = st.checkbox("Show Statistics", value=True)
    
    st.divider()
    
    # Action buttons
    st.subheader("🚀 Actions")
    col1, col2 = st.columns(2)
    with col1:
        generate_new_grid = st.button("🔄 New Grid")
    with col2:
        run_pathfinding = st.button("▶️ Run Pathfinding", type="primary")


# ============================================================================
# MAIN CONTENT
# ============================================================================

# Generate/reset grid if needed
if generate_new_grid or st.session_state.grid is None:
    env = DroneNavigationEnv(
        grid_size=st.session_state.grid_size,
        obstacle_density=st.session_state.obstacle_density
    )
    obs, _ = env.reset()
    st.session_state.grid = obs["map"]
    st.rerun()

grid = st.session_state.grid

# Display environment analysis
if show_stats:
    with st.expander("📊 Environment Analysis", expanded=True):
        analysis = analyze_environment(grid)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Obstacle Density",
                f"{analysis['obstacle_density']:.1%}"
            )
        with col2:
            st.metric(
                "Suggested Safety Weight",
                f"{analysis['suggested_safety_weight']:.1f}"
            )
        with col3:
            st.metric(
                "Recommended Weight Range",
                f"{analysis['suggested_weight_range'][0]:.1f} - {analysis['suggested_weight_range'][1]:.1f}"
            )

st.divider()

# Main visualization area
if run_pathfinding:
    col_viz, col_info = st.columns([3, 1])
    
    with col_viz:
        st.subheader("🗺️ Pathfinding Visualization")
        
        # Determine weight to use
        if mode == "Manual A*":
            final_weight = use_weight
            weight_source = f"Manual ({use_weight:.2f})"
        else:
            # Use RL model or fallback
            if HAS_PPO and st.session_state.model_loaded:
                try:
                    obs = {
                        "map": grid.copy(),
                        "drone_pos": np.array(st.session_state.drone_pos, dtype=np.int32),
                        "goal_pos": np.array(st.session_state.goal_pos, dtype=np.int32)
                    }
                    action, _ = st.session_state.model.predict(obs, deterministic=True)
                    final_weight = float(action[0])
                    weight_source = f"RL Model ({final_weight:.2f})"
                except Exception as e:
                    st.warning(f"RL prediction failed: {e}. Using default weight.")
                    final_weight = 2.0
                    weight_source = "Default (2.0)"
            else:
                final_weight = 2.0
                weight_source = "Default (2.0)"
        
        # Compute path
        path = weighted_a_star(
            grid,
            st.session_state.drone_pos,
            st.session_state.goal_pos,
            final_weight
        )
        
        # Animation
        if path:
            placeholder = st.empty()
            
            for step in range(len(path)):
                fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
                
                # Grid background
                ax.imshow(grid, cmap='Greys', alpha=0.7, origin='upper')
                
                # Path so far
                if step > 0:
                    y_coords, x_coords = zip(*path[:step+1])
                    ax.plot(x_coords, y_coords, 'c-', linewidth=2.5, alpha=0.8, label='Path')
                
                # Current position
                current_y, current_x = path[step]
                ax.plot(current_x, current_y, 'o', color='red', markersize=10, label='Drone')
                
                # Goal
                goal_y, goal_x = st.session_state.goal_pos
                ax.plot(goal_x, goal_y, 's', color='lime', markersize=12, label='Goal')
                
                # Start
                start_y, start_x = st.session_state.drone_pos
                ax.plot(start_x, start_y, '^', color='blue', markersize=10, label='Start')
                
                ax.set_xlim(-0.5, grid.shape[1] - 0.5)
                ax.set_ylim(grid.shape[0] - 0.5, -0.5)
                ax.set_aspect('equal')
                ax.legend(loc='upper right')
                ax.set_title(f'Step {step+1}/{len(path)}')
                ax.grid(True, alpha=0.2)
                
                with placeholder.container():
                    st.pyplot(fig, use_container_width=True)
                
                plt.close(fig)
                time.sleep(animation_speed)
        else:
            st.error("❌ No path found! Try adjusting the grid or positions.")
    
    with col_info:
        st.subheader("📈 Results")
        
        if path:
            path_length = sum(
                np.sqrt((path[i][0]-path[i-1][0])**2 + (path[i][1]-path[i-1][1])**2)
                for i in range(1, len(path))
            )
            
            st.metric("Path Length", f"{path_length:.2f}", "units")
            st.metric("Path Steps", len(path), "nodes")
            st.metric("Weight Used", f"{final_weight:.2f}", weight_source)
            
            # Quality score
            optimal_length = abs(st.session_state.goal_pos[0] - st.session_state.drone_pos[0]) + \
                           abs(st.session_state.goal_pos[1] - st.session_state.drone_pos[1])
            quality = (optimal_length / path_length) * 100 if path_length > 0 else 0
            
            st.metric("Path Quality", f"{quality:.1f}%", "optimal reference")
        else:
            st.warning("No path to display")


# ============================================================================
# INFO SECTION
# ============================================================================
st.divider()

with st.expander("📚 About This System", expanded=False):
    st.markdown("""
    ### Self-Learning Heuristic in A*
    The algorithm uses an **adaptive safety-aware heuristic** that:
    1. Calculates distance to goal (standard A*)
    2. Detects obstacles in nearby area (3x3 neighborhood)
    3. Applies repulsion penalty based on proximity to obstacles
    4. The heuristic "learns" to avoid danger zones by applying higher penalties
    
    ### A* Weight Parameter
    - **Weight = 1.0**: Optimal pathfinding (A*)
    - **Weight > 1.0**: Greedy pathfinding (faster, less optimal)
    - **Weight < 1.0**: Conservative pathfinding (slower, safer)
    
    ### RL Training (PPO)
    A Proximal Policy Optimization (PPO) agent learns to:
    - Analyze the environment (obstacle density and distribution)
    - Dynamically adjust the A* weight parameter
    - Optimize for both path quality and computation speed
    
    ### Modes
    - **Manual A***: You control the weight directly
    - **Auto RL**: The trained model suggests the best weight automatically
    """)

with st.expander("🚀 Quick Start", expanded=False):
    st.markdown("""
    1. **Set Grid**: Adjust grid size and obstacle density
    2. **Choose Mode**: Manual A* or Auto RL
    3. **Set Positions**: Specify start and goal positions
    4. **Run**: Click "Run Pathfinding" to visualize
    
    **Tips**:
    - Higher obstacle density → Higher recommended weight
    - Manual mode for learning / RL mode for automation
    - Watch the animation to see the drone navigating
    """)

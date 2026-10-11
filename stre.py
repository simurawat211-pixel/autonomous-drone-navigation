import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import gymnasium as gym
from gymnasium import spaces
from streamlit_drawable_canvas import st_canvas
from stable_baselines3 import PPO

from base import DroneNavigationEnv

st.set_page_config(layout="wide")
st.title("🚁 Interactive Drone AI System")

# =============================
# 🔹 SESSION STATE (IMPORTANT)
# =============================
if "start" not in st.session_state:
    st.session_state.start = (0, 0)

if "goal" not in st.session_state:
    st.session_state.goal = (10, 10)

# =============================
# 🔹 SIDEBAR
# =============================
st.sidebar.header("⚙️ Controls")

grid_size = st.sidebar.slider("Grid Size", 10, 40, 20)
speed = st.sidebar.slider("Speed", 0.01, 0.3, 0.08)

mode = st.sidebar.radio("Mode", ["Manual", "RL 🤖"])

weight = 2.0
if mode == "Manual":
    weight = st.sidebar.slider("Weight", 1.0, 10.0, 2.0)

run = st.sidebar.button("🚀 Run")

# =============================
# 🎮 CANVAS
# =============================
st.subheader("🖱️ Draw Obstacles + Click for Start/Goal")

canvas = st_canvas(
    fill_color="black",
    stroke_width=10,
    stroke_color="black",
    background_color="white",
    height=400,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

# =============================
# 🎯 CLICK TO SET START / GOAL
# =============================
if canvas.json_data is not None:
    objects = canvas.json_data["objects"]

    if len(objects) > 0:
        last_obj = objects[-1]

        if last_obj["type"] == "circle":
            x = int(last_obj["left"] / 400 * grid_size)
            y = int(last_obj["top"] / 400 * grid_size)

            # Alternate start/goal
            if "toggle" not in st.session_state:
                st.session_state.toggle = True

            if st.session_state.toggle:
                st.session_state.start = (y, x)
            else:
                st.session_state.goal = (y, x)

            st.session_state.toggle = not st.session_state.toggle

st.write(f"🎯 Start: {st.session_state.start}")
st.write(f"🏁 Goal: {st.session_state.goal}")

# =============================
# 🔄 CANVAS → GRID
# =============================
def canvas_to_grid(image_data, size):
    grid = np.zeros((size, size))

    if image_data is None:
        return grid

    img = image_data[:, :, 0]
    h, w = img.shape

    for i in range(size):
        for j in range(size):
            y = int(i * h / size)
            x = int(j * w / size)

            if img[y, x] < 200:
                grid[i, j] = 1

    return grid.astype(int)

# =============================
# 🤖 LOAD RL MODEL
# =============================
@st.cache_resource
def load_model():
    return PPO.load("ppo_drone_model")

model = None
if mode == "RL 🤖":
    try:
        model = load_model()
    except:
        st.warning("⚠️ Train model first")

# =============================
# 🚀 RUN
# =============================

if run:

    # Create env
    env = DroneNavigationEnv(
        grid_size=grid_size,
        obstacle_density=0
    )

    # Convert canvas to obstacle grid
    grid = canvas_to_grid(canvas.image_data, grid_size)

    # Update env
    env.grid = grid
    env.drone_pos = np.array(st.session_state.start)
    env.goal_pos = np.array(st.session_state.goal)

    # Gymnasium reset
    obs, info = env.reset()

    # RL Mode
    if mode == "RL 🤖" and model:

        try:
            # Predict action
            action, _ = model.predict(obs)
            
            # Clamp weight to valid range [1.0, 10.0]
            weight = float(np.clip(action[0], 1.0, 10.0))
        except Exception as e:
            st.warning(f"⚠️ Model prediction failed: {e}")
            weight = 1.0

    else:
        weight = 1.0

    # Gymnasium step
    obs, reward, terminated, truncated, info = env.step([weight])

    done = terminated or truncated

    path = env.current_path

    st.write(f"Reward: {reward}")
    st.write(f"Path Length: {info.get('path_len', 0)}")
    st.write(f"Weight Used: {weight:.2f}")

    if not path:
        st.error("❌ No path found!")

    else:

        plot = st.empty()

        for i in range(len(path)):

            fig, ax = plt.subplots(figsize=(5, 5))

            ax.imshow(env.grid, cmap='Greys')

            # Draw path
            py, px = zip(*path[:i + 1])
            ax.plot(px, py, 'cyan')

            # Drone position
            y, x = path[i]
            ax.plot(x, y, 'ro')

            # Goal position
            gy, gx = st.session_state.goal
            ax.plot(gx, gy, 'gs')

            plot.pyplot(fig)

            plt.close(fig)

            time.sleep(speed)
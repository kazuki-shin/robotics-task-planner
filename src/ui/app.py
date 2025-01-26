import streamlit as st
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import time
from src.core.task_planner import TaskPlanner
from src.core.code_generator import RobotCodeGenerator
from src.simulation.robot_environment import RobotEnvironment
from src.utils.error_handler import setup_logging, RoboticsError

def initialize_session_state():
    """Initialize session state variables"""
    if 'env' not in st.session_state:
        st.session_state.env = RobotEnvironment(gui=False)
        st.session_state.env.add_camera(
            'main_view',
            position=[2, 2, 2],
            target=[0, 0, 0]
        )
    
    if 'task_planner' not in st.session_state:
        st.session_state.task_planner = TaskPlanner()
    
    if 'code_generator' not in st.session_state:
        st.session_state.code_generator = RobotCodeGenerator()
    
    # Initialize camera controls
    if 'camera_distance' not in st.session_state:
        st.session_state.camera_distance = 2.0
    if 'camera_yaw' not in st.session_state:
        st.session_state.camera_yaw = 45.0
    if 'camera_pitch' not in st.session_state:
        st.session_state.camera_pitch = -35.0

def update_camera_view():
    """Update camera position based on spherical coordinates"""
    # Convert spherical coordinates to Cartesian
    distance = st.session_state.camera_distance
    yaw = np.radians(st.session_state.camera_yaw)
    pitch = np.radians(st.session_state.camera_pitch)
    
    x = distance * np.cos(pitch) * np.sin(yaw)
    y = distance * np.cos(pitch) * np.cos(yaw)
    z = distance * np.sin(pitch)
    
    # Update camera position
    st.session_state.env.update_camera(
        'main_view',
        position=[x, y, z],
        target=[0, 0, 0]
    )

def render_simulation_view():
    """Render the simulation view with camera controls"""
    # Camera controls
    st.subheader("Camera Controls")
    cols = st.columns(3)
    
    with cols[0]:
        st.session_state.camera_distance = st.slider(
            "Distance", 1.0, 5.0, 
            st.session_state.camera_distance,
            key="cam_distance"
        )
    
    with cols[1]:
        st.session_state.camera_yaw = st.slider(
            "Yaw", -180.0, 180.0, 
            st.session_state.camera_yaw,
            key="cam_yaw"
        )
    
    with cols[2]:
        st.session_state.camera_pitch = st.slider(
            "Pitch", -89.0, 89.0, 
            st.session_state.camera_pitch,
            key="cam_pitch"
        )
    
    # Update camera view based on controls
    update_camera_view()
    
    # Get and display camera image
    img = st.session_state.env.get_camera_image('main_view')
    
    # Add image display options
    display_options = st.columns(2)
    with display_options[0]:
        show_grid = st.checkbox("Show Grid", value=True)
    with display_options[1]:
        show_axes = st.checkbox("Show Axes", value=True)
    
    # Create figure with matplotlib for more control
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(img)
    
    # Optionally add grid
    if show_grid:
        ax.grid(True, alpha=0.3)
    
    # Optionally add axes indicators
    if show_axes:
        ax.axhline(y=img.shape[0]/2, color='r', alpha=0.3)
        ax.axvline(x=img.shape[1]/2, color='r', alpha=0.3)
    
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Display the figure
    st.pyplot(fig)
    
    # Add quick view buttons
    st.write("Quick Views:")
    quick_view_cols = st.columns(4)
    
    if quick_view_cols[0].button("Top View"):
        st.session_state.camera_yaw = 0
        st.session_state.camera_pitch = 89
        st.experimental_rerun()
    
    if quick_view_cols[1].button("Front View"):
        st.session_state.camera_yaw = 0
        st.session_state.camera_pitch = 0
        st.experimental_rerun()
    
    if quick_view_cols[2].button("Side View"):
        st.session_state.camera_yaw = 90
        st.session_state.camera_pitch = 0
        st.experimental_rerun()
    
    if quick_view_cols[3].button("Isometric"):
        st.session_state.camera_yaw = 45
        st.session_state.camera_pitch = -35
        st.experimental_rerun()

def main():
    setup_logging()
    st.set_page_config(page_title="Robotics Task Planner", layout="wide")
    
    st.title("🤖 Robotics Task Planner")
    initialize_session_state()
    
    # Create two columns for layout
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Task Configuration")
        
        # Task input
        instruction = st.text_area(
            "Enter your instruction:",
            "Pick up the red cube and place it on the blue platform",
            height=100
        )
        
        # Object configuration
        st.subheader("Object Configuration")
        with st.expander("Add Object"):
            obj_name = st.text_input("Object Name", "cube")
            x = st.slider("X Position", -1.0, 1.0, 0.0)
            y = st.slider("Y Position", -1.0, 1.0, 0.0)
            z = st.slider("Z Position", 0.0, 1.0, 0.5)
            
            if st.button("Add Object"):
                try:
                    st.session_state.env.add_object(obj_name, (x, y, z))
                    st.success(f"Added {obj_name} at position ({x}, {y}, {z})")
                except RoboticsError as e:
                    st.error(f"Failed to add object: {str(e)}")
    
    with col2:
        st.subheader("Simulation View")
        render_simulation_view()
        
        # Task execution section
        if st.button("Plan & Execute Task"):
            try:
                with st.spinner("Planning task..."):
                    # Generate task plan
                    task_plan = st.session_state.task_planner.decompose_task(instruction)
                    
                    # Display task plan
                    st.json(task_plan)
                    
                    # Generate code
                    code = st.session_state.code_generator.generate_code(task_plan)
                    
                    # Display generated code
                    st.code(code, language="python")
                    
                    # Execute task (simulation updates automatically)
                    exec(code)
                    st.success("Task executed successfully!")
                    
            except RoboticsError as e:
                st.error(f"Task execution failed: {str(e)}")
    
    # Status and monitoring
    st.sidebar.subheader("System Status")
    st.sidebar.metric("Simulation FPS", value=f"{30:.1f}")
    
    # Object status
    st.sidebar.subheader("Object Status")
    for obj_name in st.session_state.env.objects:
        state = st.session_state.env.get_object_state(obj_name)
        st.sidebar.text(f"{obj_name}:")
        st.sidebar.text(f"Position: {state['position']}")

if __name__ == "__main__":
    main() 
import pytest
import numpy as np
from src.simulation.robot_environment import RobotEnvironment
from src.simulation.robot_actions import RobotActions
from src.utils.error_handler import SimulationError

@pytest.fixture
def robot_env():
    # Initialize environment in headless mode
    env = RobotEnvironment(gui=False)
    yield env
    env.close()

@pytest.fixture
def robot_actions(robot_env):
    return RobotActions(robot_env.robot_id)

def test_environment_initialization(robot_env):
    assert robot_env.physics_client is not None
    assert robot_env.robot_id is not None
    assert robot_env.plane_id is not None

def test_camera_controls(robot_env):
    # Test camera addition
    camera_pos = (2, 2, 2)
    camera_target = (0, 0, 0)
    robot_env.add_camera("test_cam", camera_pos, camera_target)
    
    # Test camera parameters retrieval
    params = robot_env.get_camera_params("test_cam")
    assert "position" in params
    assert "target" in params
    assert np.allclose(params["position"], camera_pos, atol=1e-3)
    assert np.allclose(params["target"], camera_target, atol=1e-3)
    
    # Test camera update
    new_pos = (3, 3, 3)
    new_target = (1, 1, 1)
    robot_env.update_camera("test_cam", new_pos, new_target)
    
    updated_params = robot_env.get_camera_params("test_cam")
    assert np.allclose(updated_params["position"], new_pos, atol=1e-3)
    assert np.allclose(updated_params["target"], new_target, atol=1e-3)
    
    # Test camera image capture
    img = robot_env.get_camera_image("test_cam")
    assert isinstance(img, np.ndarray)
    assert len(img.shape) == 3  # RGB image
    assert img.shape[2] == 3    # 3 color channels (RGB)
    assert img.dtype == np.uint8  # Check image data type

def test_invalid_camera_operations(robot_env):
    # Test invalid camera name
    with pytest.raises(ValueError):
        robot_env.get_camera_params("nonexistent_camera")
    
    with pytest.raises(SimulationError):
        robot_env.get_camera_image("nonexistent_camera")

def test_object_manipulation(robot_env):
    # Test adding object
    obj_pos = (0, 0, 1)
    obj_id = robot_env.add_object("cube", obj_pos)
    assert obj_id is not None
    
    # Test getting object position
    retrieved_pos = robot_env.get_object_position("cube")
    assert np.allclose(retrieved_pos, obj_pos, atol=1e-3)

def test_robot_actions(robot_actions):
    # Test movement
    target_pos = (0.5, 0.5, 0.5)
    robot_actions.move_to_position(target_pos)
    
    # Test gripper operations
    robot_actions.open_gripper()
    assert robot_actions.gripper_open is True
    
    robot_actions.close_gripper()
    assert robot_actions.gripper_open is False

def test_environment_reset(robot_env):
    # Add camera and object
    robot_env.add_camera("test_cam", (1, 1, 1), (0, 0, 0))
    robot_env.add_object("cube", (0, 0, 1))
    
    # Reset environment
    robot_env.reset()
    
    # Check if cameras and objects are cleared
    assert len(robot_env.cameras) == 0
    assert len(robot_env.objects) == 0

def test_headless_mode():
    """Test that environment can run in headless mode"""
    env = RobotEnvironment(gui=False)
    try:
        # Verify we can perform operations without GUI
        env.add_camera("test", (1, 1, 1), (0, 0, 0))
        img = env.get_camera_image("test")
        assert isinstance(img, np.ndarray)
        assert img.shape[2] == 3  # RGB channels
    finally:
        env.close() 
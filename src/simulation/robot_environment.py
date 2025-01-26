import pybullet as p
import pybullet_data
import numpy as np
from typing import Tuple, Optional, Dict
from src.utils.error_handler import SimulationError, error_handler
from .textures import ensure_textures
import os

class RobotEnvironment:
    def __init__(self, gui: bool = True):
        """Initialize robot environment
        
        Args:
            gui (bool): Whether to show GUI window. Set False for headless mode.
        """
        self.gui = gui  # Store gui setting for reset
        # Use DIRECT mode for headless operation during testing
        self.physics_client = p.connect(p.GUI if gui else p.DIRECT)
        p.setGravity(0, 0, -9.81)
        
        # Initialize attributes
        self.robot_id = None
        self.plane_id = None
        self.cameras = {}
        self.objects = {}
        
        # Load environment
        self._load_environment()
    
    @error_handler(SimulationError)
    def _load_environment(self):
        """Load environment objects and textures"""
        # Get paths
        texture_path = os.path.join(os.path.dirname(__file__), 'textures', 'checker_blue.png')
        plane_urdf = os.path.join(os.path.dirname(__file__), 'models', 'plane.urdf')
        robot_urdf = os.path.join(os.path.dirname(__file__), 'models', 'robot_arm.urdf')
        
        # Load ground plane with texture
        textureUniqueId = p.loadTexture(texture_path)
        self.plane_id = p.loadURDF(plane_urdf, [0, 0, 0])
        p.changeVisualShape(self.plane_id, -1, textureUniqueId=textureUniqueId)
        
        # Load robot arm
        self.robot_id = p.loadURDF(robot_urdf, [0, 0, 0], useFixedBase=True)
        
        # Setup workspace boundaries
        self.workspace_bounds = {
            'x': (-1, 1),
            'y': (-1, 1),
            'z': (0, 1.5)
        }
    
    @error_handler(SimulationError)
    def add_camera(self, name: str, position: Tuple[float, float, float],
                  target: Tuple[float, float, float]):
        """Add a camera to the environment"""
        view_matrix = p.computeViewMatrix(
            position, target, [0, 0, 1]
        )
        proj_matrix = p.computeProjectionMatrixFOV(
            fov=60.0,
            aspect=1.0,
            nearVal=0.1,
            farVal=100.0
        )
        self.cameras[name] = {
            'view_matrix': view_matrix,
            'projection_matrix': proj_matrix,
            'position': position,
            'target': target
        }
    
    @error_handler(SimulationError)
    def get_camera_image(self, camera_name: str) -> np.ndarray:
        """Get RGB image from specified camera"""
        if camera_name not in self.cameras:
            raise ValueError(f"Camera {camera_name} not found")
            
        width, height = 320, 240
        camera = self.cameras[camera_name]
        
        img = p.getCameraImage(
            width,
            height,
            camera['view_matrix'],
            camera['projection_matrix']
        )
        
        # Convert RGBA to RGB
        rgba = np.array(img[2])
        rgb = rgba[:, :, :3]  # Take only the first 3 channels (RGB)
        return rgb
    
    def reset(self):
        """Reset the environment while maintaining GUI/headless setting"""
        p.resetSimulation()
        self.__init__(gui=self.gui)  # Pass the original gui setting
    
    def step_simulation(self):
        p.stepSimulation()
    
    def add_object(self, object_name: str, position: Tuple[float, float, float]):
        """
        Add an object to the environment
        
        Args:
            object_name: Name of the object (must have corresponding URDF file)
            position: (x, y, z) position to place the object
        """
        urdf_path = os.path.join(os.path.dirname(__file__), 'models', f'{object_name}.urdf')
        if not os.path.exists(urdf_path):
            raise SimulationError(f"URDF file not found for object: {object_name}")
            
        object_id = p.loadURDF(urdf_path, position)
        self.objects[object_name] = object_id
        return object_id
    
    def get_object_position(self, object_name: str) -> Optional[Tuple[float, float, float]]:
        if object_name in self.objects:
            pos, _ = p.getBasePositionAndOrientation(self.objects[object_name])
            return pos
        return None
    
    def close(self):
        p.disconnect()
    
    @error_handler(SimulationError)
    def check_collision(self, object_id: int) -> bool:
        """Check if object is in collision with environment"""
        return len(p.getContactPoints(object_id)) > 0
    
    @error_handler(SimulationError)
    def get_object_state(self, object_name: str) -> Dict:
        """Get complete state of an object"""
        if object_name not in self.objects:
            raise ValueError(f"Object {object_name} not found")
            
        obj_id = self.objects[object_name]
        pos, orn = p.getBasePositionAndOrientation(obj_id)
        lin_vel, ang_vel = p.getBaseVelocity(obj_id)
        
        return {
            'position': pos,
            'orientation': orn,
            'linear_velocity': lin_vel,
            'angular_velocity': ang_vel
        }

    def update_camera(self, name: str, position: Tuple[float, float, float],
                    target: Tuple[float, float, float]):
        """Update existing camera position and target"""
        view_matrix = p.computeViewMatrix(
            position, target, [0, 0, 1]
        )
        proj_matrix = p.computeProjectionMatrixFOV(
            fov=60.0,
            aspect=1.0,
            nearVal=0.1,
            farVal=100.0
        )
        self.cameras[name] = {
            'view_matrix': view_matrix,
            'projection_matrix': proj_matrix,
            'position': position,
            'target': target
        }

    def get_camera_params(self, name: str) -> Dict:
        """Get camera parameters"""
        if name not in self.cameras:
            raise ValueError(f"Camera {name} not found")
        return {
            'position': self.cameras[name]['position'],
            'target': self.cameras[name]['target']
        } 
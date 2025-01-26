from typing import Dict, Any
import logging
import re

class RobotCodeGenerator:
    """
    Translates task plans into executable robot code
    
    Supported Actions:
    - move_to/move/goto: Move robot to a position
    - pick_up/pickup/grab: Pick up an object
    - place/put/place_on: Place an object
    - locate_object/find/locate: Find an object in the workspace
    - identify_object/identify/check: Identify object properties
    - rotate/turn: Rotate the robot/gripper
    - open_gripper/open: Open the gripper
    - close_gripper/close: Close the gripper
    """
    
    ACTION_ALIASES = {
        # Movement
        'move': 'move_to',
        'goto': 'move_to',
        # Pickup
        'pickup': 'pick_up',
        'grab': 'pick_up',
        # Placement
        'put': 'place',
        'place_on': 'place',
        # Location
        'find': 'locate_object',
        'locate': 'locate_object',
        # Identification
        'identify': 'identify_object',
        'check': 'identify_object',
        # Rotation
        'turn': 'rotate',
        # Gripper
        'open': 'open_gripper',
        'close': 'close_gripper',
    }
    
    SUPPORTED_ACTIONS = {
        'move_to': 'self.robot.move_to_position',
        'pick_up': 'self.robot.pick_object',
        'place': 'self.robot.place_object',
        'locate_object': 'self.robot.locate_object',
        'identify_object': 'self.robot.identify_object',
        'rotate': 'self.robot.rotate',
        'open_gripper': 'self.robot.open_gripper',
        'close_gripper': 'self.robot.close_gripper'
    }
    
    REQUIRED_PARAMETERS = {
        'move_to': ['position'],
        'pick_up': ['object'],
        'place': ['position'],
        'locate_object': ['object'],
        'identify_object': ['object'],
        'rotate': ['angle'],
        'open_gripper': [],
        'close_gripper': []
    }
    
    def _normalize_action(self, action: str) -> str:
        """Convert action aliases to standard action names"""
        # Convert to lowercase and remove whitespace
        action = action.lower().strip()
        # Handle special case for PlaceOn -> place_on -> place
        if action == "placeon":
            action = "place_on"
        return self.ACTION_ALIASES.get(action, action)
    
    def _format_parameter_value(self, param_name: str, value: Any) -> str:
        """Format parameter value based on its type and name"""
        if param_name == 'position':
            if isinstance(value, (list, tuple)):
                return str(list(value))  # Convert to list representation
            elif isinstance(value, str):
                # Convert position name to coordinate lookup
                return f"self.robot.get_position('{value}')"
        elif param_name == 'object':
            return f"'{value}'"  # Wrap object names in quotes
        elif param_name == 'angle':
            return str(float(value))  # Ensure angle is a number
        return str(value)
    
    def generate_code(self, task_plan: Dict[str, Any]) -> str:
        """
        Convert task plan to executable Python code
        
        Args:
            task_plan (Dict): Structured task decomposition
        
        Returns:
            str: Generated Python execution script
            
        Raises:
            ValueError: If an unsupported action is encountered
            KeyError: If required parameters are missing
        """
        code_lines = [
            "# Auto-generated Robotic Task Execution Script",
            "def execute_robot_task():",
            "    try:"
        ]
        
        for step in task_plan['action_sequence']:
            # Validate step has required fields
            if 'parameters' not in step:
                raise KeyError(f"Missing 'parameters' field in action step: {step}")
            
            action = self._normalize_action(step['action'])
            
            if action not in self.SUPPORTED_ACTIONS:
                supported = ", ".join(sorted(set(list(self.SUPPORTED_ACTIONS.keys()) + list(self.ACTION_ALIASES.keys()))))
                raise ValueError(
                    f"Unsupported action: {step['action']}. "
                    f"Supported actions are: {supported}"
                )
            
            # Validate required parameters
            params = step.get('parameters', {})
            required_params = self.REQUIRED_PARAMETERS[action]
            missing_params = [p for p in required_params if p not in params]
            if missing_params:
                raise ValueError(
                    f"Missing required parameters for action '{action}': "
                    f"{', '.join(missing_params)}"
                )
            
            # Generate action invocation with parameters
            param_strings = []
            for param_name, value in params.items():
                formatted_value = self._format_parameter_value(param_name, value)
                param_strings.append(f"{param_name}={formatted_value}")
            
            code_lines.append(
                f"        {self.SUPPORTED_ACTIONS[action]}({', '.join(param_strings)})"
            )
        
        # Error handling and logging
        code_lines.extend([
            "    except Exception as e:",
            "        logging.error(f'Task execution failed: {e}')",
            "        raise"
        ])
        
        return "\n".join(code_lines) 
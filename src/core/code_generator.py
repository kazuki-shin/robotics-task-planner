from typing import Dict, Any
import logging

class RobotCodeGenerator:
    SUPPORTED_ACTIONS = {
        'move_to': 'self.robot.move_to_position',
        'pick_up': 'self.robot.pick_object',
        'place': 'self.robot.place_object',
        'rotate': 'self.robot.rotate',
        'open_gripper': 'self.robot.open_gripper',
        'close_gripper': 'self.robot.close_gripper'
    }
    
    def generate_code(self, task_plan: Dict[str, Any]) -> str:
        """
        Convert task plan to executable Python code
        
        Args:
            task_plan (Dict): Structured task decomposition
        
        Returns:
            str: Generated Python execution script
        """
        code_lines = [
            "# Auto-generated Robotic Task Execution Script",
            "def execute_robot_task():",
            "    try:"
        ]
        
        for step in task_plan['action_sequence']:
            action = step['action'].lower()
            
            if action not in self.SUPPORTED_ACTIONS:
                raise ValueError(f"Unsupported action: {action}")
            
            # Format parameters with proper string handling
            params = step.get('parameters', {})
            formatted_params = []
            
            if 'position' in params:
                formatted_params.append(f"position={params['position']}")
            
            if 'object' in params:
                # Quote string parameters
                formatted_params.append(f"object='{params['object']}'")
            
            # Generate specific action invocation
            code_lines.append(
                f"        {self.SUPPORTED_ACTIONS[action]}({', '.join(formatted_params)})"
            )
        
        # Error handling and logging
        code_lines.extend([
            "    except Exception as e:",
            "        logging.error(f'Task execution failed: {e}')",
            "        raise"
        ])
        
        return "\n".join(code_lines) 
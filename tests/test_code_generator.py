import pytest
from src.core.code_generator import RobotCodeGenerator
from typing import Dict, Any

@pytest.fixture
def code_generator():
    return RobotCodeGenerator()

@pytest.fixture
def valid_task_plan() -> Dict[str, Any]:
    return {
        "objective": "Pick up the red cube",
        "action_sequence": [
            {
                "action": "move_to",
                "parameters": {
                    "position": [0.1, 0.2, 0.3],
                    "object": "red_cube"
                }
            },
            {
                "action": "pick_up",
                "parameters": {
                    "object": "red_cube"
                }
            },
            {
                "action": "place",
                "parameters": {
                    "position": [0.4, 0.5, 0.6]
                }
            }
        ]
    }

def test_generate_code_success(code_generator, valid_task_plan):
    code = code_generator.generate_code(valid_task_plan)
    
    # Verify the generated code structure
    assert "def execute_robot_task():" in code
    assert "try:" in code
    assert "except Exception as e:" in code
    assert "logging.error" in code
    
    # Verify all actions are included
    assert "self.robot.move_to_position" in code
    assert "self.robot.pick_object" in code
    assert "self.robot.place_object" in code

def test_unsupported_action(code_generator):
    invalid_plan = {
        "objective": "Test task",
        "action_sequence": [
            {
                "action": "unsupported_action",
                "parameters": {}
            }
        ]
    }
    
    with pytest.raises(ValueError) as exc_info:
        code_generator.generate_code(invalid_plan)
    
    assert "Unsupported action: unsupported_action" in str(exc_info.value)

def test_missing_parameters(code_generator):
    invalid_plan = {
        "objective": "Test task",
        "action_sequence": [
            {
                "action": "move_to",
                # Missing parameters
            }
        ]
    }
    
    with pytest.raises(KeyError) as exc_info:
        code_generator.generate_code(invalid_plan)
    
    assert "parameters" in str(exc_info.value)

def test_empty_action_sequence(code_generator):
    empty_plan = {
        "objective": "Test task",
        "action_sequence": []
    }
    
    code = code_generator.generate_code(empty_plan)
    assert "def execute_robot_task():" in code
    assert "try:" in code
    assert "except Exception as e:" in code

def test_supported_actions_constant(code_generator):
    # Verify all supported actions are properly mapped
    expected_actions = {
        'move_to': 'self.robot.move_to_position',
        'pick_up': 'self.robot.pick_object',
        'place': 'self.robot.place_object',
        'locate_object': 'self.robot.locate_object',
        'identify_object': 'self.robot.identify_object',
        'rotate': 'self.robot.rotate',
        'open_gripper': 'self.robot.open_gripper',
        'close_gripper': 'self.robot.close_gripper'
    }
    
    assert code_generator.SUPPORTED_ACTIONS == expected_actions

def test_action_parameter_handling(code_generator):
    plan_with_parameters = {
        "objective": "Test parameters",
        "action_sequence": [
            {
                "action": "move_to",
                "parameters": {
                    "position": [1, 2, 3],
                    "object": "test_obj"
                }
            }
        ]
    }
    
    code = code_generator.generate_code(plan_with_parameters)
    assert "position=[1, 2, 3]" in code
    assert "object='test_obj'" in code

def test_error_handling_code(code_generator, valid_task_plan):
    code = code_generator.generate_code(valid_task_plan)
    
    # Verify error handling structure
    assert "try:" in code
    assert "except Exception as e:" in code
    assert "logging.error" in code
    assert "raise" in code

def test_additional_actions(code_generator):
    plan = {
        "objective": "Complex task",
        "action_sequence": [
            {
                "action": "locate_object",
                "parameters": {
                    "object": "red_cube"
                }
            },
            {
                "action": "identify_object",
                "parameters": {
                    "object": "red_cube"
                }
            },
            {
                "action": "rotate",
                "parameters": {
                    "angle": 90
                }
            },
            {
                "action": "open_gripper",
                "parameters": {}
            },
            {
                "action": "close_gripper",
                "parameters": {}
            }
        ]
    }
    
    code = code_generator.generate_code(plan)
    
    # Verify all actions are included
    assert "self.robot.locate_object" in code
    assert "self.robot.identify_object" in code
    assert "self.robot.rotate" in code
    assert "self.robot.open_gripper" in code
    assert "self.robot.close_gripper" in code

def test_missing_required_parameters(code_generator):
    invalid_plan = {
        "objective": "Test task",
        "action_sequence": [
            {
                "action": "move_to",
                "parameters": {
                    # Missing required 'position' parameter
                    "object": "cube"
                }
            }
        ]
    }
    
    with pytest.raises(ValueError) as exc_info:
        code_generator.generate_code(invalid_plan)
    
    assert "Missing required parameters" in str(exc_info.value)
    assert "position" in str(exc_info.value)

def test_unsupported_action_message(code_generator):
    invalid_plan = {
        "objective": "Test task",
        "action_sequence": [
            {
                "action": "invalid_action",
                "parameters": {}
            }
        ]
    }
    
    with pytest.raises(ValueError) as exc_info:
        code_generator.generate_code(invalid_plan)
    
    error_msg = str(exc_info.value)
    assert "Unsupported action: invalid_action" in error_msg
    assert "Supported actions are:" in error_msg
    for action in code_generator.SUPPORTED_ACTIONS:
        assert action in error_msg 

def test_parameter_formatting(code_generator):
    plan = {
        "objective": "Test parameter formatting",
        "action_sequence": [
            {
                "action": "move_to",
                "parameters": {
                    "position": "blue platform",  # String position
                    "object": "red cube"
                }
            },
            {
                "action": "move_to",
                "parameters": {
                    "position": [1.0, 2.0, 3.0],  # Coordinate position
                    "object": "green ball"
                }
            },
            {
                "action": "rotate",
                "parameters": {
                    "angle": 90.5  # Float angle
                }
            }
        ]
    }
    
    code = code_generator.generate_code(plan)
    
    # Check position handling
    assert "position=self.robot.get_position('blue platform')" in code
    assert "position=[1.0, 2.0, 3.0]" in code
    
    # Check object name handling
    assert "object='red cube'" in code
    assert "object='green ball'" in code
    
    # Check angle handling
    assert "angle=90.5" in code

def test_parameter_value_formatting(code_generator):
    # Test position formatting
    assert code_generator._format_parameter_value('position', [1, 2, 3]) == '[1, 2, 3]'
    assert code_generator._format_parameter_value('position', 'target') == "self.robot.get_position('target')"
    
    # Test object formatting
    assert code_generator._format_parameter_value('object', 'cube') == "'cube'"
    
    # Test angle formatting
    assert code_generator._format_parameter_value('angle', 90) == '90.0'
    assert code_generator._format_parameter_value('angle', '45.5') == '45.5'

def test_action_aliases(code_generator):
    plan = {
        "objective": "Test action aliases",
        "action_sequence": [
            {
                "action": "goto",  # alias for move_to
                "parameters": {
                    "position": [1, 2, 3]
                }
            },
            {
                "action": "pickup",  # alias for pick_up
                "parameters": {
                    "object": "cube"
                }
            },
            {
                "action": "place_on",  # alias for place
                "parameters": {
                    "position": "table"
                }
            }
        ]
    }
    
    code = code_generator.generate_code(plan)
    
    # Check that aliases are converted to proper function calls
    assert "self.robot.move_to_position" in code
    assert "self.robot.pick_object" in code
    assert "self.robot.place_object" in code

def test_action_normalization(code_generator):
    # Test various forms of action names
    assert code_generator._normalize_action("MOVE_TO") == "move_to"
    assert code_generator._normalize_action("pickup ") == "pick_up"
    assert code_generator._normalize_action("PlaceOn") == "place"
    assert code_generator._normalize_action("grab") == "pick_up"
    assert code_generator._normalize_action("unknown") == "unknown"

def test_error_message_includes_aliases(code_generator):
    invalid_plan = {
        "objective": "Test task",
        "action_sequence": [
            {
                "action": "invalid_action",
                "parameters": {}
            }
        ]
    }
    
    with pytest.raises(ValueError) as exc_info:
        code_generator.generate_code(invalid_plan)
    
    error_msg = str(exc_info.value)
    # Check that error message includes both main actions and aliases
    assert "goto" in error_msg
    assert "pickup" in error_msg
    assert "place_on" in error_msg
    assert "move_to" in error_msg 
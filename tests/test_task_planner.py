import pytest
from src.core.task_planner import TaskPlanner
from src.utils.error_handler import TaskPlanningError
from tenacity import RetryError

@pytest.fixture
def task_planner():
    return TaskPlanner()

def test_task_decomposition_success(task_planner):
    instruction = "Pick up the red cube and place it on the blue platform"
    result = task_planner.decompose_task(instruction)
    
    assert "objective" in result
    assert "action_sequence" in result
    assert len(result["action_sequence"]) > 0

def test_invalid_instruction(task_planner):
    with pytest.raises((TaskPlanningError, RetryError)):
        task_planner.decompose_task("")

def test_task_validation(task_planner):
    invalid_plan = {
        "objective": "Test task",
        # Missing required keys
    }
    
    with pytest.raises(ValueError):
        task_planner._validate_task_plan(invalid_plan) 
import pytest
from unittest.mock import Mock, patch
from src.core.task_planner import TaskPlanner
from src.utils.error_handler import TaskPlanningError
from tenacity import RetryError
import json
import logging

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI API response"""
    mock_message = Mock()
    mock_message.content = """
    {
        "objective": "Pick up red cube and place on blue platform",
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
            }
        ]
    }
    """
    
    mock_choice = Mock()
    mock_choice.message = mock_message
    
    mock_response = Mock()
    mock_response.choices = [mock_choice]
    
    return mock_response

@pytest.fixture
def task_planner():
    planner = TaskPlanner()
    # Mock the OpenAI client
    planner.client = Mock()
    return planner

def test_task_decomposition_success(task_planner, mock_openai_response, caplog):
    caplog.set_level(logging.DEBUG)
    
    # Configure the mock
    task_planner.client.chat.completions.create.return_value = mock_openai_response
    
    instruction = "Pick up the red cube and place it on the blue platform"
    result = task_planner.decompose_task(instruction)
    
    # Verify the API was called correctly
    task_planner.client.chat.completions.create.assert_called_once()
    call_kwargs = task_planner.client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4"
    assert len(call_kwargs["messages"]) == 2
    assert call_kwargs["messages"][1]["content"] == instruction
    
    # Verify the result structure
    assert "objective" in result
    assert "action_sequence" in result
    assert len(result["action_sequence"]) > 0
    
    # Verify no error logs were generated
    assert not any(record.levelno >= logging.ERROR for record in caplog.records)

def test_invalid_instruction(task_planner, caplog):
    caplog.set_level(logging.DEBUG)
    
    with pytest.raises(TaskPlanningError) as exc_info:
        task_planner.decompose_task("")
    
    assert str(exc_info.value) == "Empty instruction provided"
    assert not task_planner.client.chat.completions.create.called

def test_task_validation(task_planner):
    invalid_plan = {
        "objective": "Test task",
        # Missing required keys
    }
    
    with pytest.raises(ValueError) as exc_info:
        task_planner._validate_task_plan(invalid_plan)
    
    assert str(exc_info.value) == "Invalid task plan structure"

def test_api_error_handling(task_planner, caplog):
    caplog.set_level(logging.DEBUG)
    
    # Simulate API error that will occur on every retry
    def raise_error(*args, **kwargs):
        raise Exception("API Error")
    
    task_planner.client.chat.completions.create.side_effect = raise_error
    
    with pytest.raises(RetryError) as exc_info:
        task_planner.decompose_task("Test instruction")
    
    retry_error = exc_info.value
    assert retry_error.last_attempt is not None
    
    # Get the last attempt's exception
    last_error = retry_error.last_attempt.exception()
    assert last_error is not None
    
    # Verify it's a TaskPlanningError with the correct message
    assert isinstance(last_error, TaskPlanningError)
    assert "API Error" in str(last_error)
    
    # Verify retry behavior
    assert retry_error.last_attempt.attempt_number == 3
    
    # Verify error was logged
    assert any("Task planning failed: API Error" in record.message 
              for record in caplog.records)

def test_json_decode_error(task_planner, caplog):
    caplog.set_level(logging.DEBUG)
    
    # Create a mock response with invalid JSON
    mock_message = Mock()
    mock_message.content = "Invalid JSON content"
    mock_choice = Mock()
    mock_choice.message = mock_message
    mock_response = Mock()
    mock_response.choices = [mock_choice]
    
    task_planner.client.chat.completions.create.return_value = mock_response
    
    with pytest.raises(RetryError) as exc_info:
        task_planner.decompose_task("Test instruction")
    
    last_error = exc_info.value.last_attempt.exception()
    assert isinstance(last_error, TaskPlanningError)
    assert "Failed to parse task plan" in str(last_error)
    assert "Expecting value" in str(last_error)

def test_task_planning_error_passthrough(task_planner, caplog):
    caplog.set_level(logging.DEBUG)
    
    original_error = TaskPlanningError("Original task error")
    
    def raise_task_error(*args, **kwargs):
        raise original_error
    
    task_planner.client.chat.completions.create.side_effect = raise_task_error
    
    with pytest.raises(RetryError) as exc_info:
        task_planner.decompose_task("Test instruction")
    
    last_error = exc_info.value.last_attempt.exception()
    assert isinstance(last_error, TaskPlanningError)
    assert last_error is original_error  # Should be the exact same error
    assert str(last_error) == "Original task error"

def test_get_system_prompt(task_planner):
    prompt = task_planner._get_system_prompt()
    assert isinstance(prompt, str)
    assert "robotic task planning system" in prompt
    assert "JSON object" in prompt
    assert "objective" in prompt
    assert "action_sequence" in prompt

def test_retry_error_handling(task_planner):
    # Test handling of RetryError without Future
    mock_retry_error = RetryError(last_attempt=None)
    
    with patch.object(task_planner, '_attempt_task_decomposition', side_effect=mock_retry_error):
        with pytest.raises(RetryError) as exc_info:
            task_planner.decompose_task("Test instruction")
        
        assert exc_info.value == mock_retry_error

def test_retry_error_with_non_task_planning_error(task_planner, caplog):
    caplog.set_level(logging.DEBUG)
    
    # Create a RetryError with a non-TaskPlanningError
    original_error = ValueError("Some other error")
    future = Mock()
    future.exception.return_value = original_error
    mock_retry_error = RetryError(last_attempt=future)
    
    with patch.object(task_planner, '_attempt_task_decomposition', side_effect=mock_retry_error):
        with pytest.raises(RetryError) as exc_info:
            task_planner.decompose_task("Test instruction")
        
        # Verify the error was converted
        last_error = exc_info.value.last_attempt.exception()
        assert isinstance(last_error, TaskPlanningError)
        assert str(original_error) in str(last_error) 
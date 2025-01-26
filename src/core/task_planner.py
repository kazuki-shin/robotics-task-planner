from openai import OpenAI
from typing import Dict, Any
import logging
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError, Future
from src.utils.error_handler import TaskPlanningError, error_handler

class TaskPlanner:
    def __init__(self):
        """Initialize task planner with OpenAI client"""
        self.model = "gpt-4"  # Can be configured via settings
        self.client = OpenAI()  # Initialize the client
        
    def decompose_task(self, instruction: str) -> Dict[str, Any]:
        """
        Decompose natural language instruction into structured task plan
        
        Args:
            instruction (str): Natural language instruction
            
        Returns:
            Dict: Structured task decomposition
            
        Raises:
            TaskPlanningError: If instruction is empty or planning fails
            RetryError: If all retries fail
        """
        if not instruction.strip():
            raise TaskPlanningError("Empty instruction provided")
            
        try:
            return self._attempt_task_decomposition(instruction)
        except RetryError as retry_err:
            # Get the original exception from the last retry attempt
            last_attempt = retry_err.last_attempt
            if isinstance(last_attempt, Future):
                original_error = last_attempt.exception()
                if original_error and not isinstance(original_error, TaskPlanningError):
                    # Convert non-TaskPlanningError to TaskPlanningError
                    last_attempt._exception = TaskPlanningError(str(original_error))
            raise retry_err
            
    def _should_retry(exception: Exception) -> bool:
        """Determine if an exception should trigger a retry"""
        return not isinstance(exception, TaskPlanningError)
            
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    def _attempt_task_decomposition(self, instruction: str) -> Dict[str, Any]:
        """
        Internal method to attempt task decomposition with retries
        
        Args:
            instruction (str): Natural language instruction
            
        Returns:
            Dict: Structured task decomposition
            
        Raises:
            TaskPlanningError: For any task planning related errors
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": instruction}
                ],
                temperature=0.7
            )
            
            try:
                task_plan = json.loads(response.choices[0].message.content.strip())
            except json.JSONDecodeError as e:
                raise TaskPlanningError(f"Failed to parse task plan: {str(e)}")
            
            validated_plan = self._validate_task_plan(task_plan)
            return validated_plan
            
        except TaskPlanningError:
            raise
        except Exception as e:
            logging.error(f"Task planning failed: {str(e)}")
            raise TaskPlanningError(f"Failed to plan task: {str(e)}")
    
    def _validate_task_plan(self, task_plan: Dict) -> Dict:
        """Validate task plan structure"""
        required_keys = ["objective", "action_sequence"]
        
        if not all(key in task_plan for key in required_keys):
            raise ValueError("Invalid task plan structure")
            
        return task_plan
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for task planning"""
        return """
        You are a robotic task planning system. Convert natural language instructions 
        into structured task plans. Always respond with a valid JSON object containing:
        {
            "objective": "Brief description of the task",
            "action_sequence": [
                {
                    "action": "action_name",
                    "parameters": {
                        "position": [x, y, z],
                        "object": "object_name"
                    }
                }
            ]
        }
        """ 
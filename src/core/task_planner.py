import openai
from typing import Dict, Any
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.error_handler import TaskPlanningError, error_handler

class TaskPlanner:
    def __init__(self):
        """Initialize task planner with OpenAI client"""
        self.model = "gpt-4"  # Can be configured via settings
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @error_handler(TaskPlanningError)
    def decompose_task(self, instruction: str) -> Dict[str, Any]:
        """
        Decompose natural language instruction into structured task plan
        
        Args:
            instruction (str): Natural language instruction
            
        Returns:
            Dict: Structured task decomposition
        """
        if not instruction.strip():
            raise TaskPlanningError("Empty instruction provided")
            
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": instruction}
                ],
                temperature=0.7
            )
            
            task_plan = response.choices[0].message.content
            validated_plan = self._validate_task_plan(task_plan)
            return validated_plan
            
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
        into structured task plans with clear action sequences. Include:
        1. Overall objective
        2. Sequence of atomic actions
        3. Required parameters for each action
        4. Potential challenges or safety considerations
        """ 
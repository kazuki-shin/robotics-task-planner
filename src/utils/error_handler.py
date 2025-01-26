import os
import logging
from typing import Optional, Type, Callable
from functools import wraps
import traceback

class RoboticsError(Exception):
    """Base exception class for robotics task planner"""
    pass

class TaskPlanningError(RoboticsError):
    """Raised when task planning fails"""
    pass

class SimulationError(RoboticsError):
    """Raised when simulation operations fail"""
    pass

class RobotControlError(RoboticsError):
    """Raised when robot control operations fail"""
    pass

def setup_logging(log_file: str = 'logs/robotics.log') -> None:
    """
    Configure logging with both file and console handlers
    
    Args:
        log_file: Path to log file
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def error_handler(error_type: Type[Exception], logger: Optional[logging.Logger] = None):
    """Decorator for handling errors in robotics operations"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_type:
                # If it's already the correct error type, just re-raise it
                raise
            except Exception as e:
                log = logger or logging.getLogger(func.__module__)
                log.error(f"Error in {func.__name__}: {str(e)}")
                log.debug(traceback.format_exc())
                raise error_type(str(e)) from e
        return wrapper
    return decorator 
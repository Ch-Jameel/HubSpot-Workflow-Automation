import logging
import traceback
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentError(Exception):
    """Base exception for all agent-related errors"""
    pass

class HubspotError(AgentError):
    """Exception for Hubspot API related errors"""
    pass

class EmailError(AgentError):
    """Exception for email sending related errors"""
    pass

def handle_agent_errors(func):
    """
    Decorator to handle and log agent errors
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AgentError as e:
            logger.error(f"Agent error: {str(e)}")
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            return {"status": "error", "message": "An unexpected error occurred"}
    
    return wrapper
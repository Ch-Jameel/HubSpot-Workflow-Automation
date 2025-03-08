import json
import os

def load_config(config_path):
    """
    configuration variable load from a JSON file
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Check for environment variables that might override config
    if os.environ.get('OPENAI_API_KEY'):
        config['openai']['api_key'] = os.environ.get('OPENAI_API_KEY')
    if os.environ.get('HUBSPOT_API_KEY'):
        config['hubspot']['api_key'] = os.environ.get('HUBSPOT_API_KEY')
    if os.environ.get('EMAIL_PASSWORD'):
        config['email']['password'] = os.environ.get('EMAIL_PASSWORD')
    
    return config

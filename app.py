import os
import sys
import argparse
import logging
from utils.config_loader import load_config
from agents.orchestrator import OrchestratorAgent
from agents.hubspot_agent import HubspotAgent
from agents.email_agent import EmailAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_agents(config_path):
    """
    Set up and connect all agents
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        OrchestratorAgent: Configured orchestrator agent
    """
    # Load configuration
    config = load_config(config_path)
    
    # Initialize agents
    hubspot_agent = HubspotAgent(config)
    email_agent = EmailAgent(config)
    orchestrator = OrchestratorAgent(config)
    
    # Register agents with orchestrator
    orchestrator.register_hubspot_agent(hubspot_agent)
    orchestrator.register_email_agent(email_agent)
    
    return orchestrator

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="HubSpot Workflow Automation")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")
    parser.add_argument("--query", help="User query to process")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    try:
        # Set up agents
        orchestrator = setup_agents(args.config)
        
        if args.interactive:
            # Run in interactive mode
            print("Welcome to HubSpot Workflow Assistant. Type 'exit' to quit.")
            while True:
                query = input("\nEnter your query: ")
                if query.lower() in ["exit", "quit"]:
                    break
                
                print("\nProcessing...")
                result = orchestrator.process_query(query)
                
                if result["status"] == "success":
                    print(f"\nResponse: {result['response']}")
                    if result.get("actions"):
                        print("\nActions performed:")
                        for i, action in enumerate(result["actions"], 1):
                            print(f"{i}. {action['function']}")
                else:
                    print(f"\nError: {result.get('message', 'Unknown error')}")
        
        elif args.query:
            # Process a single query
            result = orchestrator.process_query(args.query)
            
            if result["status"] == "success":
                print(f"Response: {result['response']}")
                if result.get("actions"):
                    print("\nActions performed:")
                    for i, action in enumerate(result["actions"], 1):
                        print(f"{i}. {action['function']}")
            else:
                print(f"Error: {result.get('message', 'Unknown error')}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
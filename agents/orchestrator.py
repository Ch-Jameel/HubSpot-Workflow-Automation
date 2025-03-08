import json
import openai
from utils.error_handler import handle_agent_errors, AgentError

class OrchestratorAgent:
    """
    Global orchestrator agent that delegates tasks to specialized agents
    """
    
    def __init__(self, config):
        """
        Initialize the orchestrator with OpenAI API and register sub-agents
        
        Args:
            config (dict): Configuration dictionary containing API keys
        """
        self.client = openai.Client(api_key=config['openai']['api_key'])
        self.hubspot_agent = None
        self.email_agent = None
        self.assistant_id = None
        
    def register_hubspot_agent(self, hubspot_agent):
        """Register the HubSpot agent"""
        self.hubspot_agent = hubspot_agent
        
    def register_email_agent(self, email_agent):
        """Register the Email agent"""
        self.email_agent = email_agent
    
    @handle_agent_errors
    def create_assistant(self):
        """
        Create an OpenAI Assistant with tools for HubSpot and Email operations
        
        Returns:
            str: ID of the created assistant
        """
        # Define the tools for our assistant
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "check_lead",
                    "description": "Check if a lead exists in HubSpot by email",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "Email address of the lead to check"
                            }
                        },
                        "required": ["email"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_lead",
                    "description": "Create a new lead in HubSpot",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "Email address of the lead"
                            },
                            "firstname": {
                                "type": "string",
                                "description": "First name of the lead"
                            },
                            "lastname": {
                                "type": "string",
                                "description": "Last name of the lead"
                            },
                            "phone": {
                                "type": "string",
                                "description": "Phone number of the lead"
                            },
                            "company": {
                                "type": "string",
                                "description": "Company name of the lead"
                            }
                        },
                        "required": ["email"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_lead",
                    "description": "Update an existing lead in HubSpot",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lead_id": {
                                "type": "string",
                                "description": "ID of the lead to update"
                            },
                            "properties": {
                                "type": "object",
                                "description": "Properties to update for the lead"
                            }
                        },
                        "required": ["lead_id", "properties"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_leads",
                    "description": "Get a list of leads from HubSpot",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of leads to retrieve"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_notification",
                    "description": "Send an email notification",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient": {
                                "type": "string",
                                "description": "Email address of the recipient"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject"
                            },
                            "body": {
                                "type": "string",
                                "description": "Email body content"
                            },
                            "is_html": {
                                "type": "boolean",
                                "description": "Whether the email body contains HTML"
                            }
                        },
                        "required": ["recipient", "subject", "body"]
                    }
                }
            }
        ]
        
        # Create the assistant
        assistant = self.client.beta.assistants.create(
            name="HubSpot Workflow Assistant",
            instructions="""
            You are a workflow assistant that helps users manage leads in HubSpot.
            You can check if leads exist, create new leads, update existing leads, and send email notifications.
            
            When creating or checking leads, always ask for the email address if not provided.
            When creating leads, try to gather as much information as possible (name, company, etc.).
            Always send an email notification after creating or updating a lead.
            
            Be helpful, concise, and professional in your interactions.
            """,
            tools=tools,
            model="gpt-4-turbo-preview"
        )
        
        self.assistant_id = assistant.id
        return assistant.id
    
    @handle_agent_errors
    def process_query(self, user_query):
        """
        Process a user query through the orchestrator
        
        Args:
            user_query (str): User's natural language query
            
        Returns:
            dict: Result of the operation
        """
        if not self.hubspot_agent or not self.email_agent:
            raise AgentError("HubSpot and Email agents must be registered before processing queries")
            
        # Create assistant if it doesn't exist
        if not self.assistant_id:
            self.create_assistant()
            
        # Create a thread
        thread = self.client.beta.threads.create()
        
        # Add the user's message to the thread
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_query
        )
        
        # Run the assistant on the thread
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id
        )
        
        # Process tool calls
        results = []
        while True:
            # Retrieve the run status
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            
            if run.status == "requires_action":
                # Handle tool calls
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Execute the appropriate function based on the function name
                    output = None
                    if function_name == "check_lead":
                        output = self.hubspot_agent.check_lead(function_args["email"])
                    elif function_name == "create_lead":
                        output = self.hubspot_agent.create_lead(function_args)
                        
                        # If lead was created successfully, send notification
                        if output["status"] == "success":
                            notification = self.email_agent.create_lead_notification(function_args)
                            self.email_agent.send_notification(
                                function_args["email"],
                                notification["subject"],
                                notification["body"],
                                notification["is_html"]
                            )
                    elif function_name == "update_lead":
                        output = self.hubspot_agent.update_lead(
                            function_args["lead_id"],
                            function_args["properties"]
                        )
                        
                        # If lead was updated successfully, send notification
                        if output["status"] == "success":
                            notification = self.email_agent.create_update_notification(function_args["properties"])
                            self.email_agent.send_notification(
                                function_args["properties"].get("email", "user@example.com"),
                                notification["subject"],
                                notification["body"],
                                notification["is_html"]
                            )
                    elif function_name == "get_all_leads":
                        limit = function_args.get("limit", 10)
                        output = self.hubspot_agent.get_all_leads(limit)
                    elif function_name == "send_notification":
                        output = self.email_agent.send_notification(
                            function_args["recipient"],
                            function_args["subject"],
                            function_args["body"],
                            function_args.get("is_html", False)
                        )
                    
                    # Add the result to our list and to tool outputs
                    results.append({
                        "function": function_name,
                        "arguments": function_args,
                        "output": output
                    })
                    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(output)
                    })
                
                # Submit the outputs back to the assistant
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            
            elif run.status == "completed":
                # Get the assistant's response
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                
                # Return the last assistant message and the function results
                for message in messages.data:
                    if message.role == "assistant" and message.run_id == run.id:
                        return {
                            "status": "success",
                            "response": message.content[0].text.value,
                            "actions": results
                        }
                
                return {
                    "status": "success",
                    "response": "Query processed successfully",
                    "actions": results
                }
            
            elif run.status in ["failed", "cancelled", "expired"]:
                return {
                    "status": "error",
                    "message": f"Run failed with status: {run.status}",
                    "actions": results
                }
            
            # Wait for a moment before checking again
            import time
            time.sleep(1)
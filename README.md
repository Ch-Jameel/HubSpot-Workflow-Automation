# HubSpot Workflow Automation

This project implements a multi-agent AI system for automating workflows in HubSpot. It uses the OpenAI Assistants API to create a natural language interface for HubSpot lead management and notifications.

## Features

- **Natural Language Interface**: Use plain English to create, update, and check leads in HubSpot
- **Multi-Agent Architecture**:
  - Global Orchestrator Agent: Delegates tasks and manages workflow
  - HubSpot Agent: Interacts with the HubSpot CRM API
  - Email Agent: Sends notifications after successful operations
- **Error Handling**: Robust error handling and logging
- **Interactive Mode**: Command-line interface for interactive use

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/hubspot-workflow-automation.git
cd hubspot-workflow-automation
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Update the json with the actual keys

```json
{
  "openai": {
    "api_key": "YOUR_OPENAI_API_KEY"
  },
  "hubspot": {
    "api_key": "YOUR_HUBSPOT_API_KEY",
    "base_url": "https://api.hubapi.com"
  },
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "password": "YOUR_APP_PASSWORD"
  }
}
```

### 4. Running the Application

Run a single query:

```bash
python app.py --query "Create a lead for john@example.com with the name John Smith from Acme Corp"
```

Run in interactive mode:

```bash
python app.py --interactive
```

## Project Structure

```
project/
├── app.py                   # Main application entry point
├── config.json              # Configuration file for API keys
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py      # Global Orchestrator Agent
│   ├── hubspot_agent.py     # HubSpot Agent for CRM operations
│   └── email_agent.py       # Email Agent for notifications
├── utils/
│   ├── __init__.py
│   ├── config_loader.py     # Utility to load configuration
│   └── error_handler.py     # Common error handling
└── README.md                # Documentation
```

## Error Handling

The application includes comprehensive error handling for:
- API failures
- Missing configuration
- Invalid inputs
- Network issues

All errors are logged for troubleshooting.

## Example Queries

- "Create a new lead with email jane@example.com and name Jane Smith"
- "Check if we have a lead with email john@acme.com"
- "Update the lead for sarah@example.com with a new phone number 555-123-4567"
- "Get a list of our recent leads"

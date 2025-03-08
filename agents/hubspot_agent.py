import requests
from utils.error_handler import HubspotError, handle_agent_errors

class HubspotAgent:
    """
    Agent responsible for interacting with the HubSpot API
    """
    
    def __init__(self, config):
        """
        Initialize the HubSpot agent with configuration
        
        Args:
            config (dict): Configuration dictionary containing HubSpot API credentials
        """
        self.api_key = config['hubspot']['api_key']
        self.base_url = config['hubspot']['base_url']
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    @handle_agent_errors
    def check_lead(self, email):
        """
        Check if a lead exists in HubSpot based on email
        
        Args:
            email (str): Email address to check
            
        Returns:
            dict: Lead information if found, or None
        """
        try:
            # Search for contact by email
            url = f"{self.base_url}/crm/v3/objects/contacts/search"
            payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "email",
                                "operator": "EQ",
                                "value": email
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if data.get('results') and len(data['results']) > 0:
                return {
                    "status": "success",
                    "found": True,
                    "lead": data['results'][0]
                }
            else:
                return {
                    "status": "success",
                    "found": False
                }
                
        except requests.exceptions.RequestException as e:
            raise HubspotError(f"Failed to check lead: {str(e)}")
    
    @handle_agent_errors
    def create_lead(self, properties):
        """
        Create a new lead in HubSpot
        
        Args:
            properties (dict): Lead properties, must include at least email
            
        Returns:
            dict: Created lead information
        """
        if 'email' not in properties:
            raise HubspotError("Email is required to create a lead")
            
        try:
            # Create new contact
            url = f"{self.base_url}/crm/v3/objects/contacts"
            payload = {
                "properties": properties
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            return {
                "status": "success",
                "lead": response.json()
            }
                
        except requests.exceptions.RequestException as e:
            raise HubspotError(f"Failed to create lead: {str(e)}")
    
    @handle_agent_errors
    def update_lead(self, lead_id, properties):
        """
        Update an existing lead in HubSpot
        
        Args:
            lead_id (str): ID of the lead to update
            properties (dict): Lead properties to update
            
        Returns:
            dict: Updated lead information
        """
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/{lead_id}"
            payload = {
                "properties": properties
            }
            
            response = requests.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            return {
                "status": "success",
                "lead": response.json()
            }
                
        except requests.exceptions.RequestException as e:
            raise HubspotError(f"Failed to update lead: {str(e)}")
    
    @handle_agent_errors
    def get_all_leads(self, limit=10):
        """
        Get a list of leads from HubSpot
        
        Args:
            limit (int): Maximum number of leads to retrieve
            
        Returns:
            dict: List of leads
        """
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts?limit={limit}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return {
                "status": "success",
                "leads": response.json().get('results', [])
            }
                
        except requests.exceptions.RequestException as e:
            raise HubspotError(f"Failed to get leads: {str(e)}")
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.error_handler import EmailError, handle_agent_errors

class EmailAgent:
    """
    Agent responsible for sending email notifications
    """
    
    def __init__(self, config):
        """
        Initialize the Email agent with configuration
        
        Args:
            config (dict): Configuration dictionary containing email credentials
        """
        self.smtp_server = config['email']['smtp_server']
        self.smtp_port = config['email']['smtp_port']
        self.sender_email = config['email']['sender_email']
        self.password = config['email']['password']
    
    @handle_agent_errors
    def send_notification(self, recipient, subject, body, is_html=False):
        """
        Send an email notification
        
        Args:
            recipient (str): Email address of the recipient
            subject (str): Email subject
            body (str): Email body content
            is_html (bool): Whether the email body contains HTML
            
        Returns:
            dict: Result of the operation
        """
        try:
            # Create a multipart message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient
            message["Subject"] = subject
            
            # Add body to email
            content_type = "html" if is_html else "plain"
            message.attach(MIMEText(body, content_type))
            
            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.sender_email, self.password)
                server.send_message(message)
            
            return {
                "status": "success",
                "message": f"Email sent to {recipient}"
            }
            
        except Exception as e:
            raise EmailError(f"Failed to send email: {str(e)}")
    
    def create_lead_notification(self, lead_data):
        """
        Create a formatted notification for a new lead
        
        Args:
            lead_data (dict): Lead information
            
        Returns:
            dict: Subject and body for the email
        """
        email = lead_data.get("email", "Unknown")
        name = lead_data.get("firstname", "") + " " + lead_data.get("lastname", "")
        name = name.strip() or "Unknown"
        
        subject = f"New Lead Created: {name}"
        
        body = f"""
        <html>
        <body>
            <h2>New Lead Created in HubSpot</h2>
            <p>A new lead has been successfully created with the following details:</p>
            <ul>
                <li><strong>Name:</strong> {name}</li>
                <li><strong>Email:</strong> {email}</li>
            </ul>
            <p>You can log into HubSpot to view more details and follow up.</p>
        </body>
        </html>
        """
        
        return {
            "subject": subject,
            "body": body,
            "is_html": True
        }
    
    def create_update_notification(self, lead_data):
        """
        Create a formatted notification for an updated lead
        
        Args:
            lead_data (dict): Lead information
            
        Returns:
            dict: Subject and body for the email
        """
        email = lead_data.get("email", "Unknown")
        name = lead_data.get("firstname", "") + " " + lead_data.get("lastname", "")
        name = name.strip() or "Unknown"
        
        subject = f"Lead Updated: {name}"
        
        body = f"""
        <html>
        <body>
            <h2>Lead Updated in HubSpot</h2>
            <p>A lead has been successfully updated with the following details:</p>
            <ul>
                <li><strong>Name:</strong> {name}</li>
                <li><strong>Email:</strong> {email}</li>
            </ul>
            <p>You can log into HubSpot to view more details and follow up.</p>
        </body>
        </html>
        """
        
        return {
            "subject": subject,
            "body": body,
            "is_html": True
        }
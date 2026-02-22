import os
import time
import datetime
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
import logging

# Setup logging
os.makedirs('Logs', exist_ok=True)
logging.basicConfig(filename=f'Logs/gmail_watcher_{datetime.datetime.now().strftime("%Y%m%d")}.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.labels']

def get_gmail_service():
    """Authenticate and return Gmail API service"""
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                'credentials.json', SCOPES)
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            auth_url, _ = flow.authorization_url(prompt='consent')
            print('Please visit this URL to authorize:', auth_url)
            code = input('Enter the authorization code: ')
            flow.fetch_token(code=code)
            creds = flow.credentials
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_email_content(message):
    """Extract email content from message object"""
    payload = message['payload']
    headers = {header['name'].lower(): header['value'] for header in payload.get('headers', [])}
    
    # Extract subject and sender
    subject = headers.get('subject', 'No Subject')
    sender = headers.get('from', 'Unknown Sender')
    
    # Extract body content
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    else:
        if 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    return {
        'subject': subject,
        'sender': sender,
        'body': body
    }

def create_email_markdown(email_data, message_id):
    """Create markdown file for email in Needs_Action folder"""
    os.makedirs('Needs_Action', exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Needs_Action/[{timestamp}]_{message_id}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Email from {email_data['sender']}\n\n")
        f.write(f"## Subject: {email_data['subject']}\n\n")
        f.write("## Message Body:\n\n")
        f.write(email_data['body'].replace('\n', '\n\n'))
    
    logging.info(f"Created markdown file for email {message_id}")
    return filename

def save_processed_id(message_id):
    """Save processed email ID to avoid duplicates"""
    with open('processed_ids.txt', 'a') as f:
        f.write(f"{message_id}\n")

def is_email_processed(message_id):
    """Check if email has been processed before"""
    if not os.path.exists('processed_ids.txt'):
        return False
    
    with open('processed_ids.txt', 'r') as f:
        return message_id in f.read()

def main():
    """Main function to check for unread important emails"""
    service = get_gmail_service()
    
    while True:
        try:
            # Get unread important emails
            result = service.users().messages().list(
                userId='me', 
                q='is:unread is:important', 
                maxResults=50
            ).execute()
            
            messages = result.get('messages', [])
            
            if not messages:
                logging.info("No new important unread emails found")
                time.sleep(120)  # Wait 2 minutes before next check
                continue
            
            for message in messages:
                message_id = message['id']
                
                if is_email_processed(message_id):
                    continue
                    
                # Get full message details
                msg = service.users().messages().get(userId='me', id=message_id).execute()
                email_content = get_email_content(msg)
                
                # Create markdown file
                create_email_markdown(email_content, message_id)
                save_processed_id(message_id)
                
                logging.info(f"Processed email {message_id} from {email_content['sender']}")
                
            time.sleep(120)  # Wait 2 minutes before next check
            
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            time.sleep(60)  # Wait 1 minute before retrying after error

if __name__ == '__main__':
    main()

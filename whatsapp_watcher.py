import os
import time
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

# Configuration
SESSION_DIR = os.path.expanduser("~/AI_Employee_Vault/whatsapp_session")
NEEDS_ACTION_DIR = "Needs_Action"
LOGS_DIR = "Logs"
KEYWORDS = ["urgent", "invoice", "payment", "help", "asap"]
CHECK_INTERVAL = 30  # seconds

def initialize_browser():
    """Initialize browser with session storage"""
    os.makedirs(SESSION_DIR, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        # Load saved session if it exists
        if os.path.exists(os.path.join(SESSION_DIR, "storage.json")):
            context.storage_state(path=os.path.join(SESSION_DIR, "storage.json"))
        
        page = context.new_page()
        page.goto("https://web.whatsapp.com")
        
        # Save session
        context.storage_state(path=os.path.join(SESSION_DIR, "storage.json"))
        return page, context, browser

def log_activity(message):
    """Log activity to timestamped log file"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, f"whatsapp_watcher_{datetime.now().strftime('%Y%m%d')}.log")
    
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")

def create_action_file(contact_name, message_text, timestamp):
    """Create markdown file in Needs_Action directory"""
    filename = f"[{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}]_{contact_name.replace(' ', '_')}.md"
    filepath = os.path.join(NEEDS_ACTION_DIR, filename)
    
    content = f"""# WhatsApp Message Alert

**Contact:** {contact_name}
**Timestamp:** {timestamp}
**Keywords Found:** {', '.join(find_keywords(message_text))}
**Message:** 

import os
import re
import time
import datetime
from playwright.sync_api import sync_playwright

VAULT_PATH = os.path.expanduser("~/AI_Employee_Vault")
NEEDS_ACTION = os.path.join(VAULT_PATH, "Needs_Action")
LOGS = os.path.join(VAULT_PATH, "Logs")
SESSION_PATH = os.path.join(VAULT_PATH, "whatsapp_session")
CHECK_INTERVAL = 30
KEYWORDS = ['urgent', 'invoice', 'payment', 'help', 'asap']

os.makedirs(NEEDS_ACTION, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)
os.makedirs(SESSION_PATH, exist_ok=True)

def log_activity(message):
    today = datetime.datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(LOGS, f"whatsapp_{today}.log")
    timestamp = datetime.datetime.now().isoformat()
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - {message}\n")
    print(f"{timestamp} - {message}")

def create_action_file(contact, message, timestamp):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"WHATSAPP_{ts}_{contact[:20]}.md"
    filepath = os.path.join(NEEDS_ACTION, filename)
    content = "---\ntype: whatsapp\ncontact: " + contact + "\ntimestamp: " + timestamp + "\nstatus: pending\n---\n\n"
    content += "## WhatsApp Message Alert\n\n"
    content += "**From:** " + contact + "\n\n"
    content += "**Message:** " + message + "\n\n"
    content += "## Suggested Actions\n- [ ] Reply to message\n- [ ] Take required action\n"
    with open(filepath, "w") as f:
        f.write(content)
    log_activity(f"Created action file: {filename}")

def find_keywords(text):
    return [kw for kw in KEYWORDS if re.search(rf'\b{kw}\b', text.lower())]

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            SESSION_PATH, headless=True
        )
        page = browser.new_page()
        page.goto("https://web.whatsapp.com")
        print("Scan QR code if needed. Waiting 30 seconds...")
        page.wait_for_timeout(30000)
        log_activity("WhatsApp Watcher started")
        try:
            while True:
                try:
                    unread = page.query_selector_all('[aria-label*="unread"]')
                    for chat in unread:
                        text = chat.inner_text().lower()
                        keywords_found = find_keywords(text)
                        if keywords_found:
                            create_action_file("WhatsApp Contact", text, datetime.datetime.now().isoformat())
                    log_activity(f"Checked messages, found {len(unread)} unread")
                except Exception as e:
                    log_activity(f"Error: {str(e)}")
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            log_activity("Watcher stopped")
        browser.close()

if __name__ == "__main__":
    main()

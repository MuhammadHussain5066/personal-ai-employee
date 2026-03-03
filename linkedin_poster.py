import os
import datetime
import webbrowser
import urllib.parse

VAULT = os.path.expanduser("~/AI_Employee_Vault")
LOGS = os.path.join(VAULT, "Logs")
PENDING = os.path.join(VAULT, "Pending_Approval")
os.makedirs(LOGS, exist_ok=True)
os.makedirs(PENDING, exist_ok=True)

def log(msg):
    today = datetime.datetime.now().strftime("%Y%m%d")
    with open(f"{LOGS}/linkedin_{today}.log", 'a') as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")
    print(msg)

def post_to_linkedin(post_text):
    # Create approval file
    approval = os.path.join(PENDING, f"LINKEDIN_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(approval, 'w') as f:
        f.write(f"---\ntype: linkedin_post\nstatus: pending\n---\n\n## Post Content\n{post_text}\n\n## To Post\nURL will open in browser.\n")
    log(f"Approval file created!")

    confirm = input("Type YES to open LinkedIn and post: ")
    if confirm.upper() == "YES":
        encoded = urllib.parse.quote(post_text)
        url = f"https://www.linkedin.com/sharing/share-offsite/?url=https://example.com&summary={encoded}"
        os.system(f"cmd.exe /c start '{url}'")
        log(f"LinkedIn opened in browser!")
        
        # Move to done
        done = os.path.join(VAULT, "Done", f"LINKEDIN_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(done, 'w') as f:
            f.write(f"---\ntype: linkedin_post\nstatus: posted\n---\n\n## Posted Content\n{post_text}\n")
        log("Task moved to Done!")
    else:
        log("Cancelled!")

if __name__ == "__main__":
    post_text = input("Enter your LinkedIn post: ")
    post_to_linkedin(post_text)

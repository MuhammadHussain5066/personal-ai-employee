import os
import shutil
import datetime
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VAULT = os.path.expanduser("~/AI_Employee_Vault")
NEEDS_ACTION = os.path.join(VAULT, "Needs_Action")
PLANS = os.path.join(VAULT, "Plans")
PENDING = os.path.join(VAULT, "Pending_Approval")
DONE = os.path.join(VAULT, "Done")
LOGS = os.path.join(VAULT, "Logs")
DASHBOARD = os.path.join(VAULT, "Dashboard.md")

for d in [PLANS, PENDING, DONE, LOGS]:
    os.makedirs(d, exist_ok=True)

def log(msg):
    today = datetime.datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(LOGS, f"ai_processor_{today}.log")
    timestamp = datetime.datetime.now().isoformat()
    line = f"[{timestamp}] {msg}\n"
    with open(log_file, 'a') as f:
        f.write(line)
    print(line.strip())

def analyze(client, content):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": f"Analyze this message and tell me:\n1. What action is needed\n2. Does it need human approval? (Yes/No)\n3. Draft a brief response\n\nMessage:\n{content[:500]}"}],
        max_tokens=500
    )
    return response.choices[0].message.content

def update_dashboard(processed, pending):
    with open(DASHBOARD, 'r') as f:
        content = f.read()
    content = content.replace(
        f"- Last Updated:", 
        f"- Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d')} |"
    )
    with open(DASHBOARD, 'w') as f:
        f.write(content)

def main():
    client = Groq(api_key=GROQ_API_KEY)
    files = [f for f in os.listdir(NEEDS_ACTION) if f.endswith('.md')]
    log(f"Found {len(files)} files to process")
    
    processed = 0
    pending = 0
    
    for filename in files:
        filepath = os.path.join(NEEDS_ACTION, filename)
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            log(f"Processing: {filename}")
            analysis = analyze(client, content)
            
            # Save plan
            plan_path = os.path.join(PLANS, f"PLAN_{filename}")
            with open(plan_path, 'w') as f:
                f.write(f"# Plan for {filename}\n\n")
                f.write(f"## Original Content\n{content}\n\n")
                f.write(f"## AI Analysis\n{analysis}\n")
            
            # Move file
            if "yes" in analysis.lower() and "approval" in analysis.lower():
                shutil.move(filepath, os.path.join(PENDING, filename))
                log(f"Needs approval: {filename}")
                pending += 1
            else:
                shutil.move(filepath, os.path.join(DONE, filename))
                log(f"Done: {filename}")
                processed += 1
                
        except Exception as e:
            log(f"Error: {filename} - {str(e)}")
    
    log(f"Complete! Processed: {processed}, Pending: {pending}")

if __name__ == "__main__":
    main()

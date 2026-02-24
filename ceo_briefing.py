import os
import datetime
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
VAULT = os.path.expanduser("~/AI_Employee_Vault")
BRIEFINGS = os.path.join(VAULT, "Briefings")
os.makedirs(BRIEFINGS, exist_ok=True)

def get_stats():
    done = len(os.listdir(os.path.join(VAULT, "Done")))
    pending = len(os.listdir(os.path.join(VAULT, "Pending_Approval")))
    plans = len(os.listdir(os.path.join(VAULT, "Plans")))
    return done, pending, plans

def generate_briefing(done, pending, plans):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = f"""Generate a Monday Morning CEO Briefing report with:
- Emails processed: {done}
- Pending approvals: {pending}  
- Plans created: {plans}

Include: Executive Summary, Key Actions Needed, Recommendations.
Keep it concise and professional."""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content

def main():
    done, pending, plans = get_stats()
    print(f"Stats - Done: {done}, Pending: {pending}, Plans: {plans}")
    
    briefing = generate_briefing(done, pending, plans)
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(BRIEFINGS, f"{today}_Monday_Briefing.md")
    
    with open(filename, 'w') as f:
        f.write(f"# Monday Morning CEO Briefing - {today}\n\n")
        f.write(briefing)
    
    print(f"Briefing saved: {filename}")
    print("\n" + briefing)

if __name__ == "__main__":
    main()

# 🤖 Personal AI Employee - Bronze Tier

## Hackathon: Personal AI Employee Hackathon 0

### What is this?
A local-first AI Employee using Aider + Groq + Qwen that monitors files and takes actions automatically.

### Tech Stack
- **AI:** Aider + Groq (Qwen3-32b)
- **OS:** Ubuntu (WSL2)
- **Watcher:** Python + Watchdog

### Setup
```bash
pip3 install aider-chat watchdog markdown pyyaml
export GROQ_API_KEY="your-key"
python3 file_watcher.py
```

### Folder Structure
- `/Needs_Action` - New tasks for AI
- `/Plans` - AI generated plans  
- `/Done` - Completed tasks
- `/Logs` - Audit logs
- `/Pending_Approval` - Waiting for human approval

### Tier
🥉 Bronze - Foundation Complete

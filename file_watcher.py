import os
import time
import watchdog.observers
import watchdog.events
from datetime import datetime
import yaml
import markdown

WATCHED_FOLDER = os.path.expanduser("~/AI_Employee_Vault/drop_here")
ACTION_FOLDER = os.path.expanduser("~/AI_Employee_Vault/Needs_Action")
PROCESSED_FOLDER = os.path.expanduser("~/AI_Employee_Vault/Processed")

class FileDropHandler(watchdog.events.FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            self.create_action_marker(event.src_path)
    
    def create_action_marker(self, file_path):
        """Create markdown marker file in Needs_Action folder"""
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            timestamp = datetime.now().isoformat()
            marker_name = f"[{timestamp.split('.')[0]}]_{file_name}.md"
            marker_path = os.path.join(ACTION_FOLDER, marker_name)
            
            # Create directory structure if needed
            os.makedirs(ACTION_FOLDER, exist_ok=True)
            
            # Create markdown content with YAML front matter
            content = f"""---
file_path: {file_path}
file_size: {file_size}
timestamp: {timestamp}
---
File {file_name} was dropped in the monitored folder at {timestamp}
"""
            with open(marker_path, 'w') as f:
                f.write(content)
                
            print(f"Created marker file: {marker_path}")
            
        except Exception as e:
            print(f"Error creating marker file: {str(e)}")

def main():
    # Create watched directories if they don't exist
    os.makedirs(WATCHED_FOLDER, exist_ok=True)
    os.makedirs(ACTION_FOLDER, exist_ok=True)
    
    observer = watchdog.observers.Observer()
    observer.schedule(FileDropHandler(), path=WATCHED_FOLDER, recursive=False)
    observer.start()
    
    print(f"Watching {WATCHED_FOLDER} for file drops...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()

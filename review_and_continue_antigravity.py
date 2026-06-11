#!/usr/bin/env python3
import json
import subprocess
import sys
import time

def get_last_assistant_message(transcript_path):
    time.sleep(0.5)
    for _ in range(5):
        try:
            with open(transcript_path) as f:
                lines = f.readlines()
            if not lines:
                time.sleep(0.5)
                continue
            
            # Find the most recent message from MODEL/PLANNER_RESPONSE
            for line in reversed(lines):
                try:
                    entry = json.loads(line.strip())
                except:
                    continue
                if entry.get("source") == "MODEL" and entry.get("type") == "PLANNER_RESPONSE":
                    content = entry.get("content")
                    if content and isinstance(content, str) and content.strip():
                        return content.strip()
            time.sleep(0.5)
        except Exception as e:
            time.sleep(0.5)
    return "Antigravity Task Completed (Stop Hook triggered)."

def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception as e:
        print(f"Antigravity Hook Error: {e}", file=sys.stderr)
        sys.exit(1)
        
    transcript_path = input_data.get("transcriptPath") or input_data.get("transcript_path")
    if not transcript_path:
        sys.exit(0)
        
    last_message = get_last_assistant_message(transcript_path)
    
    # Run hitl-cli notify-completion using the absolute result bin path
    try:
        result = subprocess.run(
            ["/Users/slaser79/lab/hitl/hitl-cli/result/bin/hitl-cli", "notify-completion", "--summary", last_message],
            check=True,
            capture_output=True,
            text=True,
            timeout=900
        )
        stdout = result.stdout
    except Exception as e:
        print(f"Antigravity Hook notify-completion failed: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Extract response
    prefix = "✅ Human response received:"
    user_response = stdout.strip()
    if prefix in stdout:
        user_response = stdout.split(prefix, 1)[1].strip()
        
    if user_response == "YOU ARE DONE":
        sys.exit(0)
    else:
        output = {
            "decision": "block",
            "reason": user_response
        }
        print(json.dumps(output))
        sys.exit(0)

if __name__ == "__main__":
    main()

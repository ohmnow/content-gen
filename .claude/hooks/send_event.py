#!/usr/bin/env python3
"""
Claude Code Hook: Send Event to Observability Server

This hook forwards Claude Code events to the observability dashboard.
Automatically called by Claude Code when configured in .claude/settings.json
"""

import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

# Configuration
OBSERVABILITY_SERVER_URL = "http://localhost:4000/events"
TIMEOUT_SECONDS = 2


def send_event(hook_type: str, event_data: dict) -> None:
    """Send event to observability server (fails silently)."""
    try:
        # Extract useful information
        session_id = event_data.get("sessionId", "unknown")
        
        # Build payload
        payload = {
            "source_app": "big-three-agents: Claude Code Hook",
            "session_id": session_id,
            "hook_event_type": hook_type,
            "payload": event_data,
            "timestamp": int(datetime.now().timestamp() * 1000),
        }
        
        # Add summary based on hook type
        if hook_type == "PreToolUse":
            tool_name = event_data.get("toolInput", {}).get("toolName", "unknown")
            payload["summary"] = f"About to use tool: {tool_name}"
        elif hook_type == "PostToolUse":
            tool_name = event_data.get("toolInput", {}).get("toolName", "unknown")
            payload["summary"] = f"Completed tool: {tool_name}"
        elif hook_type == "SessionStop":
            payload["summary"] = "Claude Code session stopped"
            # Include chat transcript if available
            if "chatTranscript" in event_data:
                payload["payload"]["chat_transcript"] = event_data["chatTranscript"]
        
        # Send request
        req = urllib.request.Request(
            OBSERVABILITY_SERVER_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "ClaudeCodeHook/1.0",
            },
        )
        
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            if response.status != 200:
                print(
                    f"[Hook] Observability server returned {response.status}",
                    file=sys.stderr,
                )
    
    except urllib.error.URLError as e:
        # Silently fail if observability server is not running
        pass
    except Exception as e:
        print(f"[Hook] Error sending event: {e}", file=sys.stderr)


def main():
    """Main hook entry point."""
    if len(sys.argv) < 2:
        print("Usage: send_event.py <hook_type>", file=sys.stderr)
        sys.exit(1)
    
    hook_type = sys.argv[1]
    
    # Read event data from stdin
    try:
        event_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"[Hook] Failed to parse JSON from stdin: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Send the event
    send_event(hook_type, event_data)
    
    # Return success
    sys.exit(0)


if __name__ == "__main__":
    main()



# Claude Code Configuration

This directory contains Claude Code hooks for multi-agent observability.

## How It Works

When Claude Code agents work in this directory, they automatically trigger hooks defined in `settings.json`. These hooks forward events to the observability dashboard for real-time monitoring.

## Files

- **`settings.json`** - Claude Code hook configuration
- **`hooks/send_event.py`** - Python script that sends events to the observability server

## Event Types

The following hooks are configured:

- **PreToolUse** - Triggered before a tool is used
- **PostToolUse** - Triggered after a tool completes
- **Notification** - Triggered when Claude sends a notification
- **SessionStop** - Triggered when a Claude Code session ends

## Observability Server

Events are sent to: `http://localhost:4000/events`

The observability dashboard runs on: `http://localhost:3000`

To start the observability server:
```bash
cd ~/path/to/claude-code-hooks-multi-agent-observability
npm install && npm run dev
```

## Testing

To verify the hooks are working:

1. Start the observability server
2. Open the dashboard at http://localhost:3000
3. Start the voice agent and create a Claude Code agent
4. Watch events appear in the dashboard in real-time

## Troubleshooting

**No events appearing?**
- Check if the observability server is running on port 4000
- Look for errors in Claude Code's output
- Verify the hook script is executable: `ls -la hooks/send_event.py`

**Hook errors?**
- The hook fails silently if the server is not running (by design)
- Check stderr for any error messages from the hook script



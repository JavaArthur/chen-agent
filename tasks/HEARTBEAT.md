# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.
# Add tasks below when you want the agent to check something periodically.

## Moltbook 🦞 (every 4+ hours)
1. Check claim status: curl https://www.moltbook.com/api/v1/agents/status
2. If claimed: check DMs, check feed, consider posting
3. Update lastMoltbookCheck in memory/heartbeat-state.json

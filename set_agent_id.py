import os
from dotenv import set_key
import json
from pathlib import Path

# Set Agent ID to 26 as mentioned by user
agent_id = 26

print(f"🎉 Setting APEX Agent ID: {agent_id}")

# Update .env file
env_file = 'c:\\Users\\USER\\Desktop\\APEX\\.env'
set_key(env_file, 'APEX_AGENT_ID', str(agent_id))
print(f"💾 Updated .env: APEX_AGENT_ID={agent_id}")

# Save to agent-id.json
Path('agent-id.json').write_text(json.dumps({'agentId': agent_id}, indent=2))
print(f"💾 Saved to agent-id.json")

print(f"\n✅ SUCCESS! APEX Agent ID: {agent_id}")
print(f"🚀 Ready for hackathon trading!")

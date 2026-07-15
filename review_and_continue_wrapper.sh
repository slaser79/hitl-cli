#!/bin/bash
# Set HITL_API_KEY for correct agent attribution
export HITL_API_KEY=mcp_pk_jf47fiJt6QknNHchh9xeLDHkfDx2q4p8ZNiqtbso5g0

# Set IS_ANTIGRAVITY to let the hook know it's running under Antigravity
export IS_ANTIGRAVITY=1

# Read stdin into a variable so we can inspect it before forwarding
INPUT=$(cat)

# Check if the agent is fully idle (no background tasks running).
# When fullyIdle=false, let the agent stop — the system's reactive wakeup
# will resume it when background tasks complete. This avoids wasting tokens
# on forced re-entry into the execution loop.
#
# NOTE: jq's // (alternative) operator treats boolean false as falsy,
# so we must use 'tostring' instead of '// "true"' to correctly convert
# the boolean to a string for bash comparison.
FULLY_IDLE=$(echo "$INPUT" | jq -r '.fullyIdle | tostring')

if [ "$FULLY_IDLE" = "false" ]; then
  # Allow the stop — reactive wakeup will handle background task completion
  echo '{"decision": "allow", "reason": ""}'
  exit 0
fi

# Agent is fully idle — forward to the HITL review binary for phone notification
echo "$INPUT" | tee /Users/slaser79/lab/hitl/hitl-cli/debug_stdin.json | /Users/slaser79/lab/hitl/hitl-cli/result/bin/hitl-hook-review-and-continue --antigravity

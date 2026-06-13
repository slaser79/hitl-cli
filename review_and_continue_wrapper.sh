#!/bin/bash
# Set HITL_API_KEY for correct agent attribution
export HITL_API_KEY=mcp_pk_jf47fiJt6QknNHchh9xeLDHkfDx2q4p8ZNiqtbso5g0

# Set IS_ANTIGRAVITY to let the hook know it's running under Antigravity
export IS_ANTIGRAVITY=1

# Capture incoming JSON and run the rebuilt compiled stop hook binary
tee /Users/slaser79/lab/hitl/hitl-cli/debug_stdin.json | /Users/slaser79/lab/hitl/hitl-cli/result/bin/hitl-hook-review-and-continue --antigravity

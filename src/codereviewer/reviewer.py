import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, ToolUseBlock, ResultMessage, TextBlock
import os


if os.path.exists("result.md"):
    os.remove("result.md")
cwd = os.getcwd()

async def review_changes():
    async for message in query(
prompt=f"""
Working directory: /Users/rmahshie/Downloads/projects/lawsearchprod (repo root)

Review changes from commit 0071e88. Write findings to ./result.md (in repo root).
You have exactly 6 turns to complete this task and write to result.md immediately.
Steps:
1. `git diff -U55 0071e88` (35 lines context included)
2. For modified functions, `grep -rn "function_name" --include="*.py"` to find callers
3. Write critical issues only to ./result.md
Do NOT:
- List files or explore structure
- Read entire files
- Include non-critical observations
Output format (max 45 lines):
## Critical Issues
- [Issue]: [File:Line] - [Impact]
""",
        options=ClaudeAgentOptions(
            model="claude-haiku-4-5-20251001",
            system_prompt="You are a fast code reviewer. Complete reviews in 3 tool calls maximum. Do not over-investigate. Write findings immediately after seeing the diff.",
            allowed_tools=["Write", "Grep", "Bash"],
            permission_mode="acceptEdits",
            max_turns=6,
            cwd="/Users/rmahshie/Downloads/projects/lawsearchprod"
        )
    ):
        if hasattr(message, 'data'):
            print(f"Session ID: {message.data.get('session_id')}")
            print(f"Model: {message.data.get('model')}")

        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Response: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"Tool used: {block.name}")
                    print(f"Tool input: {block.input}")
        
        if isinstance(message, ResultMessage):
                    print(f"Result: {message.result}")
                    if hasattr(message, 'usage'):
                        print(f"Usage: {message.usage}")
                        print(f"Total Turns: {message.num_turns}")
                    if hasattr(message, 'total_cost_usd'):
                        print(f"Total Cost: {message.total_cost_usd}")


asyncio.run(review_changes())
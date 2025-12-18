from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, ToolUseBlock, ResultMessage, TextBlock
import os
from .prompts import get_complex_review_prompt, get_simple_review_prompt
from .models import ReviewOutput
from langchain_openai import ChatOpenAI


async def review_commplex_changes(diff: str, summary: str) -> dict:
    """
        Reviews the changes in a pr diff that are complex and require navigating the codebase.

        Args:
            diff: The diff of the pull request.
            summary: The summary of the changes.

        Returns:
            A dictionary containing the issues and has_critical_issues.
    """
    cwd = os.getcwd()
    async for message in query(
        prompt=get_complex_review_prompt(cwd, diff, summary),
        options=ClaudeAgentOptions(
            model="claude-haiku-4-5-20251001",
            system_prompt="You are a fast code reviewer. Complete reviews with minimum tool calls. Do not over-investigate. Write findings immediately after seeing the diff.",
            allowed_tools=["Write", "Grep", "Bash"],
            permission_mode="acceptEdits",
            max_turns=6,
            cwd=cwd
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


async def review_simple_changes(diff: str, summary: str) -> dict:
    """
        Reviews the changes in a pull request diff.
        Designed for small changes that are easy to review.

        Args:
            diff: The diff of the pull request.
            summary: The summary of the changes.

        Returns:
            A dictionary containing the issues and has_critical_issues.
    """
    llm = ChatOpenAI(model="gpt-5-mini", temperature=0)
    structured_llm = llm.with_structured_output(ReviewOutput)
    prompt = get_simple_review_prompt(diff, summary)
    response = structured_llm.invoke(prompt)
    return {
        "issues": response.issues,
        "has_critical_issues": response.has_critical_issues
    }
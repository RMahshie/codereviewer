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
            A dictionary containing the issues.
    """
    cwd = os.getcwd()
    review_file = "/tmp/review.json"
    
    # Remove any existing review file
    if os.path.exists(review_file):
        os.remove(review_file)
    
    async for message in query(
        prompt=get_complex_review_prompt(cwd, diff, summary),
        options=ClaudeAgentOptions(
            model="claude-haiku-4-5-20251001",
            system_prompt="You are a fast code reviewer. Investigate the code, then use the Write tool to save your findings to /tmp/review.json in JSON format. YOU MUST FOLLOW THE TURN LIMIT INSTRUCTIONS.",
            allowed_tools=["Write", "Grep", "Bash", "Read"],
            permission_mode="acceptEdits",
            max_turns=25,
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
    
    # Read the review file written by Claude
    raw_review = None
    if os.path.exists(review_file):
        with open(review_file, 'r') as f:
            raw_review = f.read()
        print(f"✅ Read review from {review_file}")
    else:
        print(f"⚠️ Warning: {review_file} not found, Claude may not have written findings")
        raw_review = '{"issues": []}'
    
    # Parse Claude's JSON output with GPT-5-mini for validation
    llm = ChatOpenAI(model="gpt-5-mini")
    structured_llm = llm.with_structured_output(ReviewOutput)
    
    prompt = f"""Extract and validate the code review issues from this JSON output.
If the JSON is malformed, do your best to extract the issues:

{raw_review}

Return in the required structured format."""
    
    response = structured_llm.invoke(prompt)
    
    return {
        "issues": [issue.model_dump() for issue in response.issues]
    }


async def review_simple_changes(diff: str, summary: str) -> dict:
    """
        Reviews the changes in a pull request diff.
        Designed for small changes that are easy to review.

        Args:
            diff: The diff of the pull request.
            summary: The summary of the changes.

        Returns:
            A dictionary containing the issues.
    """
    llm = ChatOpenAI(model="gpt-5-mini")
    structured_llm = llm.with_structured_output(ReviewOutput)
    prompt = get_simple_review_prompt(diff, summary)
    response = structured_llm.invoke(prompt)
    return {
        "issues": [issue.model_dump() for issue in response.issues]
    }
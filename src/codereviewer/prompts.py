"""
Prompts for the code review and summarization.
"""

def get_complex_review_prompt(cwd: str, diff: str, summary: str) -> str:
    return f"""
Working directory: {cwd} (repo root)
<instructions>
Review changes from the diff. The summary describes the intent of the changes at a high level. 
Focus on finding issues not covered in the summary and high level flow breaks that are critical.
Return a list of critical observations that need to be addressed.
You have exactly 8 turns to complete this task and return the results immediately.
</instructions>

</steps>
Steps:
1. Review the diff for issues within each file.
2. For functions that are added/modified, grep for callers to check upstream impact.
3. For functions being called, grep to verify they exist and signatures match
3. Return a list of critical observations that need to be addressed.
</steps>

<summary>
{summary}
</summary>

<diff>
{diff}
</diff>

<requirements>
Do NOT:
- List files or explore structure
- Read entire files
- Include non-critical observations
</requirements>

<output format>
Output ONLY valid JSON in this exact format (no markdown, no explanation text):
{{
  "issues": [
    {{
      "category": "Security|Logic|Performance|Maintainability",
      "file": "path/to/file.py",
      "line": 123,
      "issue": "Brief description of the issue",
      "impact": "Why this matters / what could go wrong",
      "recommendation": "How to fix it"
    }}
  ]
}}

If no critical issues found, return:
{{
  "issues": []
}}
</output format>
"""

def get_simple_review_prompt(diff: str, summary: str) -> str:
    return f"""
Review this pull request diff.

## Summary
{summary}

## Diff
{diff}

Report issues that would cause bugs, crashes, security vulnerabilities, or significant maintainability problems.

Examples of what to report:
- Security: auth.py:14 - SQL injection via f-string: user input directly in query
- Logic: utils.py:23 - Division without zero check will crash
- Complexity: service.py:45 - 150-line function with 8 nested conditions, hard to maintain

Examples of what NOT to report:
- "Variable 'x' could be more descriptive" (minor naming)
- "Consider adding type hints" (enhancement, not issue)
- "Unused import" (unless it indicates a missing implementation)

If no real issues, say "No issues found."

Format:
- [Category]: [File:Line] - [Issue and why it matters]
"""


def get_summarizer_prompt(diff: str) -> str:
    return f"""
Summarize this pull request diff.

## Diff
{diff}

Provide:
1. A 2-3 sentence overview of what this PR does
2. Data flow changes (if any): how data moves differently through the system now
3. Key files affected and why they matter

Keep it concise. This summary will be used as context for a detailed code review.
"""
"""
Quality evaluation tests using LLM-as-a-Judge pattern.
Evaluates if the review output is actually good quality.

Setup: Run `pip install -e .` from the project root before running tests.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from codereviewer.reviewer import review_simple_changes
from codereviewer.summarizer import summarize_changes
from langchain_openai import ChatOpenAI


def load_sample_diff(filename: str) -> str:
    """Load a sample diff from test_data directory."""
    test_data_dir = Path(__file__).parent / "test_data"
    with open(test_data_dir / filename, "r") as f:
        return f.read()


async def evaluate_review_quality(diff: str, review_output: dict) -> dict:
    """
    Uses LLM to judge if the review is good quality.
    Returns: {score: 0-10, reasoning: str, missed_issues: []}
    """
    judge_llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    evaluation_prompt = f"""You are evaluating a code review tool's output quality.

## Original Diff:
{diff}

## Review Output:
{json.dumps(review_output, indent=2)}

Rate the review quality (0-10) based on:
1. Did it catch real issues in the diff?
2. Are the issues actionable and specific (file and line numbers)?
3. Are recommendations helpful and concrete?
4. Are there false positives (non-issues flagged as issues)?
5. Did it miss obvious security/quality issues?

The buggy_diff.txt contains 3 known issues:
- Hardcoded credentials (admin/admin123) - CRITICAL SECURITY
- Removed input validation in calculate_discount - QUALITY/SECURITY
- SQL injection vulnerability in execute_query - CRITICAL SECURITY

Respond with ONLY valid JSON, no other text:
{{"score": <0-10>, "reasoning": "<explanation>", "missed_issues": ["<issue1>", "<issue2>"]}}"""
    
    response = judge_llm.invoke(evaluation_prompt)
    return json.loads(response.content)


async def test_quality_on_buggy_diff():
    """Test review quality on known buggy diff."""
    print("\n🧪 Testing Review Quality (LLM-as-Judge)...")
    print("=" * 60)
    
    diff = load_sample_diff("buggy_diff.txt")
    summary = {"summary": "Authentication and discount calculation changes"}
    
    # Get review
    print("🔍 Running code review...")
    review = await review_simple_changes(diff, summary)
    
    print(f"   Found {len(review['issues'])} issues")
    for i, issue in enumerate(review['issues'], 1):
        print(f"   {i}. [{issue['category']}] {issue['file']}:{issue['line']}")
        print(f"      {issue['issue'][:80]}...")
    
    # Evaluate quality
    print("\n🤖 Evaluating quality with LLM judge...")
    evaluation = await evaluate_review_quality(diff, review)
    
    print(f"\n📊 Quality Score: {evaluation['score']}/10")
    print(f"📝 Reasoning: {evaluation['reasoning']}")
    
    if evaluation.get('missed_issues'):
        print(f"⚠️  Missed Issues:")
        for missed in evaluation['missed_issues']:
            print(f"   - {missed}")
    
    # Should score at least 7/10 to pass
    assert evaluation['score'] >= 7, f"Review quality too low: {evaluation['score']}/10"
    
    print(f"\n✅ Quality test passed! (Score: {evaluation['score']}/10)")
    return evaluation


async def run_quality_tests():
    """Run all quality evaluation tests."""
    print("=" * 60)
    print("Running Code Reviewer Quality Tests")
    print("=" * 60)
    
    try:
        evaluation = await test_quality_on_buggy_diff()
        
        print("\n" + "=" * 60)
        print("✅ Quality tests completed!")
        print("=" * 60)
        
        return evaluation
    
    except AssertionError as e:
        print(f"\n❌ Quality test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    # Make sure API keys are set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set")
        sys.exit(1)
    
    evaluation = asyncio.run(run_quality_tests())

"""
Structure tests for code reviewer functions.
Tests that outputs match expected Pydantic models.

Setup: Run `pip install -e .` from the project root before running tests.
"""

import asyncio
import json
import os
from pathlib import Path

from codereviewer.reviewer import review_simple_changes
from codereviewer.summarizer import summarize_changes


def load_sample_diff(filename: str) -> str:
    """Load a sample diff from test_data directory."""
    test_data_dir = Path(__file__).parent / "test_data"
    with open(test_data_dir / filename, "r") as f:
        return f.read()


async def test_summarizer_structure():
    """Verify summarizer returns correct dict structure."""
    print("\n🧪 Testing Summarizer Structure...")
    diff = load_sample_diff("simple_diff.txt")
    result = await summarize_changes(diff)
    
    # Check structure
    assert "summary" in result, "Missing 'summary' field"
    assert "number_of_changes" in result, "Missing 'number_of_changes' field"
    
    # Check types
    assert isinstance(result["summary"], str), "summary should be string"
    assert isinstance(result["number_of_changes"], int), "number_of_changes should be int"
    
    print(f"✅ Summarizer structure test passed!")
    print(f"   Summary: {result['summary'][:80]}...")
    print(f"   Changes: {result['number_of_changes']}")
    print(f"result: {result}")
    return result


async def test_simple_reviewer_structure():
    """Verify reviewer returns issues list with correct structure."""
    print("\n🧪 Testing Simple Reviewer Structure...")
    diff = load_sample_diff("buggy_diff.txt")
    summary = {"summary": "Authentication and discount calculation changes"}
    result = await review_simple_changes(diff, summary)
    
    # Check top-level structure
    assert "issues" in result, "Missing 'issues' field"
    assert isinstance(result["issues"], list), "issues should be a list"
    
    print(f"✅ Reviewer structure test passed!")
    print(f"   Found {len(result['issues'])} issues")
    
    # Validate Issue model fields if issues exist
    if result["issues"]:
        for i, issue in enumerate(result["issues"], 1):
            required_fields = ["category", "file", "line", "issue", "impact", "recommendation"]
            for field in required_fields:
                assert field in issue, f"Issue {i} missing '{field}' field in {issue}"
            
            print(f"   Issue {i}: {issue['category']} at {issue['file']}:{issue['line']}")
        
        print(f"✅ All issues have correct structure!")
    
    return result


async def test_catches_known_bugs():
    """Test that reviewer catches the 3 known bugs in buggy_diff.txt."""
    print("\n🧪 Testing Bug Detection...")
    diff = load_sample_diff("buggy_diff.txt")
    summary = {"summary": "Authentication and discount calculation changes"}
    result = await review_simple_changes(diff, summary)
    
    issues_found = len(result["issues"])
    print(f"   Found {issues_found} issues (expected at least 3)")
    
    # We expect at least 3 issues:
    # 1. Hardcoded credentials (admin/admin123)
    # 2. Removed input validation in calculate_discount
    # 3. SQL injection vulnerability in execute_query
    
    assert issues_found >= 3, f"Expected at least 3 issues, found {issues_found}"
    print(f"✅ Bug detection test passed! Found {issues_found} issues")
    
    return result


async def run_all_tests():
    """Run all structure tests."""
    print("=" * 60)
    print("Running Code Reviewer Structure Tests")
    print("=" * 60)
    
    try:
        # Run tests
        summary_result = await test_summarizer_structure()
        reviewer_result = await test_simple_reviewer_structure()
        bug_result = await test_catches_known_bugs()
        
        print("\n" + "=" * 60)
        print("✅ All structure tests passed!")
        print("=" * 60)
        
        return {
            "summary": summary_result,
            "review": reviewer_result,
            "bugs": bug_result
        }
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    # Make sure API keys are set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Tests may fail.")
    
    results = asyncio.run(run_all_tests())

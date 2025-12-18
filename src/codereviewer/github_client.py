import os
import logging
from github import Github

logger = logging.getLogger(__name__)

def post_comments_and_summary(review: dict, summary: dict) -> None:
    """
    Posts the comments and summary to the GitHub PR.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number_str = os.getenv("GITHUB_PULL_REQUEST_NUMBER")
    
    logger.info(f"Starting to post comments - repo: {repo_name}, pr_number: {pr_number_str}")
    
    if not github_token or not repo_name or not pr_number_str:
        logger.error(f"Missing required environment variables - token: {bool(github_token)}, repo: {bool(repo_name)}, pr_number: {bool(pr_number_str)}")
        return
    
    try:
        pr_number = int(pr_number_str)
    except ValueError:
        logger.error(f"Invalid PR number format: {pr_number_str}")
        return
    
    try:
        logger.info(f"Authenticating with GitHub...")
        gh_client = Github(github_token)
        logger.info(f"Getting repo: {repo_name}")
        repo = gh_client.get_repo(repo_name)
        logger.info(f"Getting PR #{pr_number}")
        pr = repo.get_pull(pr_number)
        logger.info(f"PR found: {pr.title}")
        
        # post the summary comment at the top of the pr
        summary_comment = f"## Code Review Summary\n\n{summary['summary']}"
        logger.info(f"Posting summary comment ({len(summary_comment)} chars)...")
        summary_result = pr.create_issue_comment(summary_comment)
        logger.info(f"✅ Summary comment posted: {summary_result.html_url}")

        # go through the review and post the comments on their respective lines
        issues = review.get("issues", [])
        logger.info(f"Posting {len(issues)} inline comments...")
        
        for i, issue in enumerate(issues, 1):
            comment_body = f"**{issue['category']}**: {issue['issue']}\n\n**Impact**: {issue['impact']}\n\n**Recommendation**: {issue['recommendation']}"
            try:
                logger.info(f"[{i}/{len(issues)}] Posting comment at {issue['file']}:{issue['line']}...")
                comment_result = pr.create_review_comment(
                    body=comment_body,
                    commit=pr.head.sha,
                    path=issue['file'],
                    line=issue['line']
                )
                logger.info(f"✅ Comment posted: {comment_result.html_url}")
            except Exception as e:
                logger.error(f"❌ Error posting comment for {issue['file']}:{issue['line']}: {e}", exc_info=True)

        logger.info(f"✅ All comments posted successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to authenticate or access PR: {e}", exc_info=True)
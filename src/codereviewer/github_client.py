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
        gh_client = Github(github_token)
        repo = gh_client.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        # post the summary comment at the top of the pr
        summary_comment = f"## Code Review Summary\n\n{summary['summary']}"
        summary_result = pr.create_issue_comment(summary_comment)
        logger.info(f"✅ Summary comment posted")

        # go through the review and post the comments on their respective lines
        issues = review.get("issues", [])
        logger.info(f"Posting {len(issues)} inline comments...")
        
        for issue in issues:
            comment_body = f"**{issue['category']}**: {issue['issue']}\n\n**Impact**: {issue['impact']}\n\n**Recommendation**: {issue['recommendation']}"
            try:
                pr.create_review_comment(
                    body=comment_body,
                    commit=pr.head.sha,
                    path=issue['file'],
                    line=issue['line']
                )
            except Exception as e:
                logger.error(f"❌ Error posting comment for {issue['file']}:{issue['line']}: {e}", exc_info=True)

        logger.info(f"✅ All comments posted successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to authenticate or access PR: {e}", exc_info=True)
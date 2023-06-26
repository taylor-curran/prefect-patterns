import requests
from prefect.blocks.core import Block
from datetime import datetime

class GitHubIssues(Block):
    """
    Interact with GitHub's API to get issues of a given repository.
    Get the most recently commented issue.

    Args:
        username (str): The username of the repository's owner.
        repo (str): The name of the repository.
        state (str): The state of the issues to return. Can be either 'open', 'closed', or 'all'. Default is 'open'.

    Example:
        Load stored block:
        ```python
        from my_blocks import GitHubIssues

        issues_block = GitHubIssues.load("BLOCK_NAME")
        issues_block.get_issues()
        ```
    """

    _block_type_name = "GitHub Issues"
    _block_schema_capabilities = ["get_issues", "get_most_recently_commented_issue"]
    _logo_url = ""
    username: str
    repo: str
    state: str = 'open'

    def get_issues(self) -> list:
        url = f"https://api.github.com/repos/{self.username}/{self.repo}/issues?state={self.state}"
        response = requests.get(url)
        response.raise_for_status()  # Will raise an exception if the status code is not 200
        return response.json()
    
    def get_most_recently_commented_issue(self) -> dict:
        issues = self.get_issues()
        most_recent_issue = max(issues, key=lambda issue: datetime.fromisoformat(issue['updated_at'].rstrip("Z")))
        return most_recent_issue
    


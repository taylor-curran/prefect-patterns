from custom_block import GitHubIssues

issues_block = GitHubIssues.load("my-issues-block")
issues_block.get_issues()
from custom_block import GitHubIssues

issues_block = GitHubIssues.load("my-issues-block")
print(issues_block.get_most_recently_commented_issue())
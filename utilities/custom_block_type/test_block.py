from custom_block import GitHubIssues

my_issues_block = GitHubIssues(repo="prefect", username="PrefectHQ")
my_issues_block.save("my-issues-block", overwrite=True)

issues_block = GitHubIssues.load("my-issues-block")
print(issues_block.get_most_recently_commented_issue())
class JIRAActivity:
    def __init__(self, jira_client: JIRA):
        self.jira_client = jira_client

    def create_issue(self, issue_type: str, summary: str, description: str):
        issue = self.jira_client.create_issue(
            project={"key": "TEST"},
            summary=summary,
            description=description,
            issuetype={"name": issue_type}
        )
        return issue
    
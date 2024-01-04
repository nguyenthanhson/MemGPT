import json
import os

from jira import JIRA
from jira.exceptions import JIRAError


def connect_to_jira(self):
    """
    Private function to connect to the user's JIRA instance.
    """
    if self.jira is None:
        server = os.getenv("JIRA_SERVER")
        email = os.getenv("JIRA_USER")
        token = os.getenv("JIRA_KEY")
        self.jira = JIRA({"server": server}, basic_auth=(email, token))


def get_jira_fields(self, issue_key: str, fields: str) -> dict:
    """
    Makes a request to user's JIRA instance with the jira issue key that is provided and returns the issue fields that are requested
    Args:
        issue_key (str): the issue key ("KMS-1" for example).
        fields (str): the fields to be returned. Example: "summary,description,issuetype,project,priority,reporter,assignee,status,updated,subtasks,fix_versions,parent,comment,attachment,issuelinks"
    Returns:
        dict: The response from the JIRA request.
    """
    connect_to_jira(self)
    try:
        issue = self.jira.issue(issue_key, fields=fields)
        # log issue object for debugging
        with open(issue_key + ".txt", "w") as f:
            json.dump(issue.raw, f, indent=4)

        return {
            "issue": {
                "key": issue.key,
                # loop though fields and add them to the response
                **{field: getattr(issue.fields, field) for field in fields.split(",")},
            }
        }
    except JIRAError as e:
        print(f"Error: {e.text}")
        return {"error": str(e.text)}


def get_jira(self, issue_key: str) -> dict:
    """
    Makes a request to user's JIRA instance with the jira issue that is provided and returns the issue details
    Args:
        issue_key (str): the issue key ("KMS-1" for example).
    Returns:
        dict: The response from the JIRA request.
    """
    connect_to_jira(self)
    try:
        issue = self.jira.issue(issue_key)
        # log issue object for debugging
        with open(issue_key + ".txt", "w") as f:
            json.dump(issue.raw, f, indent=4)

        return {
            "issue": {
                "key": issue.key,
                "summary": issue.fields.summary,
                "description": issue.fields.description,
                "issuetype": issue.fields.issuetype.name,
                "project": issue.fields.project.name,
                "priority": issue.fields.priority.name,
                "reporter": issue.fields.reporter.displayName,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None,
                "feature_flag": issue.fields.customfield_10069 if issue.fields.customfield_10069 else None,
                "feature_category": issue.fields.customfield_11104.value if issue.fields.customfield_11104 else None,
                "feature_category_id": issue.fields.customfield_11104.id if issue.fields.customfield_11104 else None,
                "status": issue.fields.status.name,
                "updated": issue.fields.updated,
                "subtasks": [subtask.key for subtask in issue.fields.subtasks],
                "sprint": [sprint.name for sprint in
                           issue.fields.customfield_10010] if issue.fields.customfield_10010 else None,
                "story_points": issue.fields.customfield_10038 if issue.fields.customfield_10038 else None,
                "fix_versions": [fix_version.name for fix_version in
                                 issue.fields.fixVersions] if issue.fields.fixVersions else None,
                "parent": {
                    "key": issue.fields.parent.key,
                    "summary": issue.fields.parent.fields.summary,
                    "issuetype": issue.fields.parent.fields.issuetype.name
                }
                if issue.fields.parent else None,
                "comments": [
                    {
                        "author": comment.author.displayName,
                        "body": comment.body,
                        "created": comment.created,
                        "updated": comment.updated,
                    }
                    for comment in issue.fields.comment.comments
                ] if issue.fields.comment.comments else None,
                "attachments": [
                    {
                        "filename": attachment.filename,
                        "created": attachment.created,
                        "size": attachment.size,
                        "content": attachment.get(),
                    }
                    for attachment in issue.fields.attachment
                ] if issue.fields.attachment else None,
                # "links": [
                #     {
                #         "type": link.type.name,
                #         "inwardIssue": link.inwardIssue.key if link.inwardIssue else None,
                #         "inwardIssueSummary": link.inwardIssue.fields.summary if link.inwardIssue else None,
                #         "inwardIssueType": link.inwardIssue.fields.issuetype.name if link.inwardIssue else None,
                #         "inwardIssueStatus": link.inwardIssue.fields.status.name if link.inwardIssue else None,
                #         "outwardIssue": link.outwardIssue.key if link.outwardIssue else None,
                #         "outwardIssueSummary": link.outwardIssue.fields.summary if link.outwardIssue else None,
                #         "outwardIssueType": link.outwardIssue.fields.issuetype.name if link.outwardIssue else None,
                #         "outwardIssueStatus": link.outwardIssue.fields.status.name if link.outwardIssue else None,
                #     }
                #     for link in issue.fields.issuelinks
                # ] if issue.fields.issuelinks else None,
            }
        }
    except JIRAError as e:
        print(f"Error: {e.text}")
        return {"error": str(e.text)}


def query_jira(self, jql: str, max_results: int) -> dict:
    """
    Makes a request to user's JIRA instance with the jql that is provided and returns the issues
    Args:
        jql (str): the Jira Query Language. Example: "project=KMS and assignee != currentUser() and resolution = Unresolved order by priority DESC"
        max_results (int): the maximum number of results to return. Example: 10
    Returns:
        dict: The response from the JIRA request containing issue keys and summaries.
    """
    connect_to_jira(self)
    try:
        issues = self.jira.search_issues(jql, maxResults=max_results)
        return {"issues": [{"key": issue.key, "summary": issue.fields.summary} for issue in issues]}
    except JIRAError as e:
        print(f"Error: {e.text}")
        return {"error": str(e.text)}


def get_projects(self) -> dict:
    """
    Makes a request to user's JIRA instance and returns the projects
    Returns:
        dict: The response from the JIRA request.
    """
    connect_to_jira(self)
    try:
        projects = self.jira.projects()
        return {"projects": [project.key for project in projects]}
    except JIRAError as e:
        print(f"Error: {e.text}")
        return {"error": str(e.text)}


def get_boards(self) -> dict:
    """
    Makes a request to user's JIRA instance and returns the boards
    Returns:
        dict: The response from the JIRA request.
    """
    connect_to_jira(self)
    try:
        boards = self.jira.boards()
        return {"boards": [board.name for board in boards]}
    except JIRAError as e:
        print(f"Error: {e.text}")
        return {"error": str(e.text)}


def get_board_id(self, board_name: str) -> dict:
    """
    Makes a request to user's JIRA instance and returns the board id
    Args:
        board_name (str): the board name.
    Returns:
        dict: The response from the JIRA request.
    """
    connect_to_jira(self)
    try:
        boards = self.jira.boards()
        for board in boards:
            if board.name == board_name:
                return {"board_id": board.id}
        return {"error": "Board not found"}
    except JIRAError as e:
        print(f"Error: {e.text}")
        return {"error": str(e.text)}


def get_sprints(self, board_id: int) -> dict:
    """
    Makes a request to user's JIRA instance and returns the sprints
    Args:
        board_id (int): the board id.
    Returns:
        dict: The response from the JIRA request.
    """
    connect_to_jira(self)
    try:
        sprints = self.jira.sprints(board_id)
        return {"sprints": [sprint.name for sprint in sprints]}
    except JIRAError as e:
        print(f"Error: {e.text}")
        return {"error": str(e.text)}


def get_sprint(self, sprint_id: int) -> dict:
    """
    Makes a request to user's JIRA instance and returns the sprint name
    Args:
        sprint_id (int): the sprint id.
    Returns:
        dict: The response from the JIRA request.
    """
    connect_to_jira(self)
    try:
        sprint = self.jira.sprint(sprint_id)
        return {"sprint": sprint.name}
    except JIRAError as e:
        print(f"Error: {e.text}")
        return {"error": str(e.text)}

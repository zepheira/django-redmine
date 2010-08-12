from django.template import RequestContext
from django.conf import settings

from freemix_redmine.utils import *

def redmine_create_issue(project_id, subject, description, tracker, author,
                         status = None,
                         priority = None,
                         assigned_to = None,
                         fixed_version = None,
                         parent = None,
                         start_date = None,
                         due_date = None,
                         done_ratio = None,
                         estimated_hours = None):
    """
    Generic method for creating an issue in an associated Redmine
    installation.  Unlikely to be directly useful.  No provision
    for custom fields for the time being.
    """
    c = RedmineClient(settings.REDMINE_URL, settings.REDMINE_USER, settings.REDMINE_PASSWORD, settings.REDMINE_KEY)
    issue = RedmineIssue(None)
    issue.set_project(project_id)
    issue.add_element('subject', value = subject)
    issue.add_element('description', value = description)
    issue.add_element('tracker', tracker)
    issue.add_element('author', author)
    if status is not None:
        issue.add_element('status', status)
    if priority is not None:
        issue.add_element('priority', priority)
    if assigned_to is not None:
        issue.add_element('assigned_to', assigned_to)
    if fixed_version is not None:
        issue.add_element('fixed_version', fixed_version)
    if parent is not None:
        issue.add_element('parent', parent)
    if start_date is not None:
        issue.add_element('start_date', value = start_date)
    if due_date is not None:
        issue.add_element('due_date', value = due_date)
    if done_ratio is not None:
        issue.add_element('done_ratio', value = done_ratio)
    if estimated_hours is not None:
        issue.add_element('estimated_hours', value = estimated_hours)

    return c.create_issue(issue)

def recollection_create_issue(subject, description):
    """
    Sugar for easier issue creation pertaining to our needs.
    Returns the URL for the new issue.
    """
    new_id = redmine_create_issue(settings.REDMINE_PROJECT_ID, subject, description, REDMINE['TRACKER']['SUPPORT'], settings.REDMINE_USER_ID)
    if new_id is not None:
        return '%s/issues/%s' % (settings.REDMINE_URL, new_id)
    else:
        return None

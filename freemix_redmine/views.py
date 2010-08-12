from django.conf import settings
from django.template import RequestContext

from freemix_redmine.utils import *

def create_issue(project, tracker, author, status = None, priority = None, assigned_to = None, fixed_version = None, parent = None, subject = None, description = None, start_date = None, due_date = None, done_ratio = None, estimated_hours = None):
    issue = RedmineIssue(None, None)
    issue.add_element('project', project)
    issue.add_element('tracker', tracker)
    issue.add_element('author', author)
    if (status is not None):
        issue.set_attribute

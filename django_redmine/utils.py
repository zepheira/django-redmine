import httplib2
import urllib
import os
import sys
from xml.dom import minidom

"""
The Redmine API is documented at:
http://www.redmine.org/wiki/1/Rest_api

The API usage examples make use of ActiveResource libraries and the API
is clearly geared towards making use of an underlying knowledge base of
ActiveResource, so the description is a bit light on details.  As such,
only the most vital portions of this library have tests associated with
them, specifically issue creation.  There is an active bug around the
use of custom fields in issue management.  Adding issue custom fields
right now will do nothing.

A Redmine URL, user, password, and user API key are needed to initialize
the RedmineClient.  To run this set of doctests, you will have to supply
them below as well.
"""

class RedmineResource:
    """
    Base class, do not use directly.
    """
    def __init__(self, document = None, node = None, root = None):
        self.document = document
        if self.document is None and node is not None:
            impl = minidom.getDOMImplementation()
            self.resource = impl.createDocument(None, None, None)
            self.resource.appendChild(node)
        elif self.document is None:
            impl = minidom.getDOMImplementation()
            self.resource = impl.createDocument(None, root, None)

    def add_element(self, element, id = None, name = None, value = None, is_custom = False):
        element = self.resource.createElement(element)
        if id is not None:
            if type(id).__name__ == "int":
                element.setAttribute('id', '%d' % id)
            else:
                element.setAttribute('id', id)
        if name is not None:
            element.setAttribute('name', name)
        if value is not None:
            if type(value).__name__ == "int":
                val = self.resource.createTextNode('%d' % value)
            else:
                val = self.resource.createTextNode(value)
            if is_custom:
                valEl = self.resource.createElement('value')
                valEl.appendChild(val)
                element.appendChild(valEl)
            else:
                element.appendChild(val)
        if is_custom:
            customEl = self.resource.getElementsByTagName('custom_fields')
            if len(customEl) > 0:
                customEl[0].appendChild(element)
            else:
                customEl = self.resource.createElement('custom_fields')
                customEl.setAttribute('type', 'array')
                customEl.appendChild(element)
                self.resource.documentElement.appendChild(customEl)
        else:
            self.resource.documentElement.appendChild(element)

    def get_element(self, element_name):
        els = self.resource.getElementsByTagName(element_name)
        if len(els) > 0:
            return els[0].firstChild.data
        else:
            return None

    def parse(self, xml):
        self.resource = minidom.parseString(xml)
        return self.resource

    def to_xml(self):
        return self.resource.toxml()

class RedmineUser(RedmineResource):
    def __init__(self, user = None):
        """
        Redmine user representation, tied to the API XML form.

        >>> r = RedmineUser(None)
        >>> r.to_xml()
        '<?xml version="1.0" ?><project/>'
        """
        RedmineResource.__init__(self, None, user, 'user')

class RedmineProject(RedmineResource):
    def __init__(self, project = None):
        """
        Redmine project representation, tied to the API XML form.

        >>> r = RedmineProject(None)
        >>> r.to_xml()
        '<?xml version="1.0" ?><project/>'
        """
        RedmineResource.__init__(self, None, project, 'project')

class RedmineIssue(RedmineResource):
    def __init__(self, issue = None):
        """
        Redmine issue representation, tied to the API XML form.

        >>> r = RedmineIssue(None)
        >>> r.to_xml()
        '<?xml version="1.0" ?><issue/>'
        >>> r.add_element('project', '1')
        >>> r.to_xml()
        '<?xml version="1.0" ?><issue><project id="1"/></issue>'
        """
        RedmineResource.__init__(self, None, issue, 'issue')
        self.project_id = None

    def set_project(self, project_id):
        self.project_id = project_id
        self.add_element('project_id', value = project_id)

class RedmineClient:
    def __init__(self, base, user, password, key):
        """
        Talks to the API.
        """
        # httplib2 uses its own CA file, which is dumb. Workaround for Ubuntu.
        certfile = None
        if os.path.isfile("/etc/ssl/certs/ca-certificates.crt"):
            certfile = "/etc/ssl/certs/ca-certificates.crt"
        if base[-1] == '/':
            base = base[0:-1]
        self.base = base
        if certfile is not None:
            self.http = httplib2.Http(ca_certs=certfile)
        else:
            self.http = httplib2.Http()
        self.http.add_credentials(user, password)
        self.key = key

    def _request(self, url, method, payload = None):
        headers = {'X-Redmine-API-Key': self.key,
                   'X-ChiliProject-API-Key': self.key}
        if payload is not None:
            headers['Content-Type'] = 'application/xml; charset=utf-8'
        return self.http.request(url, method=method, body=payload, headers=headers)
    
    
    # ---- Users ----

    def get_users(self):
        """
        """
        url = "%s/users.xml" % self.base
        response, content = self._request(url, "GET")
        users = []
        usersRoot = minidom.parseString(content)
        usersList = usersRoot.documentElement.getElementsByTagName('users')
        for user in usersList:
            users.append(RedmineUser(user))
        return users
    
    
    # ---- Projects ----

    def get_projects(self):
        """
        Get a [list] of all projects
        GET $base/projects.xml

        >>> r = RedmineClient('http://redmine.example.com', 'test_username', 'test_password', 'test_key')
        >>> p = r.get_projects()
        >>> len(p) > 0
        True
        """
        url = "%s/projects.xml" % self.base
        response, content = self._request(url, "GET")
        projects = []
        projectsRoot = minidom.parseString(content)
        projectsList = projectsRoot.documentElement.getElementsByTagName('project')
        for project in projectsList:
            projects.append(RedmineProject(project))
        return projects

    def get_project(self, id):
        """
        Get one project based on the numerical ID or short identifier
        GET $base/projects/$id.xml
        """
        if type(id).__name__ == "int":
            url = "%s/projects/%d.xml" % (self.base, id)
        else:
            url = "%s/projects/%s.xml" % (self.base, id)
        response, content = self._request(url, "GET")
        project = RedmineProject(None)
        project.parse(content)
        return project

    def create_project(self, project):
        """
        Create a project
        POST $base/projects.xml
        """
        url = "%s/projects.xml" % self.base
        response, content = self._request(url, "POST", project.to_xml())
        if response.status == 201:
            new_project = RedmineProject(None)
            new_project.parse(content)
            return new_project.get_element('id')
        else:
            # It would be better to have details about failure modes here instead of a global None
            return None            

    def update_project(self, id, project):
        """
        Update a project
        PUT $base/projects/$id.xml
        """
        if type(id).__name__ == "int":
            url = "%s/projects/%d.xml" % (self.base, id)
        else:
            url = "%s/projects/%s.xml" % (self.base, id)
        response, content = self._request(url, "PUT", project.to_xml())
        if response.status == 200:
            return True
        else:
            return False

    def delete_project(self, id):
        """
        Delete a project
        DELETE $base/projects/$id.xml
        """
        if type(id).__name__ == "int":
            url = "%s/projects/%d.xml" % (self.base, id)
        else:
            url = "%s/projects/%s.xml" % (self.base, id)
        response, content = self._request(url, "DELETE")
        if response.status == 200:
            return True
        else:
            return False

    # ---- Issues ----

    def get_issues(self, project_id = None, tracker = None, status = None, page = 0, custom = None):
        """
        Get paginated list of all issues
        GET $base/issues.xml?page=$page&project_id=$project&tracker_id=$tracker&status_id=$status

        Creating an issue should probably be part of this test...
        >>> r = RedmineClient('http://redmine.example.com', 'test_username', 'test_password', 'test_key')
        >>> l = r.get_issues(1)
        >>> len(l) > 0
        True
        """
        urlArgs = {'key': self.key, 'page': page}
        if project_id is not None:
            urlArgs['project_id'] = project_id
        if tracker is not None:
            urlArgs['tracker_id'] = tracker
        if status is not None:
            urlArgs['status_id'] = status
        if custom is not None:
            if type(custom).__name__ == "dict":
                for cf_id in custom:
                    urlArgs['cf_%d' % cf_id] = custom[cf_id]
        url = "%s/issues.xml?%s" % (self.base, urllib.urlencode(urlArgs))
        response, content = self._request(url, "GET")
        issues = []
        issuesRoot = minidom.parseString(content)
        issuesList = issuesRoot.documentElement.getElementsByTagName('issue')
        for issue in issuesList:
            issues.append(RedmineIssue(issue))
        return issues

    def get_issue(self, id):
        """
        Get one issue
        GET $base/issues/$id.xml

        >>> r = RedmineClient('http://redmine.example.com', 'test_username', 'test_password', 'test_key')
        >>> i = r.get_issue(12)
        >>> i.get_element('id').firstChild.data
        u'12'
        """
        url = "%s/issues/%d.xml" % (self.base, id)
        response, content = self._request(url, "GET")
        issue = RedmineIssue(None)
        issue.parse(content)
        return issue

    def create_issue(self, issue):
        """
        Create an issue
        POST $base/issues.xml?project_id=$project_id

        >>> r = RedmineClient('http://redmine.example.com', 'test_username', 'test_password', 'test_key')
        >>> i = RedmineIssue(None)
        >>> i.set_project('1')
        >>> i.add_element('tracker', '3')
        >>> i.add_element('status', '1')
        >>> i.add_element('priority', '4')
        >>> i.add_element('author', '3')
        >>> i.add_element('subject', value = 'Test')
        >>> i.add_element('description', value = 'Test')
        >>> i.add_element('custom_field', id = '1', value = 'http://somewhere.com/file.xls', is_custom = True)
        >>> i.to_xml()
        '<?xml version="1.0" ?><issue><project_id>1</project_id><tracker id="3"/><status id="1"/><priority id="4"/><author id="3"/><subject>Test</subject><description>Test</description><custom_fields type="array"><custom_field id="1"><value>http://somewhere.com/file.xls</value></custom_field></custom_fields></issue>'
        >>> r.create_issue(i) is not None
        True
        """
        url = "%s/issues.xml?project_id=%s" % (self.base, issue.project_id)
        response, content = self._request(url, "POST", issue.to_xml())
        if response.status == 201:
            new_issue = RedmineIssue(None)
            new_issue.parse(content)
            return new_issue.get_element('id')
        else:
            # It would be better to have details about failure modes here instead of a global None
            return None            

    def update_issue(self, id, issue):
        """
        Update an issue
        PUT $base/issues/$id.xml
        """
        url = "%s/issues/%d.xml" % (self.base, id)
        response, content = self._request(url, "PUT", issue.to_xml())
        if response.status == 200:
            return True
        else:
            return False

    def delete_issue(self, id):
        """
        Delete an issue
        DELETE $base/issues/$id.xml
        """
        url = "%s/issues/%d.xml" % (self.base, id)
        response, content = self._request(url, "DELETE")
        if response.status == 200:
            return True
        else:
            return False

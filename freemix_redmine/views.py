import httplib2
import sys
from xml.dom import minidom

class RedmineResource:
    def __init__(self, xml = None, resource = None):
        self.xml = xml
        self.resource = resource
        self.obj = {}
        if (self.xml is not None and self.resource is None):
            self.parse(self.xml)

    def set_attribute(self, name, value):
        self.obj[name] = value

    def parse(self, xml):
        self.resource = minidom.parseString(self.xml)
        return self.resource

    def to_xml(self):
        if (self.xml is None):
            self.xml = self.resource.toxml()
        return self.xml

class RedmineProject(RedmineResource):
    def b():
        return None

class RedmineIssue(RedmineResource):
    def __init__(self, xml = None, issue = None):
        super().__init__(xml, issue)

#def create_issue(project, tracker, author, status = None, priority = None, assigned_to = None, fixed_version = None, parent = None, subject = None, description = None, start_date = None, due_date = None, done_ratio = None, estimated_hours = None):

class RedmineClient:
    def __init__(self, base, user, password):
        if base[-1] == '/':
            base = base[0:-1]
        self.base = base
        self.http = httplib2.Http()
        self.http.add_credentials(user, password)

    # ---- Projects ----

    def get_projects(self):
        '''
        Get a [list] of all projects
        GET $base/projects.xml
        '''
        url = self.base + "/projects.xml"
        response, content = self.http.request(url, "GET")
        projects = []
        projectsRoot = minidom.parseString(content)
        projectsList = projectsRoot.documentElement.getElementsByTagName('project')
        for project in projectsList:
            projects.append(RedmineProject(None, project))
        return projects

    def get_project(self, id):
        '''
        Get one project based on the numerical ID or short identifier
        GET $base/projects/$id.xml
        '''
        if (type(id).__name__ == "int"):
            url = "%s/projects/%d.xml" % (self.base, id)
        else:
            url = "%s/projects/%s.xml" % (self.base, id)
        response, content = self.http.request(url, "GET")
        return RedmineProject(content, None)

    def create_project(self, project):
        '''
        Create a project
        POST $base/projects.xml
        '''
        url = self.base + "/projects.xml"
        response, content = self.http.request(url, "POST", project.to_xml())
        # return http response object?
        return response

    def update_project(self, id, project):
        '''
        Update a project
        PUT $base/projects/$id.xml
        '''
        if (type(id).__name__ == "int"):
            url = "%s/projects/%d.xml" % (self.base, id)
        else:
            url = "%s/projects/%s.xml" % (self.base, id)
        response, content = self.http.request(url, "PUT", project.to_xml())
        # return http response object?
        return response

    def delete_project(self, id):
        '''
        Delete a project
        DELETE $base/projects/$id.xml
        '''
        if (type(id).__name__ == "int"):
            url = "%s/projects/%d.xml" % (self.base, id)
        else:
            url = "%s/projects/%s.xml" % (self.base, id)
        response, content = self.http.request(url, "DELETE")
        # return http response object?
        return response

    # ---- Issues ----

    def get_issues(self, project = None, tracker = None, status = None, page = 0):
        '''
        Get paginated list of all issues
        GET $base/issues.xml?page=$page&project_id=$project&tracker_id=$tracker&status_id=$status
        '''
        url = "%s/issues.xml?page=%d" % (self.base, page)
        if (type(project).__name__ == "int"):
            url = "%s&project_id=%d" % (url, project)
        else:
            url = "%s&project_id=%s" % (url, project)
        if (tracker is not None):
            url = "%s&tracker_id=%d" % (url, tracker)
        if (status is not None):
            if (type(status).__name__ == "int"):
                url = "%s&status_id=%d" % (url, status)
            else:
                url = "%s&status_id=%s" % (url, status)
        response, content = self.http.request(url, "GET")
        issues = []
        issuesRoot = minidom.parseString(content)
        issuesList = issuesRoot.documentElement.getElementsByTagName('issue')
        for issue in issuesList:
            issues.append(RedmineIssue(None, issue))
        return issues

    def get_issue(self, id):
        '''
        Get one issue
        GET $base/issues/$id.xml
        '''
        url = "%s/issues/%d.xml" % (self.base, id)
        response, content = self.http.request(url, "GET")
        return RedmineIssue(content, None)

    def create_issue(self, issue):
        '''
        Create an issue
        POST $base/issues.xml
        '''
        url = "%s/issues.xml" % self.base
        response, content = self.http.request(url, "POST", issue.to_xml())
        # return http response?
        return response

    def update_issue(self, id, issue):
        '''
        Update an issue
        PUT $base/issues/$id.xml
        '''
        url = "%s/issues/%d.xml" % (self.base, id)
        response, content = self.http.request(url, "PUT", issue.to_xml())
        # return http response?
        return response

    def delete_issue(self, id):
        '''
        Delete an issue
        DELETE $base/issues/$id.xml
        '''
        url = "%s/issues/%d.xml" % (self.base, id)
        response, content = self.http.request(url, "DELETE")
        # return http response
        return response

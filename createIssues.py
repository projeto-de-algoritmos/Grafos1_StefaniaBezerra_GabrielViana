import json
import requests
#from user import *


# Authentication for user filing issue (must have read/write access to
# repository to add issue to)
user = ''
password = ''

# The repository to add this issue to
REPO_OWNER = 'TecProg-20181'
REPO_NAME = 'T--jiboia'

def make_github_issue(title, body=None):
    '''Create an issue on github.com using the given parameters.'''
    # Our url to create issues via POST
    url = 'https://api.github.com/repos/%s/%s/issues' % (REPO_OWNER, REPO_NAME)
    # Create an authenticated session to create the issue
    session = requests.session()
    auth=(user, password)
    session.auth = auth
    # Create our issue
    issue = {'title': title,
             'body': body
             }
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        print ('Successfully created Issue "%s"' % title)
    else:
        print ('Could not create Issue "%s"' % title)
        print ('Response:', r.content)

#make_github_issue('Issue Title', 'Body text')
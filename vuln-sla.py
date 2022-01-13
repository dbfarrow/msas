#!/usr/bin/env python

from dateutil.parser import parse
from datetime import datetime, timezone
from jira import JIRA
import os

if __name__ == "__main__":

    with open(os.path.expanduser('~/.ssh/atlassian'), 'r') as tf:
        token = tf.readline().strip()

    url = 'https://cookieai.atlassian.net/'
    auth = ( 'dave.farrow@cookie.ai', token )
    jira = JIRA(url, basic_auth=auth)
    
    slas = {
        'P0': 7,
        'P1': 30,
        'P2': 90,
        'P3': 180,
        'None': 9999,
    }

    separator = '|'
    cols = [ 'issuetype', 'issueid', 'priority', 'status', 'summary', 'created', 'resolved', 'age', 'sla', 'compliant' ]
    print(separator.join(cols))
 
    issues = jira.search_issues('issuetype in (Vulnerability, Security)')
    for issue in issues:
        f = {
            'issuetype': issue.fields.issuetype,
            'issueid': issue,
            'priority': issue.fields.priority,
            'status': issue.fields.status,
            'summary': issue.fields.summary,
            'created': issue.fields.created,
            'resolved': issue.fields.resolutiondate,
        }
        if issue.fields.status.name == 'Done':
            age = (parse(issue.fields.resolutiondate) - parse(issue.fields.created)).days
        else:
            age = (datetime.now(timezone.utc) - parse(issue.fields.created)).days
        sla = slas[issue.fields.priority.name]
        compliant = (age <= sla)
        f['age'] = age
        f['sla'] = sla
        f['compliant'] = compliant

        print(separator.join([ str(f[x]) for x in cols ]))


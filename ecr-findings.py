#!/usr/bin/env python

import boto3
import json

REGION='us-east-2'

def get_repos(ecr, region):

    ecr = boto3.client('ecr', region_name=region)
    repos = ecr.describe_repositories()
    for r in repos['repositories']:
        yield r['repositoryName']

    return
    
def get_current_image(ecr, repo):

    latest_image = None
    latest = None

    # aws ecr describe-images --repository agent_manager --query 'sort_by(imageDetails,& imagePushedAt)[-1].imageTags[0]'
    images = ecr.describe_images(repositoryName=repo, maxResults=1000)
    for i in images['imageDetails']:
        pushed = i['imagePushedAt']
        if (not latest) or (pushed > latest):
            latest_image = i
            latest = pushed

    if latest_image:
        return latest_image['imageTags'][0]
    else:
        return None

def get_scan_findings(ecr, repo):

    image = get_current_image(ecr, repo)
    if not image:
        return None

    findings = ecr.describe_image_scan_findings(repositoryName=repo, imageId={'imageTag': image})
    if 'imageScanFindings' in findings:
        scanned = findings['imageScanFindings']['imageScanCompletedAt']
        for f in findings['imageScanFindings']['findings']:
            a = f['attributes']
            f['repo'] = repo
            f['tag'] = image
            f['scanned'] = str(scanned)
            f['package'] = f'{a[1]["value"]} {a[0]["value"]}'
            f['vector'] = a[2]["value"] if len(a) > 2 else 'none'
            f['score'] = a[3]["value"] if len(a) > 2 else 'none'
            del f['attributes']
            yield f
    else:
        return { 'repo': repo, 'tag': image }
        
FIELDS = [ 'repo', 'tag', 'name', 'package', 'severity', 'score', 'vector', 'scanned' ]

if __name__ == '__main__':

    ecr = boto3.client('ecr', region_name=REGION)

    print(','.join(FIELDS))
    for repo in get_repos(ecr, REGION):
        for f in get_scan_findings(ecr, repo):
            line = []
            for F in FIELDS:
                line.append(f.get(F))
            print(','.join(line))





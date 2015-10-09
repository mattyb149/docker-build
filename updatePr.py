#!/usr/bin/env python

import argparse
import json
import os
import sys
from jinja2 import Environment, PackageLoader
from subprocess import call
from urllib2 import urlopen, Request, HTTPError

def post_comment(repo, pr, token, comment):
  try:
    url = ''.join(['https://api.github.com/repos/', repo, '/issues/', str(pr), '/comments'])
    request = Request(url, json.dumps({ 'body' : comment }).encode('UTF-8'))
    request.add_header('Authorization', 'token {}'.format(token))
    response = urlopen(request, timeout = 20)
    charset = 'UTF-8'
    content_type = response.info().get('Content-Type').split(';')
    for info in content_type:
      if info.startswith('charset='):
        charset = info.split('=')[-1]
    return json.loads(response.read().decode(charset, 'strict'))
  except HTTPError as e:
    print e.read()

def get_pr_info(repo, pr, token = None):
  return api_request(''.join(['https://api.github.com/repos/', repo, '/pulls/', str(pr)]), token)

def get_compare_info(repo, headLabel, baseLabel, token = None):
  return api_request(''.join(['https://api.github.com/repos/', repo, '/compare/', headLabel, '...', baseLabel]), token)

def enrichJacoco(jacoco):
  result = {}
  result[u'results'] = jacoco
  coverageTypes = set([])
  for group, diffs in jacoco.iteritems():
    for classname, coverages in diffs.iteritems():
      for coverageType, number in coverages.iteritems():
        coverageTypes.add(coverageType)
  result[u'coverageTypes'] = [ coverageType for coverageType in coverageTypes ]
  result[u'coverageTypes'].sort()
  return result

if __name__ == '__main__':
  os.chdir('/home/gitguy')
  parser = argparse.ArgumentParser(description='''
    This script will post a comment about the output of the build
  ''', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-a", "--apiToken", help="Github api token")
  parser.add_argument("-r", "--repository", help="Format: owner/repo")
  parser.add_argument("-p", "--pullRequest", help="Pull request number")
  args, unknown = parser.parse_known_args()
  with open('aggregate-metrics/checkstyle.json', 'r') as f:
    checkstyle = json.load(f)
  with open('aggregate-metrics/tests.json', 'r') as f:
    tests = json.load(f)
  with open('aggregate-metrics/jacocoUnit.json', 'r') as f:
    jacocoUnit = json.load(f)
  with open('aggregate-metrics/jacocoIntegration.json', 'r') as f:
    jacocoIntegration = json.load(f)

  jacocoUnit = enrichJacoco(jacocoUnit)
  jacocoUnit['header'] = "Unit test coverage change"
  jacocoIntegration = enrichJacoco(jacocoIntegration)
  jacocoIntegration['header'] = "Integration test coverage change"

  env = Environment(loader = PackageLoader('updatePr', 'templates'))

  comments = [
    env.get_template('checkstyle.md').render(checkstyle),
    env.get_template('tests.md').render(tests),
    env.get_template('jacoco.md').render(jacocoUnit),
    env.get_template('jacoco.md').render(jacocoIntegration)
  ]

  output = '\n'.join(comments)
  
  if not args.repository or not args.pullRequest or not args.apiToken:
    parser.print_help()
    raise Exception('repository, pullRequest, apiToken required')
  else:
    print 'Posting comment on pull request'

  post_comment(args.repository, args.pullRequest, args.apiToken, '\n'.join(comments))

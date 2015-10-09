#!/usr/bin/env python

import argparse
import json
import os
import sys
from subprocess import call
from urllib2 import urlopen, Request, HTTPError

def call_and_check(command, error_message, shell=False):
  result = call(command, shell=shell)
  if result != 0:
    raise Exception(error_message)

def api_request(url, token = None):
  request = Request(url)
  if token:
    request.add_header('Authorization', 'token {}'.format(token))
  response = urlopen(request, timeout = 20)
  charset = 'UTF-8'
  content_type = response.info().get('Content-Type').split(';')
  for info in content_type:
    if info.startswith('charset='):
      charset = info.split('=')[-1]
  return json.loads(response.read().decode(charset, 'strict'))

def get_pr_info(repo, pr, token = None):
  return api_request(''.join(['https://api.github.com/repos/', repo, '/pulls/', str(pr)]), token)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='''
    This script will pull down a pull request, build it, and compare it against master
  ''', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-b", "--beforeDirectory", help="Directory for metrics before merge")
  parser.add_argument("-a", "--afterDirectory", help="Directory for metrics after merge")
  parser.add_argument("-b", "--buildCommand", help="Build command")
  parser.add_argument("-m", "--metricsCommand", help="Metrics command")
  parser.add_argument("-a", "--aggregateCommand", help="Aggregate metrics")
  parser.add_argument("-c", "--cleanupCommand", help="Cleanup command")
  args = parser.parse_args()
  if not args.repository or not args.pullRequest or not args.buildCommand or not args.cleanupCommand or not args.metricsCommand:
    parser.print_help()
    raise Exception('repository, pullRequest, buildCommand, and cleanupCommand are required')
  api_token = os.environ.get('API_TOKEN')
  api = 'https://api.github.com/repos/'
  api += args.repository
  pr_info = get_pr_info(args.repository, args.pullRequest)
  commits = pr_info['commits']
  branch_to_apply = pr_info['base']['ref']
  if not pr_info['merged'] and not pr_info['mergeable']:
    raise Exception('PR needs to be rebased to be mergeable')
  merge_commit_sha = pr_info['merge_commit_sha']
  repository = 'https://'
  if api_token:
    repository += api_token
    repository += '@'
  repository += 'github.com/'
  repository += args.repository
  repository += '.git'
  call_and_check(['git', 'config', '--global', 'user.email', 'docker-buildguy@pentaho.com'], "Couldn't set email")
  call_and_check(['git', 'config', '--global', 'user.name', 'docker-buildguy'], "Couldn't set email")
  call_and_check(['git', 'init'], "Couldn't initialize git")
  call_and_check(['git', 'clone', '--depth=1', '--branch', branch_to_apply, repository, 'build-dir' ], "Couldn't clone repo")
  os.chdir('build-dir')
  os.mkdir('before-metrics')
  os.mkdir('after-metrics')
  try:
    #call_and_check(args.buildCommand, "Build failed", shell = True)
    #call_and_check(args.metricsCommand + ' before-metrics', "Couldn't collect metrics", shell = True)
    call_and_check(['git', 'fetch', 'origin', '--depth=' + str(commits + 2), 'pull/' + str(args.pullRequest) + '/head:pullRequest'], "Couldn't fetch pr")
    call_and_check(['git', 'merge', '--no-edit', '--no-ff', 'pullRequest'], "Couldn't merge pr")
    #call_and_check(args.buildCommand, "Build failed", shell = True)
    #call_and_check(args.metricsCommand + ' after-metrics', "Couldn't collect metrics", shell = True)
    #call_and_check(args.aggregateCommand + ' before-metrics after-metrics', "Couldn't collect metrics", shell = True)
  finally:
    call_and_check(args.cleanupCommand, "Cleanup failed", shell = True)

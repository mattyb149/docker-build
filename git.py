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

def get_compare_info(repo, headLabel, baseLabel, token = None):
  return api_request(''.join(['https://api.github.com/repos/', repo, '/compare/', headLabel, '...', baseLabel]), token)

if __name__ == '__main__':
  os.chdir('/home/gitguy')
  parser = argparse.ArgumentParser(description='''
    This script will pull down a pull request
  ''', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-a", "--apiToken", help="Github api token")
  parser.add_argument("-r", "--repository", help="Format: owner/repo")
  parser.add_argument("-p", "--pullRequest", help="Pull request number")
  args, unknown = parser.parse_known_args()
  if not args.repository or not args.pullRequest:
    parser.print_help()
    raise Exception('repository, pullRequest')
  else:
    print 'Fetching pr ' + str(args.pullRequest) + ' from ' + str(args.repository)
  api_token = args.apiToken
  api = 'https://api.github.com/repos/'
  api += args.repository

  pr_info = get_pr_info(args.repository, args.pullRequest)
  commits = pr_info['commits']
  headLabel = pr_info['head']['label']
  baseLabel = pr_info['base']['label']
  branch_to_apply = pr_info['base']['ref']
  compare_info = get_compare_info(args.repository, headLabel, baseLabel)

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
  call_and_check(['git', 'clone', '--depth=' + str(int(compare_info['ahead_by']) + 10), '--branch', branch_to_apply, repository, 'build-dir/base' ], "Couldn't clone repo")
  call_and_check(['cp', '-r', 'build-dir/base', 'build-dir/head' ], "Couldn't clone repo")
  os.chdir('build-dir/head')
  call_and_check(['git', 'fetch', '--depth=' + str(int(commits) + 10), 'origin', 'pull/' + str(args.pullRequest) + '/head:pullRequest'], "Couldn't fetch pr")
  call_and_check(['git', 'merge', '--no-edit', '--no-ff', 'pullRequest'], "Couldn't merge pr")
  call_and_check('git diff --name-only --relative origin/' + branch_to_apply + ' > checkdiff.out', 'Couldn\'t get diff files', shell= True)

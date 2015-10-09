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

if __name__ == '__main__':
  os.chdir('/home/buildguy')
  parser = argparse.ArgumentParser(description='''
    This script will pull down a pull request, build it, and compare it against master
  ''', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-b", "--buildCommand", help="Build command")
  parser.add_argument("-c", "--cleanupCommand", help="Cleanup command")
  args, unknown = parser.parse_known_args()
  if not args.buildCommand or not args.cleanupCommand:
    parser.print_help()
    raise Exception('buildCommand, and cleanupCommand are required')

  os.chdir('build-dir/base')
  os.mkdir('/home/buildguy/aggregate-metrics/working-dir')
  try:
    call_and_check(args.buildCommand, "Build failed", shell = True)
    call_and_check('{ find ./ -name \'surefire-reports\' -print0 && find ./ -name \'failsafe-reports\' -print0 && find ./ -wholename \'*bin/reports/*test/xml*\' -type d -print0; } | xargs -0 -I {} find {} -name \'*.xml\' -print0 | xargs -0 python ~/lib/test.python > ~/aggregate-metrics/working-dir/beforeTests.json', 'Couldn\'t aggregate surefire output before merge', shell= True)
    call_and_check('find ./ -name \'jacoco\' -print0 | xargs -0 -I {} find {} -name \'*.csv\' -print0 | xargs -0 python ~/lib/jacoco.python  > ~/aggregate-metrics/working-dir/jacocoUnitBefore.json', 'Couldn\'t aggregate jacoco unit test output before merge', shell= True)
    call_and_check('{ find ./ -name \'jacoco-integration\' -print0; } | xargs -0 -I {} find {} -name \'*.csv\' -print0 | xargs -0 python ~/lib/jacoco.python  > ~/aggregate-metrics/working-dir/jacocoIntegrationBefore.json', 'Couldn\'t aggregate jacoco integration test output before merge', shell= True)
    os.chdir('../head')
    call_and_check(args.buildCommand, "Build failed", shell = True)
    call_and_check('cat checkdiff.out | xargs ~/lib/checkstyle.py > ~/aggregate-metrics/checkstyle.json', 'Couldn\'t aggregate checkstyle output', shell= True)
    call_and_check('{ find ./ -name \'surefire-reports\' -print0 && find ./ -name \'failsafe-reports\' -print0 && find ./ -wholename \'*bin/reports/*test/xml*\' -type d -print0; } | xargs -0 -I {} find {} -name \'*.xml\' -print0 | xargs -0 python ~/lib/test.python > ~/aggregate-metrics/working-dir/afterTests.json', 'Couldn\'t aggregate surefire output after merge', shell= True)
    call_and_check('find ./ -name \'jacoco\' -print0 | xargs -0 -I {} find {} -name \'*.csv\' -print0 | xargs -0 python ~/lib/jacoco.python  > ~/aggregate-metrics/working-dir/jacocoUnitAfter.json', 'Couldn\'t aggregate jacoco unit test output after merge', shell= True)
    call_and_check('{ find ./ -name \'jacoco-integration\' -print0; } | xargs -0 -I {} find {} -name \'*.csv\' -print0 | xargs -0 python ~/lib/jacoco.python  > ~/aggregate-metrics/working-dir/jacocoIntegrationAfter.json', 'Couldn\'t aggregate jacoco integration test output after merge', shell= True)
    call_and_check('python ~/lib/testAggregate.python -b ~/aggregate-metrics/working-dir/beforeTests.json -a ~/aggregate-metrics/working-dir/afterTests.json > ~/aggregate-metrics/tests.json', 'Couldn\'t aggregate surefire output after merge', shell= True)
    call_and_check('python ~/lib/jacocoAggregate.python -b ~/aggregate-metrics/working-dir/jacocoUnitBefore.json -a ~/aggregate-metrics/working-dir/jacocoUnitAfter.json > ~/aggregate-metrics/jacocoUnit.json', 'Couldn\'t aggregate surefire output after merge', shell= True)
    call_and_check('python ~/lib/jacocoAggregate.python -b ~/aggregate-metrics/working-dir/jacocoIntegrationBefore.json -a ~/aggregate-metrics/working-dir/jacocoIntegrationAfter.json > ~/aggregate-metrics/jacocoIntegration.json', 'Couldn\'t aggregate surefire output after merge', shell= True)
  finally:
    call_and_check(args.cleanupCommand, "Cleanup failed", shell = True)

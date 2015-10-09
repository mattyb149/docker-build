#!/usr/bin/python

import argparse
import os
import json
import sys

def coveragePercent(coverage):
  result = {}
  for key, value in coverage.iteritems():
    if key.endswith('Covered'):
      keyPrefix = key[:-len('Covered')]
      missed = keyPrefix + 'Missed'
      total = int(value) + int(coverage[missed])
      if total > 0:
        result[keyPrefix + 'PercentCoverage'] = (100 * int(value)) / float(total)
  return result;

def diffPercent(before, after):
  result = {}
  for key, value in after.iteritems():
    if key in before:
      change = value - before[key]
      if abs(change) > 0.0001:
        result[key + 'Change'] = change
    else:
      result[key] = value
  return result

def diffGroup(before, after):
  result = {}
  for classname, results in after.iteritems():
    if classname not in before:
      result[classname] = diffPercent({}, coveragePercent(after[classname]))
    else:
      result[classname] = diffPercent(coveragePercent(before[classname]), coveragePercent(after[classname]))
  result = { classname: results for classname, results in result.iteritems() if len(results) > 0 }
  return result

def diff(before, after):
  result = {}
  for group, classresults  in after.iteritems():
    if group not in before:
      result[group] = diffGroup({}, classresults)
    else:
      result[group] = diffGroup(before[group], classresults)
  result = { group: classresults for group, classresults in result.iteritems() if len(classresults) > 0 }
  return result

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='''
  Utilitiy to diff mvn junit outputs
  ''', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-b", "--before", help="Before pr")
  parser.add_argument("-a", "--after", help="After pr")
  args = parser.parse_args()
  with open(args.before, 'r') as inputFile:
    before = json.load(inputFile)
  with open(args.after, 'r') as inputFile:
    after = json.load(inputFile)
  print(json.dumps(diff(before, after), sort_keys = True, indent = 2))

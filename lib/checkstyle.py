#!/usr/bin/python

import json
import os
import xml.etree.ElementTree as ET
import sys

def find_violations_file(rootDir, filename, fileFilter):
  tree = ET.parse(filename)
  results = {}
  for parentFile in tree.getroot().iter('file'):
    errors = set([])
    relName = os.path.relpath(parentFile.get('name'), rootDir)
    if fileFilter is None or relName in fileFilter:
      for error in parentFile.iter('error'):
        errors.add((error.get('line'), error.get('message'), error.get('column')))
      if len(errors) > 0:
        results[relName] = errors
  return results

def find_violations_recursively(rootDir, fileFilter):
  results = {}
  rootDir =  os.path.abspath(rootDir)
  for root, dirs, files in os.walk(rootDir):
    if 'checkstyle-result.xml' in files:
      filename = os.path.join(root, 'checkstyle-result.xml')
      for relName, errors in find_violations_file(rootDir, filename, fileFilter).iteritems():
        if relName in results:
          results[relName] |= (errors)
        else:
          results[relName] = errors
  resultList = []
  for relName, errors in results.iteritems():
    resultEntry = { 'filename': relName }
    errorList = [ error for error in errors ]
    errorList.sort(key = lambda tup: (tup[0], tup[1], tup[2]))
    resultEntry['errors'] = [ { 'line': tup[0], 'column': tup[2], 'message': tup[1] } for tup in errorList ]
    resultList.append(resultEntry)
  resultList.sort(key = lambda result: result['filename'])
  return resultList

if __name__ == '__main__':
  if len(sys.argv) > 1:
    fileList = [os.path.relpath(filename, os.getcwd()) for filename in sys.argv[1:]]
    result = {}
    result['fileList'] = fileList
    result['violations'] = find_violations_recursively(os.getcwd(), set(fileList))
    print(json.dumps(result, sort_keys = True, indent = 2))
  else:
    print('No changed files (maybe PR is already merged)')

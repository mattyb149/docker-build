#!/usr/bin/python

import os
import json
import sys
import xml.etree.ElementTree as ET

def parseElement(element, severity):
  return { 'severity' : severity, 'type' : element.get('type'), 'message': element.text }

def findFailuresAndErrors(filename, result):
  tree = ET.parse(filename)
  suiteName = tree.getroot().get('name')
  for suiteError in tree.getroot().findall('error'):
    if suiteName not in result:
      result[suiteName] = {}
    if 'suiteErrors' not in result[suiteName]:
      result[suiteName]['suiteErrors'] = []
    result[suiteName]['suiteErrors'].append(parseElement(suiteError, 'error'))
  for testCase in tree.getroot().iter('testcase'):
    className = testCase.get('classname')
    name = testCase.get('name')
    if className not in result:
      result[className] = {}
    for error in testCase.iter('error'):
      if 'caseErrors' not in result[className]:
        result[className]['caseErrors'] = {}
      result[className]['caseErrors'][name] = parseElement(error, 'error')
    for failure in testCase.iter('failure'):
      if 'caseErrors' not in result[className]:
        result[className]['caseErrors'] = {}
      result[className]['caseErrors'][name] = parseElement(failure, 'failure')
  return result

if __name__ == '__main__':
  result = {}
  for testXml in sys.argv[1:]:
    textXml = testXml.strip()
    if len(testXml) > 0:
      findFailuresAndErrors(testXml, result)
  result = { k: v for k, v in result.iteritems() if len(v) > 0 }
  print(json.dumps(result, sort_keys = True, indent = 2))

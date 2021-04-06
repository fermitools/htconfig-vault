#!/usr/bin/python3

import os
import sys
import yaml
import json

prog = 'parseconfig.py'
dir = '/etc/htvault-config/config.d'

def efatal(msg, e, code=1):
    print(prog + ': ' + msg + ': ' + str(e), file=sys.stderr)
    sys.exit(code)

def debug(msg):
    # print(msg)
    return

combined = {}

def merge(old, new):
    debug('type old: ' + str(type(old)) + ', type new: ' + str(type(new)))
    if type(new) is dict:
        if type(old) is not dict:
            raise Exception('type ' + str(type(new)) + ' does not match type ' + str(type(old)))
        for key in old:
            debug('old has key ' + key)
        for key in new:
            debug('checking new key ' + key)
            val = new[key]
            if key in old:
                try:
                    old[key] = merge(old[key], new[key])
                except Exception as e:
                    raise Exception('error merging ' + key + ': ' + str(e))
            else:
                old[key] = new[key]
        for key in old:
            debug('combined has key ' + key)
        return old
    if type(new) is list:
        if type(old) is not list:
            raise Exception('type ' + str(type(new)) + ' does not match type ' + str(type(old)))
        combinedlist = []
        knownnames = set()
        for oldval in old:
            if type(oldval) is dict and 'name' in oldval:
                for newval in new:
                    if 'name' in newval and newval['name'] == oldval['name']:
                        knownnames.add(newval['name'])
                        try:
                            debug('merging ' + newval['name'])
                            combinedlist.append(merge(oldval, newval))
                        except Exception as e:
                            raise Exception('error merging ' + newval['name'] + ': ' + str(e))
                if oldval['name'] not in knownnames:
                    debug('adding unmerged ' + oldval['name'])
                    knownnames.add(oldval['name'])
                    combinedlist.append(oldval)
            else:
                    debug('adding non-named dict')
                    combinedlist.append(oldval)
        for newval in new:
            if type(newval) is not dict or 'name' not in newval or newval['name'] not in knownnames:
                debug('adding new item ' + str(newval) + ' to ' + str(knownnames))
                combinedlist.append(newval)
        return combinedlist
    debug('returning non-dict non-list ' + str(new))
    return new


for f in sorted(os.listdir(dir)):
    if f[-5:] != '.yaml':
        continue
    filename = dir + '/' + f
    try:
        with open(filename) as fd:
            data = yaml.load(fd)
    except Exception as e:
        efatal('error loading yaml in ' + filename, e)
                 
    debug('merging ' + filename +': ' + str(json.dumps(data)))
    try:
        combined = merge(combined, data)
    except Exception as e:
        efatal('error merging data from ' + filename, e)
    debug('combined: ' + str(json.dumps(combined)))

print(str(json.dumps(combined)))


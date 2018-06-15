from lib import dashboard, sites, url
from datetime import datetime, timedelta
import sys, os
import json
import pprint

endpoints = sites.getInvertedSRMEndpoints()
for site in endpoints:
  print site
  print endpoints[site]

with open('data.json') as f:
  data = json.load(f)

#for key, value in data.iteritems() :
#      pprint.pprint(value)

for tier in data['responses']:
  for tag in tier['aggregations']['source']['buckets']:
    source_se=tag['key']
    #pprint.pprint(tag['key'])
    for dest in tag['dest']['buckets']:
      dest_se=dest['key']
      #pprint.pprint('-->' + dest['key'])
      total_jobs = dest['doc_count']
    #  pprint.pprint("TOTAL: "+str(dest['doc_count']))
      for fts in dest['filestates']['buckets']:
        status = fts['key']
        if 'FAILED' in status:
          failed = fts['doc_count']
          #pprint.pprint("FAILEDD "+str(failed))
    #      successrt = float(failed/total_jobs)*100
        else:
          successrt = 100
       
      print '-- Analyzing pair '+source_se+' --> '+dest_se
      print successrt
        #print fts['key']+', '+str(fts['doc_count'])
        

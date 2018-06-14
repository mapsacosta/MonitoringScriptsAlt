from lib import dashboard, sites, url
from datetime import datetime, timedelta
import sys, os
import json
import pprint

#endpoints = sites.getSRMEndpoints()
#for site in endpoints:
  #print site
  #print sites.getTier(site)
  #print endpoints[site]

with open('data.json') as f:
  data = json.load(f)

#for key, value in data.iteritems() :
#      pprint.pprint(value)

for tier in data['responses']:
  for tag in tier['aggregations']['source']['buckets']:
    pprint.pprint('--------------------- '+ tag['key']+ '---------------------')
    for dest in tag['dest']['buckets']:
      pprint.pprint('-->' + dest['key'])
      pprint.pprint(dest['doc_count'])
      for fts in dest['filestates']['buckets']:
        print fts['key']+', '+str(fts['doc_count'])
        

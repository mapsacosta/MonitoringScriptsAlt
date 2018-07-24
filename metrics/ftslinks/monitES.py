#!/usr/bin/python
#@author Maria Acosta - CMS SST

import requests
import time
import argparse
import dateutil.parser
from datetime import datetime, timedelta
import simplejson as json
import os


def buildQueryFile(date_from, date_to):
  
  #Convert input dates to str in a format ES can understand
  dateFormat="%Y-%m-%dT%H:%M:%S"
  date_from_str = datetime.strftime(date_from, dateFormat)
  date_to_str = datetime.strftime(date_to, dateFormat)

  grafanaLine = '{"search_type":"query_then_fetch","ignore_unavailable":true,"index":["monit_prod_fts_raw_state_*"]}'
  queryLine = '{"size":0,"query":{"bool":{"must":[{"match_all":{}},{"match_phrase":{"data.vo":{"query":"cms"}}},{"range":{"metadata.event_timestamp":{"gte":"'+date_from_str+'","lte":"'+date_to_str+'","format":"date_hour_minute_second"}}}],"must_not":[]}},"_source":{"excludes":[]},"aggs":{"source":{"terms":{"field":"data.source_se","size": 5000,"order":{"_count":"desc"}},"aggs":{"dest":{"terms":{"field":"data.dest_se","size": 5000,"order":{"_count":"desc"}},"aggs":{"reason":{"terms":{"field":"data.reason","size":5000,"order":{"_count":"desc"}}}}}}}}}'
  q_out_fname=date_from_str+"_15_query.json"

  with open(q_out_fname, 'w+') as out:  
    out.write(grafanaLine+"\n")
    out.write(queryLine+"\n")
    out.close()

  return q_out_fname
  
def fetch(fname):
  endpoint = "https://monit-grafana.cern.ch/api/datasources/proxy/8332/_msearch"
  headers = {"Authorization":"Bearer eyJrIjoiWGdESVczR28ySGVVNFJMMHpRQ0FiM25EM0dKQm5HNTEiLCJuIjoiZnRzX2NsaSIsImlkIjoyNX0=","Content-type": "application/json"}
  compl=file(fname,'rb').read()
  response = requests.post(endpoint,data=compl,headers=headers).json()
  return json.loads(json.dumps(response))

def getResults(date_from,date_to):
  return fetch(buildQueryFile(date_from,date_to))

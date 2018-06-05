from lib import dashboard, sites, url
from datetime import datetime, timedelta
import sys, os
import json
import pprint

endpoints = sites.getSRMEndpoints()
for site in endpoints:
  print site
  print sites.getTier(site)
  print endpoints[site]

#!/usr/bin/python
# ########################################################################### #
# python script to query PhEDEX agent logs in order to obtain recent info-    #
# rmation about FTS servers usage by CMS sites. It can generate a file        #
# or write to stdout. There are two possible formats:                         #
#   > List: Tab spaced list of sites and its correspondent FTS server         #
#   > Server: A summary of the usage of FTS serverw within the CMS VO         #
# @author: Maria A. CMS SST                                                   #
# Last modification:2018-Aug-21  Maria P. Acosta                              #
# ########################################################################### #

from __future__ import division

import dateutil.parser
import getpass, socket
import traceback
import time, calendar
import requests
import argparse
from decimal import *
from datetime import datetime, timedelta
import sys, os
import simplejson as json
import urllib3
import pprint
import shlex

def fetch(writeFile):
  if writeFile:
      urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
      response = json.loads(json.dumps(requests.get('https://cmsweb.cern.ch/phedex/datasvc/json/prod/agentlogs?node=T*', verify=False).json()))
      with open('data.json', 'w+') as f:
         json.dump(response, f)
      f.close()
      with open('data.json') as f:
         data = json.load(f)  
      return populate(data)
  else:
      urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
      response = json.loads(json.dumps(requests.get('https://cmsweb.cern.ch/phedex/datasvc/json/prod/agentlogs?node=T*', verify=False).json()))
      return populate(response)

#with open('data.json') as f:
#  data = json.load(f)  

hosts={}

def add(node,ftsServer):
    try:
        hosts[node]=ftsServer
    except Exception:
        print(traceback.format_exc())
    except:
        return

def populate(data):
    for agent in data['phedex']['agent']:
        for log in agent['log']:
            current = log['message']['$t']
            if 'FTS3' not in current:
                continue
            else:
                splt = current.split('-nodes')
                node = splt[1].split('-')[0].strip()
                ftsServer = splt[1].split('-service')[1].split('-')[0].strip()
                add(node,ftsServer)
    return hosts

def getFTSserver(sitename):
  return whichFTS.hosts[sitename]

def countTier(sList):
    tier = {}
    tier['0'] = 0
    tier['1'] = 0
    tier['2'] = 0
    tier['3'] = 0
    for site in sList:
        if 'T0' in site:
            tier['0'] += 1
        elif 'T1' in site:
            tier['1'] += 1
        elif 'T2' in site:
            tier['2'] += 1
        else:
            tier['3'] += 1
    return tier

def writefile(param='list',file=sys.stdout):
  now = time.strftime("%Y-%b-%d %H:%M:%S UTC", time.gmtime())
  file.write(("#\n# List of FTS servers curr"
    "ently being used by CMS PhEDEx endpoints. \n# @author macostaf \n# Written at %s by %s\n#" +
    " in account %s on node %s\n# " +
    " Maintained by cms-comp-ops-site-support-team@NOSPAMPLEASE.cern.ch\n"+
    "# ===========================================\n\n") %
    (now, sys.argv[0], getpass.getuser(), socket.gethostname()))
  if 'server' in param:
      fnal = []
      cern = []
      ral = []
      for k in sorted(hosts.iterkeys()):
          if 'fnal.gov' in hosts[k]:
              fnal.append(k)
              continue
          elif 'cern.ch' in hosts[k]:
              cern.append(k)
              continue
          else:
              ral.append(k)
      #Process FNAL
      file.write("# ==== FNAL FTS ==== #"+
                 "\n T0s: "+ str(countTier(fnal)['0'])+
                 "\n T1s: "+ str(countTier(fnal)['1'])+
                 "\n T2s: "+ str(countTier(fnal)['2'])+
                 "\n T3s: "+ str(countTier(fnal)['3'])+
                 "\n Total: "+ str(len(fnal))+'\n\n')
      for site in fnal:
          file.write("%s\n" % site)
      file.write("\n")

      file.write("# ==== CERN FTS ==== #"+
                 "\n T0s: "+ str(countTier(cern)['0'])+
                 "\n T1s: "+ str(countTier(cern)['1'])+
                 "\n T2s: "+ str(countTier(cern)['2'])+
                 "\n T3s: "+ str(countTier(cern)['3'])+
                 "\n Total: "+ str(len(cern))+'\n\n')
      for site in cern:
          file.write("%s\n" % site)
      file.write("\n")

      file.write("# ==== RAL FTS ==== #"+
                 "\n T0s: "+ str(countTier(ral)['0'])+
                 "\n T1s: "+ str(countTier(ral)['1'])+
                 "\n T2s: "+ str(countTier(ral)['2'])+
                 "\n T3s: "+ str(countTier(ral)['3'])+
                 "\n Total: "+ str(len(ral))+'\n\n')
      for site in ral:
          file.write("%s\n" % site)
      file.write("\n")



  elif 'list' in param:
      for k in sorted(hosts.iterkeys()):
          file.write("%s\t%s\n" % (k,hosts[k]))

def whichFTS(sitename):
    populate()
    return hosts(sitename)

#fetch(True)
#fetch(False)
#writefile('server')
#writefile()

if __name__ == '__main__':
  #
    parserObj = argparse.ArgumentParser(description="Script that generates information on FTS servers and Site within CMS ")
    parserObj.add_argument("-l", dest="list", action="store_true",
                           help="Will generate a tab spaced list of sites with the latest FTS server used by the site as known by PhEDEx")
    parserObj.add_argument("-s", dest="server", action="store_true",
                           help="Will generate a summary of usage of FTS servers by CMS sites")
    parserObj.add_argument("-f", dest="filename", action="store_true",
                           help="If the user requieres, output will be written in the file specified")

    argStruct = parserObj.parse_args()
    if argStruct.l and argStruct.f:
        fetch(False)
        writefile()
    elif argStruct.l and argStruct.s and argStruct.f:
        fetch(False)
        writefile()
        writefile("server")
    elif argStruct.s and argStruct.f:
        fetch(False)
        writefile("server")
    else:
        fetch(False)
        writefile()
    



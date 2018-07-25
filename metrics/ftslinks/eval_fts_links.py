from __future__ import division
import dateutil.parser
import monitES
from optparse import OptionParser
from decimal import *
from datetime import datetime, timedelta
from lib import dashboard, sites, url
import sys, os
import simplejson as json
import pprint

def  main():
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
    parser.add_option("-d", "--date",
                      dest="inputDate",
                      help="Date from which to fetch the results for FTS transfers in format %Y-%m-%dT%H:%M:%SZ ")
    parser.add_option("-o", "--outputDir",
                      dest="outputDir",
                      help="Directory in which to save the output")
    (options, args) = parser.parse_args()
    if options.inputDate is None:
        print "Please input a date with the --date option"
        exit(-1)
    else:
        try:
            datetmp = dateutil.parser.parse(options.inputDate, ignoretz=True)
        except:
            print "I couldn't recognize the date, please give me one like 2018-12-31T23:59:59"
            exit(-1)
    if options.outputDir is None:
        print "Please add a directory with option --outputDir"
        exit(-1)
    else:
        if os.path.isdir(options.outputDir) == False:
            print options.outputDir + " is not a valid directory or you don't have read permissions"
            exit(-1)
# Constants:
    # Dashboard API for Hammercloud
    # replace (site, startTimeStamp, endTimeStamp)
    interval = 15
    dateFrom = datetmp- timedelta(minutes=datetmp.minute % interval,
                             seconds=datetmp.second,
                             microseconds=datetmp.microsecond)
    dateTo = dateFrom + timedelta(minutes=interval)
    OUTPUT_FILE_NAME = os.path.join(options.outputDir,"fts15min.txt")
    print "Retrieving ES data for FTS files from " + str(dateFrom) + " to " + str(dateTo)

    data = monitES.getResults(dateFrom,dateTo)
    print len(data)
    print "Starting process"
    process15Min(data)
    dump(dateFrom,OUTPUT_FILE_NAME)

active_sites = []
  
def siteByName(sitename):
  return next(iter(filter(lambda site: site.site_name == sitename,  active_sites)),None) 

def siteExists(nsite):
  if next(iter(filter(lambda site: site.site_name == nsite, active_sites)),None):
    return True
  else:
    return False

def dump(dateFrom,out):
  rates = []
  OutputFile = open(out, 'w')
  for site in active_sites:
    if site.total_files > 0:
      OutputFile.write(str(dashboard.entry(date = dateFrom.strftime("%Y-%m-%d %H:%M:%S"), name = site.site_name, value = site.srate, color = site.color, url = "https://fts3.cern.ch:8449/fts3/ftsmon/#/?page=3&vo=cms&source_se=&dest_se=&time_window=1"))+'\n')
  print "\n-- FTS Success rate output written to %s" % out
  OutputFile.close()

#    next((response for site in self.active_sites if site.site_name == sitename), None)
 #   return response
def process15Min(data):
  for tier in data['responses']:
    for src in tier['aggregations']['source']['buckets']:
      src_data=src['key'].split("://")
      src_se=src_data[1]
      src_protocol=src_data[0]
      src_site = getOwnerSite(src_se)
      if src_site:
        #print "Source start "+src_site
        if siteExists(src_site):
          source=siteByName(src_site)
        else:
          source=Site(src_site)
          active_sites.append(source)
        for dest in src['dest']['buckets']:
          dest_data=dest['key'].split("://")
          dest_se=dest_data[1]
          dest_protocol=dest_data[0]
          dest_site = getOwnerSite(dest_se)
          if dest_site:
            #print "Destionation start " + dest_site
            if siteExists(dest_site):
              destination=siteByName(dest_site)
            else:
              destination=Site(dest_site)
              active_sites.append(destination)
            n_files = 0
            for fts in dest['reason']['buckets']:
              status = fts['key']
              n_files = fts['doc_count']
              if status:
                blame(status,n_files,source,destination)
                continue
              else:
                continue
                #source.successful_files += n_jobs
                #source.total_files += n_jobs
            destination.calculate()
        source.calculate()
      else:
        continue

def blame(message,n_files,src,dest):
  if "SOURCE" in message:
    src.f_other += n_files
    src.total_files += n_files
  elif "DESTINATION" in message:
    dest.f_quota += n_files
    dest.total_files += n_files
  elif "ipc command failed" in message.lower():
    src.f_undecided += n_files
    dest.f_undecided += n_files
  else:
    src.total_files += n_files
    src.successful_files += n_files
 
class Site:

  def __init__(self, cms_name):

    self.site_name = cms_name
    self.endpoints = getEndpoints (cms_name)
    self.tier = sites.getTier(self.site_name)

    #Statistical attributes
    self.total_files = 0
    self.successful_files = 0

    #Number of failed fts files categorized by type (undecided is not counted in the final rate)
    self.f_undecided = 0
    self.f_quota = 0
    self.f_permissions = 0
    self.f_unreachable = 0
    self.f_nosuchfile = 0
    self.f_other = 0
    self.f_total = 0

    #Success rate before categorizing error messages
    self.color = "Gray"
    self.srate = "N/A"

  def calculate(self):
    self.f_total = self.f_quota+self.f_permissions+self.f_unreachable+self.f_nosuchfile+self.f_other
    fl_srate = 0.0

    if self.total_files > 0:
      fl_srate = (1-(self.f_total/self.total_files))*100
      self.srate = format(fl_srate,'.1f')
      if fl_srate >= 80.0:
        self.color = "Green"
      elif fl_srate >= 40.0 and fl_srate < 80.0:
        self.color = "Yellow"
      elif fl_srate < 40.0:
        self.color = "Red"
    else:
      self.srate = "N/A"
      self.color = "Gray"

def getEndpoints(site):
  try:
    return sites.getSRMEndpoints()[site]
  except:
    return None

def getOwnerSite(endpt_hostname):
  try:
    return sites.getInvertedSRMEndpoints()[endpt_hostname]
  except:
    return None

if __name__ == "__main__":
  #go = ftsMetric()
  main()





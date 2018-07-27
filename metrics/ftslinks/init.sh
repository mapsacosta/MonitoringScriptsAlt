#!/bin/sh

export SSTBASE=/afs/cern.ch/user/m/macostaf/private/MonitoringScripts/
export CERTS=$SSTBASE/certs
export PYTHONPATH="$PYTHONPATH:$SSTBASE"
export SSTOUT="$SSTBASE/output"
export SSTLOG="$SSTBASE/log"
#export SSTMAIL="cms-comp-ops-site-support-team@cern.ch"
export SSTMAIL="macostaf@cern.ch"
SSTINITERR="$SSTLOG/sstInit.log"

if [ ! -d "$SSTOUT" ]; then
    mkdir $SSTOUT
fi

if [ ! -d "$SSTLOG" ]; then
    mkdir $SSTLOG
fi

#!/bin/bash
source init.sh
OUT=$SSTBASE/output/metrics/ftslinks

if [ ! -d "$OUT" ]; then
      mkdir -p $OUT
    fi

date=$(date "+%Y-%m-%dT%H:%M:%SZ" --utc -d "15 minutes ago")
echo $date

python eval_fts.py $date -q -v 

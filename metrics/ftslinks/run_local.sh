cd $(dirname $(readlink -f "${BASH_SOURCE[0]}"))
source init.sh
OUT=$SSTBASE/output/metrics/ftslinks

if [ ! -d "$OUT" ]; then
	    mkdir -p $OUT
    fi

    python  getlinks.py 

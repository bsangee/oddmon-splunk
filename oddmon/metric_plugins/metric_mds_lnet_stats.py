#!/usr/bin/env python

import os
import logging
import json
import time
from collections import defaultdict
try:
    from oddmon import lfs_utils
except:
    import lfs_utils

logger = None


class G:
    fsname = None
    mdtnames = None
    stats = defaultdict(lambda: defaultdict(int))


def metric_init(name, config_file, is_subscriber=True,
                loglevel=logging.DEBUG):
    global logger
    logger = logging.getLogger("app.%s" % __name__)
    rv = True
    
    G.fsname, G.mdtnames = lfs_utils.scan_targets(OSS=False)
    if not G.mdtnames:
        logger.warn("No MDT's found.  Disabling plugin.")
        rv = False
    elif not G.fsname:
        logger.error("MDT's found, but could not discern filesystem name. "
                     "(This shouldn't happen.)  Disabling plugin.")
        rv = False
    
    return rv


def metric_cleanup(is_subscriber=True):
    pass


def get_stats():

    if G.fsname is None:
        logger.error("No valid file system ... skip")
        return ""

    update()

    return json.dumps(G.stats)


def save_stats(msg):
    stats = json.loads(msg)
    # msg (and thus stats) is organized as a dictionary with target (OST or
    # MDT) names for keys.  The associated values are themselves lists of
    # dictionaries where each dictionary is the key/value data for one job.

    for target in stats.keys():
        jobList = stats[target]
        for job in jobList:
            # convert the python structure into an event string suitable
            # for Splunk and write it out
                event_str = "  send_count=%d  recv_count=%d send_length=%d recv_length=%d MDS=%s" %\
                            (int(job["send_count"]), int(job["recv_count"]),
                             int(job["send_length"]), int(job["recv_length"]), str(target))

    		stats_logger.info(event_str)


def read_lnet_stats(f):
    """
    expect input of a path to lnet stats
    return a dictionary with key/val pairs
    """
    ret = {'send_count': 0, 'recv_count': 0, 'send_length':0, 'recv_length': 0}

    pfile = os.path.normpath(f) + "/stats"
    with open(pfile, "r") as f:
            for line in f:
                chopped = line.split()
                if chopped[3]:
                    ret["send_count"] = int(chopped[3])
                if chopped[4]:
                    ret["recv_count"] = int(chopped[4])
                if chopped[7]:
                    ret["send_length"] = int(chopped[7])
                if chopped[8]:
                    ret["recv_length"] = int(chopped[8])


    if ret['send_count'] == 0 and ret['recv_count'] == 0 and ret['send_length'] == 0 and ret['recv_length'] == 0 :
        return None

    return ret


def update():

        fpath = '/proc/sys/lnet'
        ret = read_lnet_stats(fpath)
        if ret:
            G.stats = ret

if __name__ == '__main__':
    metric_init("mds-lnet-stats")
    while True:
        print get_stats()
        time.sleep(5)
    metric_cleanup()

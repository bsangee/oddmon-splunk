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

    for target in stats.keys():
        jobList = stats[target]
        for job in jobList:
            # convert the python structure into an event string suitable
            # for Splunk and write it out
                event_str = "open=%d  close=%d unlink=%d getattr=%d  getxattr=%d statfs=%d MDS=%s" %\
                            (int(job["open"]), int(job["close"]),
                             int(job["unlink"]), int(job["getattr"]),
			     int(job["getxattr"]), int(job["statfs"]), str(target))

    		stats_logger.info(event_str)



def read_mdt_stats(f):
"""
    expect input of a path to mdt stats
    return a dictionary with key/val pairs
    """
    ret = {}
    pfile = os.path.normpath(f) + "/md_stats"
    with open(pfile, "r") as f:
            for line in f:
                chopped = line.split()
                if chopped[0] == "open":
                    ret["open"] = int(chopped[1])
                if chopped[0] == "close":
                    ret["close"] = int(chopped[1])
                if chopped[0] == "unlink":
                    ret["unlink"] = chopped[1]
                if chopped[0] == "getattr":
                    ret["getattr"] = int(chopped[1])
                if chopped[0] == "getxattr":
                    ret["getxattr"] = int(chopped[1])
                if chopped[0] == "statfs":
                    ret["statfs"] = int(chopped[1])


    return ret



def update():

    for mdt in G.mdtnames:
        fpath = '/proc/fs/lustre/mdt/' + mdt
        ret = read_mdt_stats(fpath)
        if ret:
            G.stats[mdt] = ret


if __name__ == '__main__':
    metric_init("mdt-stats")
    while True:
        print get_stats()
        time.sleep(5)
    metric_cleanup()

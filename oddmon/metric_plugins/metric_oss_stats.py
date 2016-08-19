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
    ostnames = None
    stats = defaultdict(lambda: defaultdict(int))


def metric_init(name, config_file, is_subscriber=False,
                loglevel=logging.DEBUG):
    global logger
    logger = logging.getLogger("app.%s" % __name__)
    rv = True
    
    G.fsname, G.ostnames = lfs_utils.scan_targets(OSS=True)
    if not G.ostnames:
        logger.warn("No OST's found.  Disabling plugin.")
        rv = False
    elif not G.fsname:
        logger.error("OST's found, but could not discern filesystem name. "
                     "(This shouldn't happen.)  Disabling plugin.")
        rv = False
    
    return rv


def metric_cleanup(is_subscriber=False):
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
                event_str = "cpu=%f  mem=%d OSS=%s" %\
                            (float(job["cpu"]), int(job["mem"]), str(target))

		stats_logger.info(event_str)


def read_oss_stats(f):
    ret = {'cpu': 0, 'mem': 0}
    count=1
    cmd = subprocess.Popen('sar 1 1 -r -u', shell=True, stdout=subprocess.PIPE)
    for line in cmd.stdout:
                chopped = line.split()
                if chopped and count == 10:
                   ret['cpu'] = 100 - float(chopped[-1]);  #idle cpu
                if chopped and count == 13:
                   ret['mem'] = chopped[3];
                count = count+1;


    return ret



def update():


        ret = read_oss_stats()
        if ret:
            G.stats = ret

if __name__ == '__main__':
    metric_init("oss-stats")
    while True:
        print get_stats()
        time.sleep(5)
    metric_cleanup()

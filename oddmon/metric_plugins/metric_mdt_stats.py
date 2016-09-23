#!/usr/bin/env python

import os
import ConfigParser
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
    global logger, stats_logger
    logger = logging.getLogger("app.%s" % __name__)
    rv = True

    if is_subscriber is True:
        G.fsname, G.mdtnames = lfs_utils.scan_targets(OSS=False)
        if not G.mdtnames:
                logger.warn("No MDT's found.  Disabling plugin.")
                rv = False
        elif not G.fsname:
                logger.error("MDT's found, but could not discern filesystem name. "
                             "(This shouldn't happen.)  Disabling plugin.")
                rv = False
    #else:
        # config file is only needed for the location of the
        # stats_logger file, and that's only needed on the
        # subscriber side
        config = ConfigParser.SafeConfigParser()
        try:
            config.read(config_file)
            G.save_dir = config.get(name, "save_dir")
        except Exception, e:
            logger.error("Can't read configuration file")
            logger.error("Exception: %s" % e)
            rv = False

        # TODO: this code block should probably be inside the exception handler
        # log to file until reaching maxBytes then create a new log file
        stats_logger = logging.getLogger("mdt_stats.%s" % __name__)
        stats_logger.propagate = False
        stats_logger_name = G.save_dir+os.sep+"mdt_stats_log.txt"
        logger.debug("Stats data saved to: %s" % stats_logger_name)
        stats_logger.addHandler(
            logging.handlers.RotatingFileHandler(stats_logger_name,
                                                 maxBytes=1024*1024*1024,
                                                 backupCount=1))
        stats_logger.setLevel(logging.DEBUG)


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
    event_str = "snapshot: %d" % int(time.time())
    stats_logger.info(event_str)

    stats_logger.info(stats)


def read_mdt_stats(f):
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
                                                          
                                                              

Last login: Fri Sep 23 12:49:59 on ttys001
Sangeethas-MacBook-Pro:~ sangeethabs$ spark
spark@hydra.cs.vt.edu's password: 
Warning: untrusted X11 forwarding setup failed: xauth key data not generated
Last login: Fri Sep 23 11:46:33 2016 from 172.30.64.105
[spark@hydra ~]$ cd RMQ
-bash: cd: RMQ: No such file or directory
[spark@hydra ~]$ ssh lustre@hulk2
lustre@hulk2's password: 
Last login: Fri Sep 23 11:50:10 2016 from hydra
[lustre@hulk2 ~]$ cd RMQ
[lustre@hulk2 RMQ]$ cd oddmon/
[lustre@hulk2 oddmon]$ git status
# On branch splunk_mods
# Changed but not updated:
#   (use "git add <file>..." to update what will be committed)
#   (use "git checkout -- <file>..." to discard changes in working directory)
#
#	modified:   monctl.py
#	modified:   oddmon.cfg.sample
#	modified:   oddmon/metric_plugins/metric_ost_stats.py
#
# Untracked files:
#   (use "git add <file>..." to include in what will be committed)
#
#	LOG.aggregator
#	oddmon.db
#	oddmon/metric_plugins/metric_mdt_stats.py
#	oddmon/metric_plugins/metric_oss_lnet_stats.py
#	oddmon/metric_plugins/metric_oss_stats.py
no changes added to commit (use "git add" and/or "git commit -a")
[lustre@hulk2 oddmon]$ vim oddmon.cfg.sample 
[lustre@hulk2 oddmon]$ vim oddmon/metric_plugins/metric_ost_stats.py
















    return json.dumps(G.stats)


def save_stats(msg):

        stats = json.loads(msg)
        stats_logger.info(stats)


def read_ost_stats(f):
    """
    expect input of a path to ost stats
    return a dictionary with key/val pairs
    """
    ret = {'read_bytes_sum': 0, 'write_bytes_sum': 0}

    pfile = os.path.normpath(f) + "/stats"
    with open(pfile, "r") as f:
            for line in f:
                chopped = line.split()
                if chopped[0] == "snapshot_time":
                    ret["snapshot_time"] = chopped[1]
                if chopped[0] == "write_bytes":
                    ret["write_bytes_sum"] = int(chopped[6])
                if chopped[0] == "read_bytes":
                    ret["read_bytes_sum"] = int(chopped[6])

    if ret['read_bytes_sum'] == 0 and ret['write_bytes_sum'] == 0:
        return None

    return ret


def update():

    for ost in G.ostnames:
        fpath = '/proc/fs/lustre/obdfilter/' + ost
        ret = read_ost_stats(fpath)
        if ret:
            G.stats[ost] = ret


if __name__ == '__main__':
    metric_init("ost-stats")
    while True:
        print get_stats()
        time.sleep(5)
    metric_cleanup()
                                                                                                                                                                   126,9         Bot

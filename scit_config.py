#!/usr/bin/env python
import os
from ConfigParser import ConfigParser


#config handler
def getScitConfig(config_file="/root/openstack/pys/scit-sys/confs/scit.conf"):
    cf = ConfigParser()
    cf.read(config_file)
    scit_config = {}

    #read the section infos
    for i in cf.sections():
        scit_config[i] = {}
        for j in cf.options(i):
            scit_config[i][j] = cf.get(i,j)
    return scit_config


def initScitSetting(floatips):
    os.popen("true > /root/.ssh/known_hosts")
    os.popen("true > /etc/ansible/hosts")

    #write into /etc/ansible/hosts file
    f = open("/etc/ansible/hosts", "w")
    f.write("\n".join(floatips))
    f.close()

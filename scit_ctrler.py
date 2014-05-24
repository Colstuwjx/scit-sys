#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import time
import types
from scit_config import * 
from scit_network import initScitNetwork
from scit_log import initLogHandler
from openstack_api import *


class ScitCtrler:
    '''
        Scit-DNS system central ctrler
        Version: V0.9
        
        1 init the ctrler
          * read the scit configuration
          * setup the log handler
          * net,vm,ssh,ansible env init
          * start vm and wait ok
          * collect the system info and write into db
        2 rotate-clean and check alghorithem
          * wait timeout or test.ping not ok or check failed vm
          * if there is a clean server, then rotate it
          * otherwise, throw warning and wait 3 times
          * forcely delete the cleanning vm and re-create it
          * if still don't work, check the online vm status
          * if failed again, system hang up.        
    '''
    #value defs
    #default settings
    CONFIG_FILE = "confs/scit.conf"
    CONFIG_VAL = {}
    FILE_PATH = ""

    #create vm timeout settings, use second
    SCIT_T = 360

    #vm life cycle
    SCIT_D = 2400

    #total vm
    SCIT_N = 3

    #online vm nums
    SCIT_M = 2

    #retry vm creation times
    SCIT_R = 5

    #vm init script
    INIT_SCRIPT = ""

    #private defs
    __scit_logger = None


    def __init__(self):
        self.FILE_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__)))
        self.CONFIG_VAL = getScitConfig(self.CONFIG_FILE)

        #init the log handler
        #logging_file = self.CONFIG_VAL["log"]["log_fullpath"]
        #if not logging_file:
        #    logging_file = self.FILE_PATH + "/logs/scit_run.log"
        #self.__scit_logger = initLogHandler(logging_file)
        self.__scit_logger = initLogHandler()

        #init the vm boot script settings
        script = self.CONFIG_VAL["scit"]["scit_init_script"]
        if not script:
            script = self.FILE_PATH + "/scripts/init.sh"
        self.INIT_SCRIPT = script

        #read conf and set args
        self.initScitConf()


    def initScitConf(self):
        if not self.CONFIG_VAL:
            return None

        try:
            self.SCIT_T = int(self.CONFIG_VAL["scit"]["scit_timeout"])
        except:
            pass

        try:
            self.SCIT_D = int(self.CONFIG_VAL["scit"]["scit_deadline"])
        except:
            pass

        try:
            self.SCIT_N = int(self.CONFIG_VAL["scit"]["scit_servers_N"])
        except:
            pass

        try:
            self.SCIT_M = int(self.CONFIG_VAL["scit"]["scit_servers_M"])
        except:
            pass

        try:
            self.SCIT_R = int(self.CONFIG_VAL["scit"]["scit_clean_retry"])
        except:
            pass

        return True


    #clean the scit-dns env
    def initScitCtrler(self):
        print "start init scit-dns system.."
        self.__scit_logger.info("start init scit-dns system.")

        #init the nova,clear all vms
        ta = time.time() 

        if not clear_nova_vm(self.__scit_logger):
            print "error found when clear nova vm"
            self.__scit_logger.error("init vm env stopped, exit..")
            sys.exit(1)

        tb = time.time()
        t = int(tb-ta + (tb-ta - int(tb-ta))/1.0)

        print "init nova vms complete"
        print "Total: " + str(t) + "s."
        self.__scit_logger.info("init nova vms complete, time: " + str(t) + " s.")

        #init the scit-dns network env
        nets_ret = initScitNetwork(self.__scit_logger, self.SCIT_M)
        if not nets_ret:
            self.__scit_logger.error("init network env stopped, exit..")
            sys.exit(1)

        print "init network env complete."
        self.__scit_logger.info("init network env complete.")

        #init the sys env
        initScitSetting(nets_ret)

        print "clear the ssh known_list and ansible hosts.."
        self.__scit_logger.info("init the ssh set and ansible hosts.")

        print "scit-dns system init complete!"
        self.__scit_logger.info("scit-dns init finished.")


    #start rotate and clean task
    def rotateClean(self):


#scit-dns system ctrler
def main():
    sc = ScitCtrler()
    sc.initScitCtrler()


#start program
if __name__ == "__main__":
    sys.exit(main())

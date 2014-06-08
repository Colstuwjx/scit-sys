#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import time
import types
import threading
from scit_config import * 
from scit_network import initScitNetwork
from scit_log import initLogHandler
from scit_db import *
from scit_resolv import *
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
          * otherwise, throw warning and wait
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

    #vm base name
    VM_BASENAME = ""

    #float ips
    FLOAT_IPS = []

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

        #init the vm basename
        basename = self.CONFIG_VAL["instance"]["instance_basename"]
        if not basename:
            basename = "SCIT_VM"
        self.VM_BASENAME = basename

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
            self.SCIT_N = int(self.CONFIG_VAL["scit"]["scit_servers_n"])
        except:
            pass

        try:
            self.SCIT_M = int(self.CONFIG_VAL["scit"]["scit_servers_m"])
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

        print "args: \nSCIT_M: " + str(self.SCIT_M) + ", SCIT_N: " + str(self.SCIT_N)
        self.__scit_logger.info("Use args, SCIT_N: " + str(self.SCIT_N) + ", SCIT_M: " + str(self.SCIT_M) + ".")

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

        self.FLOAT_IPS = nets_ret

        print "init network env complete."
        self.__scit_logger.info("init network env complete.")

        #init the sys env
        initScitSetting(nets_ret)

        print "clear the ssh known_list and ansible hosts.."
        self.__scit_logger.info("init the ssh set and ansible hosts.")

        #truncate the mysqldb
        runSQL("TRUNCATE TABLE scit_vm;") 

        print "start creating vms.."
 
        #init the vms
        for i in xrange(self.SCIT_N):
            vm_name = self.VM_BASENAME + "%02d" % i
            print "try create vm: " + vm_name
            self.__scit_logger.info("try create vm: " + vm_name + " without floatip..")

            if not create_nova_vm(self.__scit_logger, vm_name, self.INIT_SCRIPT):
                print "Error when create vm: " + vm_name
                self.__scit_logger.error("failed create vm: " + vm_name)
                sys.exit(1)
            print "complete create vm: " + vm_name
            self.__scit_logger.info("vm: " + vm_name + " created!")

            if i < self.SCIT_M:
                vm_extra_set(self.__scit_logger, vm_name, self.FLOAT_IPS[i])

        print "scit-dns system init complete!"
        self.__scit_logger.info("scit-dns init finished.")

        print "starting cleaner and watcher."
        self.__scit_logger.info("starting cleaner and watcher..")

        time.sleep(60)
        threading.Thread(target = self.scitWatcher, args = (), name = "thread-scit-watcher").start()
        print "started scitWatcher.."
        self.__scit_logger.info("scitWatcher started..")

        self.rotateCleaner()

    #start rotate and clean task
    def rotateCleaner(self):
        #cycle to find a dirty or timeout one
        print "started cleaner.."
        self.__scit_logger.info("scit-dns cleaner started..")

        while True:
            print "waiting error or timeout vm.."
            time.sleep(10)

            vm_name = checkVm()
            if vm_name:
                print "start rotate-clean vm " + vm_name
                self.__scit_logger.info("rotate-clean vm " + vm_name)
                self.rotateCleanTask(vm_name)


    #scit-dns system watcher
    def scitWatcher(self): 
        #check vm and find timeout-vm or dirty vm
        #write changes into the db,and that's all
        time.sleep(360)

        print "started watcher.."
        self.__scit_logger.info("scit-dns watcher started..")

        while True:
            print "finding the dirty server.."

            for ip in self.FLOAT_IPS:
                q_vmname = getVmByIP(ip)
                #check the overtime to work server
                if q_vmname and q_vmname in watchTimeout(self.SCIT_D):
                    print "found a overtime work server " + q_vmname + "."
                    self.__scit_logger.error("server " + q_vmname + " timeout to work.")
                    updateVmStatus(q_vmname, "TIMEOUT")
                
                #if q_vmname and not testVmDNS(ip):
                #    print "found a failed-dns server " + q_vmname + "."
                #    self.__scit_logger.error("server " + q_vmname + " failed to resolv domain.")
                #    updateVmStatus(q_vmname, "ERROR")


    def rotateCleanTask(self, vm_name):
        #min clean-rotate task
        #confirm a clean one
        clean_server = findReadyVm()
        retry = self.SCIT_R

        while not clean_server:
            #no clean server wait
            if retry <= 0:
                print "retry timeout.."
                self.__scit_logger.error("retry timeout..")
                sys.exit(2)

            print "waiting clean server."
            self.__scit_logger.warn("waiting clean server.")
            time.sleep(5)
            
            clean_server = findReadyVm()
            retry = retry - 1

        #floatip free and assign to clean one
        fip = vm_free_set(self.__scit_logger, vm_name)
        if not fip:
            print "error when try free floatip.."
            self.__scit_logger("stopped with free floatip.")
            sys.exit(1)

        #make a clean vm online
        vm_extra_set(self.__scit_logger, clean_server, fip)

        #test the online one
        #write into db
        #make the old dirty one at cleaning state
        updateVmStatus(vm_name, "CLEANING")

        #try delete the dirty one and create same one
        delete_nova_vm(self.__scit_logger, vm_name, fip)
        #re-create it
        if not create_nova_vm(self.__scit_logger, vm_name, self.INIT_SCRIPT):
            print "creat nova vm timeout.."
            self.__scit_logger.error("nova vm " + vm_name + " re-create timeout..")
            sys.exit(2)
 

#scit-dns system ctrler
def main():
    sc = ScitCtrler()
    sc.initScitCtrler()


#start program
if __name__ == "__main__":
    sys.exit(main())

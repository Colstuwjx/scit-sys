#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
from creds import get_nova_obj
from scit_config import *
from scit_db import *


#get authed nova obj
nova = get_nova_obj()


def create_nova_vm(logger, server_name, usr_dst):
    conf = getScitConfig()
    retry = int(conf["scit"]["scit_clean_retry"])

    #check status and write into db
    ret = create_vm_min(logger, server_name, usr_dst)
    if not ret:
        while True:
            if retry <= 0:
                print "create vm " + server_name + " timeout"
                if logger:
                    logger.error("create vm " + server_name + " timeout.")

                return False
            else:
                delete_nova_vm(logger, server_name, None)
                time.sleep(10)
                
                retry = retry - 1
                ret = create_vm_min(logger, server_name, usr_dst)
                if ret:
                    break

    #write into db
    addVm(ret["vm_name"], ret["vm_fixip"], "READY")
    return True


#minimal create vm
def create_vm_min(logger, server_name, usr_dst):
    ret = {}
    ret["vm_name"] = server_name

    try:
        f = open(usr_dst)
        user_data = f.read()
        f.close()
    except:
        if logger:
            logger.error("create vm failed, is there a init script?")
        return False

    #read the conf
    conf = getScitConfig()
    img = conf["instance"]["instance_img"]
    flvr = conf["instance"]["instance_flvr"]
    key_pair = conf["instance"]["instance_keypair"]
    network_id = conf["network"]["network_ext_netid"]

    #query whether the name is already exists.
    #try create
    if not nova.keypairs.findall(name=key_pair):
        with open(os.path.expanduser('/root/.ssh/id_rsa.pub')) as fpubkey:
            nova.keypairs.create(name=key_pair, public_key=fpubkey.read())

    ta = time.time()
    try:
        image = nova.images.find(name=img)
        flavor = nova.flavors.find(name=flvr)
        network = nova.networks.find(id=network_id)

        instance = nova.servers.create(name=server_name, image=image, flavor=flavor, userdata=user_data, network=network, key_name=key_pair)
    except:
        if logger:
            logger.error("failed create nova vm, exception throw out.")
        print "expceton found when try creating nova vm."
        return False

    status = instance.status
    while status == 'BUILD':
        time.sleep(5)
        print "waiting vm active.."
        # Retrieve the instance again so the status field updates
        instance = nova.servers.get(instance.id)
        status = instance.status

    tb = time.time()
    t = int(tb-ta + (tb-ta - int(tb-ta))/1.0)

    print "Total: " + str(t) + " s."
    if logger:
        logger.info("create vm " + server_name + ", Total " + str(t) + " s.")

    #not active or network is not ok
    if status != 'ACTIVE':
        return False

    instance = nova.servers.get(instance.id)
    network_flag = False
    if instance.networks:
        for item in instance.networks:
            if instance.networks[item]:
                ret["vm_fixip"] = instance.networks[item][0]
                network_flag = True

    if not network_flag:
        print "vm network init failed."
        if logger:
            logger.error("vm: " + server_name + " network init failed.")
        return False

    print "successful create vm: " + server_name
    if logger:
        logger.info("vm: " + server_name + " created.")

    return ret


#bind floatip to vm
#check whether a clean server is ok to online
def vm_extra_set(logger, server_name, floatip):
    try:
        instance = nova.servers.find(name = server_name)
    except:
        print "vm " + server_name + "not found."
        if logger:
            logger.error("vm " + server_name + "not found.")
        return False

    if instance.status == "ACTIVE":
        floating_ip = nova.floating_ips.find(ip=floatip)
        instance.add_floating_ip(floating_ip)

        #check whether server is ok

        #write into db
        updateFloatip(server_name, floatip)

        return True
    else:
        return False


def vm_free_set(logger, server_name):
    instance = None

    try:
        instance = nova.servers.find(name = server_name)
    except:
        print "vm " + server_name + "not found."
        if logger:
            logger.error("vm " + server_name + "not found?!")
        return False

    floatip = ""
    for item in instance.networks:
        if len(instance.networks[item]) == 2:
            floatip = instance.networks[item][1]
        else:
            return False

    #free the floatip
    instance.remove_floating_ip(floatip)
    return floatip


#delete the vm
def delete_nova_vm(logger, server_name, float_ip):
    #clean the env
    #remove the knownlist info
    if not server_name:
        print "vm name illegal."
        if logger:
            logger.warn("vm name illegal, delete task stopped.")

    print "deleting vm " + server_name
    if logger:
        logger.info("try deleting vm " + server_name)

    if float_ip:
        os.popen("sed -i '/^.*" + float_ip + ".*/d' /root/.ssh/known_hosts")
        #os.popen("sed -i '/^.*" + float_ip + ".*/d' /etc/ansible/hosts")

    try:
        instance = nova.servers.find(name=server_name)
    except:
        print "vm: " + server_name + " not found."
        if logger:
            logger.warn("vm " + server_name + " not found.")

        return True

    instance.delete()

    #clear the db
    #runSQL("delete from scit_vm where vm_name = " + server_name + ";")
    delVm(server_name)

    #confirm that is delete ok
    conf = getScitConfig()
    retry = int(conf["scit"]["scit_clean_retry"])

    while True:
        if retry <= 0:
            print "delete task timeout."
            if logger:
                logger.error("delete vm: " + server_name + " task timeout.")
            return False

        try:
            instance = nova.servers.find(name=server_name)
            retry = retry - 1
        except:
            break


#clear the vm
def clear_nova_vm(logger):
    #clear the all nova vm
    instances = nova.servers.list()
    retry = 0
    if instances:
        for server in instances:
            print "deleting the vm: " + server.name
            if logger:
                logger.info("deleting the vm: " + server.name)
            server.delete()
    else:
        return True

    #wait the clear ok
    while True:
        if retry > 10:
            #retry 10 times
            print "clear vm failed, timeout.."
            if logger:
                logger.error("clear vm retry timeout.")
            return False

        instances = nova.servers.list()
        if instances:
            retry = retry + 1
            time.sleep(10)
        else:
            print "all vm cleared.."
            logger.info("cleared the vms..")
            return True 


#main func
def main():
    create_nova_vm(None, server_name="test2", img="CentOS 6.5 x86_64", flvr="m1.small", usr_dst="/root/openstack/pys/scit-sys/scripts/init.sh", key_pair="dns_test", network_id="0e13d973-f3a7-4e65-aba0-7d0f392ce13b")
    #delete_nova_vm(None, server_name="test2", float_ip="192.168.1.122")

    return 0


#code entry
if __name__ == '__main__':
    #main()
    vm_extra_set(None, "SCIT_VM00", "192.168.1.122")
    #clear_nova_vm(None)

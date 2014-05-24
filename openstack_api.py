#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
from creds import get_nova_obj


#get authed nova obj
nova = get_nova_obj()


#def test_ping_vm(server_name):


def create_nova_vm(logger, server_name, img, flvr, usr_dst, key_pair, network_id):
    #query whether the name is already exists.
    #try create
    if not nova.keypairs.findall(name=key_pair):
        with open(os.path.expanduser('/root/.ssh/id_rsa.pub')) as fpubkey:
            nova.keypairs.create(name=key_pair, public_key=fpubkey.read())

    try:
        f = open(usr_dst)
        user_data = f.read()
        f.close()
    except:
        if logger:
            logger.error("create vm failed, is there a init script?")
        return None

    image = nova.images.find(name=img)
    flavor = nova.flavors.find(name=flvr)
    network = nova.networks.find(id=network_id)
    instance = nova.servers.create(name=server_name, image=image, flavor=flavor, userdata=user_data, network=network, key_name=key_pair)

    status = instance.status
    while status == 'BUILD':
        time.sleep(5)
        # Retrieve the instance again so the status field updates
        instance = nova.servers.get(instance.id)
        status = instance.status
    print "status: %s" % status


#bind floatip to vm
def bind_fip_vm(logger, server_name, floatip):
    instance = nova.servers.find(name = server_name)
    if instance.status == "ACTIVE":
        floating_ip = nova.floating_ips.find(ip=floatip)
        instance.add_floating_ip(floating_ip)

        return True
    else:
        return False


#delete the vm
def delete_nova_vm(logger, server_name, float_ip):
    #clean the env
    #remove the knownlist info
    start_time = time.time()

    os.popen("sed -i '/^.*" + float_ip + ".*/d' /root/.ssh/known_hosts")
    instance = nova.servers.find(name=server_name)
    instance.delete()

    stop_time = time.time()
    
    #confirm that is delete ok


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
            time.sleep(5)
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
    main()
    #bind_fip_vm(None, "test2", "192.168.1.122")
    #clear_nova_vm(None)

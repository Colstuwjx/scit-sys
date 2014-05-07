#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
from creds import get_nova_obj


nova = get_nova_obj()


def create_nova_vm(server_name, img, flvr, user_data, key_pair, network_id, float_ip):
    #query whether the name is already exists.
    #try create
    if not nova.keypairs.findall(name=key_pair):
        with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
            nova.keypairs.create(name=key_pair, public_key=fpubkey.read())

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

    #add a float ip
    if instance.status == "ACTIVE":
        floating_ip = nova.floating_ips.find(ip=float_ip)
        instance.add_floating_ip(floating_ip)


#float ip ctrller
def assign_float_ip(server_name, float_ip):
    #check whether the ip exists in DB
    instance = nova.servers.find(name=server_name)
    instance.add_floating_ip(floating_ip)


#main func
def main():
    create_nova_vm(server_name="test2", img="CentOS 6.5 x86_64", flvr="m1.small", user_data=None, key_pair="dns_test", network_id="0e13d973-f3a7-4e65-aba0-7d0f392ce13b", float_ip="192.168.1.121")
    return 0


#code entry
if __name__ == '__main__':
    main()

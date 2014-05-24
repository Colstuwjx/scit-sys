from creds import get_neutron_obj
from scit_config import getScitConfig


neutron = get_neutron_obj()


#complete the scit-dns floatip initial
def initScitNetwork(logger, vm_num):
    nets = neutron.list_floatingips()
    scit_nets = []

    for item in nets["floatingips"]:
        if not item["fixed_ip_address"]:
            if len(scit_nets) < vm_num:
                scit_nets.append(item["floating_ip_address"])
            else:
                return scit_nets

    if type(vm_num) != type(1):
        if logger:
            logger.error("scit_network failed with wrong vm_num args")
        print "failed, wrong args..."

    for i in xrange(vm_num - len(scit_nets)):
        ret = createScitFloatip()
        if not ret:
            if logger:
                logger.error("scit_network failed to create floatip")
            print "failed to create floatip"

            return None 
        else:
            scit_nets.append(ret["floating_ip_address"])

    scit_nets.sort()
    return scit_nets


#use api to create a new floatingip
def createScitFloatip():
    conf = getScitConfig()
    ext_net = conf["network"]["network_ext_netid"]
    param = {'floatingip': {'floating_network_id': ext_net}}

    try:
        result = neutron.create_floatingip(param)
        return result["floatingip"]
    except:
        return None

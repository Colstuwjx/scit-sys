scit-sys
========

SCIT-DNS system, Enable a secure and easy-ctrl DNS cluster.

========

##How it Work?
Use Openstack and Saltstack made a SCIT-DNS System.  
It will rotate the vms, and make the dns-cluster at  
a clean state.
  
##Techs:  
> Openstack (H) API and Horizon;  
> Saltstack 0.17.5;  
> Python 2.6.6(actually don't care);  
> SCIT rotate;  
> BIND and dns settings;  

##Ansible Usage:
> Use ansible all -m raw -a 'w' to call raw cmd module run shell;
> Use original target run: ansible '192.168.1.122' -m raw -a 'w';

##MysqlDB Table
To be continue

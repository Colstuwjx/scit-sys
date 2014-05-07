#!/bin/bash -
#nova vm init
HOST_IP=192.168.1.101
VM_NAME="test2"

#dns init
cat > /etc/resolv.conf << EOF
nameserver 8.8.8.8
nameserver 4.4.4.4
EOF

#rpm curl download
curl -C -s -o /tmp/wget.rpm http://${HOST_IP}/rpms/wget-1.12-1.11.el6_5.x86_64.rpm
curl -C -s -o /tmp/epel.rpm http://${HOST_IP}/rpms/epel-release-6-8.noarch.rpm

#install them
yum localinstall -y /tmp/wget.rpm
yum localinstall -y /tmp/epel.rpm

#iptables settings
cat > /etc/sysconfig/iptables << EOF
# Firewall configuration written by system-config-firewall
# Manual customization of this file is not recommended.
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
-A INPUT -p icmp -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 22 -j ACCEPT
-A INPUT -m tcp -p tcp --dport 4505 -j ACCEPT
-A INPUT -m tcp -p tcp --dport 4506 -j ACCEPT
-A INPUT -j REJECT --reject-with icmp-host-prohibited
-A FORWARD -j REJECT --reject-with icmp-host-prohibited
COMMIT
EOF

service iptables reload
service sshd restart

#install salt
wget -O /var/cache/yum/x86_64/6/base/packages/m2crypto-0.20.2-9.el6.x86_64.rpm  http://192.168.1.101/rpms/m2crypto-0.20.2-9.el6.x86_64.rpm

wget -O /var/cache/yum/x86_64/6/base/packages/python-babel-0.9.4-5.1.el6.noarch.rpm  http://192.168.1.101/rpms/python-babel-0.9.4-5.1.el6.noarch.rpm

wget -O /var/cache/yum/x86_64/6/base/packages/python-crypto-2.0.1-22.el6.x86_64.rpm  http://192.168.1.101/rpms/python-babel-0.9.4-5.1.el6.noarch.rpm

wget -O /var/cache/yum/x86_64/6/base/packages/python-jinja2-2.2.1-1.el6.x86_64.rpm  http://192.168.1.101/rpms/python-jinja2-2.2.1-1.el6.x86_64.rpm

wget -O /tmp/salt-0.17.5-1.el6.noarch.rpm  http://192.168.1.101/rpms/salt-0.17.5-1.el6.noarch.rpm

wget -O /tmp/salt-minion-0.17.5-1.el6.noarch.rpm  http://192.168.1.101/rpms/salt-minion-0.17.5-1.el6.noarch.rpm

wget -O /var/cache/yum/x86_64/6/epel/packages/openpgm-5.1.118-3.el6.x86_64.rpm  http://192.168.1.101/rpms/openpgm-5.1.118-3.el6.x86_64.rpm

wget -O /var/cache/yum/x86_64/6/epel/packages/python-msgpack-0.1.13-3.el6.x86_64.rpm  http://192.168.1.101/rpms/python-msgpack-0.1.13-3.el6.x86_64.rpm

wget -O /var/cache/yum/x86_64/6/epel/packages/python-zmq-2.2.0.1-1.el6.x86_64.rpm  http://192.168.1.101/rpms/python-zmq-2.2.0.1-1.el6.x86_64.rpm

wget -O /var/cache/yum/x86_64/6/epel/packages/sshpass-1.05-1.el6.x86_64.rpm  http://192.168.1.101/rpms/sshpass-1.05-1.el6.x86_64.rpm

wget -O /var/cache/yum/x86_64/6/epel/packages/zeromq3-3.2.4-1.el6.x86_64.rpm  http://192.168.1.101/rpms/zeromq3-3.2.4-1.el6.x86_64.rpm

wget -O /var/cache/yum/x86_64/6/updates/packages/yum-utils-1.1.30-17.el6_5.noarch.rpm  http://192.168.1.101/rpms/yum-utils-1.1.30-17.el6_5.noarch.rpm

yum -y install salt-minion
yum -y remove salt
yum localinstall -y /tmp/salt-0.17.5-1.el6.noarch.rpm /tmp/salt-minion-0.17.5-1.el6.noarch.rpm 

wget -O /etc/salt/minion http://192.168.1.101/confs/minion 
echo ${VM_NAME}"" > /etc/salt/minion_id

service salt-minion restart

#!/bin/bash -
#nova vm init
HOST_IP=192.168.1.101
VM_NAME="test1"

#dns init
cat > /etc/resolv.conf << EOF
nameserver 8.8.8.8
nameserver 4.4.4.4
EOF

\cp -f /root/.ssh/authorized_keys /root/.ssh/authorized_keys.bak
\cp -f /home/cloud-user/.ssh/authorized_keys /root/.ssh/authorized_keys 

#rpm curl download
curl -C -s -o /tmp/wget.rpm http://${HOST_IP}/rpms/wget-1.12-1.11.el6_5.x86_64.rpm
curl -C -s -o /tmp/epel.rpm http://${HOST_IP}/rpms/epel-release-6-8.noarch.rpm

#install them
rpm -ih /tmp/wget.rpm
rpm -ih /tmp/epel.rpm

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
-A INPUT -m tcp -p tcp --dport 53 -j ACCEPT
-A INPUT -m tcp -p tcp --dport 953 -j ACCEPT
-A INPUT -p udp --dport 53 -j ACCEPT
-A INPUT -j REJECT --reject-with icmp-host-prohibited
-A FORWARD -j REJECT --reject-with icmp-host-prohibited
COMMIT
EOF

service iptables restart
service sshd restart

#rpm installation
mkdir -p /tmp/rpms/

#install bind
wget -c -O /tmp/rpms/bind-9.8.2-0.23.rc1.el6_5.1.x86_64.rpm http://192.168.1.101/rpms/bind-9.8.2-0.23.rc1.el6_5.1.x86_64.rpm

wget -c -O /tmp/rpms/bind-libs-9.8.2-0.23.rc1.el6_5.1.x86_64.rpm http://192.168.1.101/rpms/bind-libs-9.8.2-0.23.rc1.el6_5.1.x86_64.rpm

wget -c -O /tmp/rpms/portreserve-0.0.4-9.el6.x86_64.rpm http://192.168.1.101/rpms/portreserve-0.0.4-9.el6.x86_64.rpm

#set up the dns server
cd /tmp/rpms/

rpm -ih portreserve-0.0.4-9.el6.x86_64.rpm
rpm -ih bind-libs-9.8.2-0.23.rc1.el6_5.1.x86_64.rpm
rpm -ih bind-9.8.2-0.23.rc1.el6_5.1.x86_64.rpm

#set the named confs
cat > /etc/named.conf << EOF
options {
        listen-on port 53 { any; };
        //listen-on-v6 port 53 { ::1; };
        directory       "/var/named";
        dump-file       "/var/named/data/cache_dump.db";
        statistics-file "/var/named/data/named_stats.txt";
        memstatistics-file "/var/named/data/named_mem_stats.txt";
        allow-query     { any; };
        recursion yes;

        dnssec-enable yes;
        dnssec-validation yes;
        dnssec-lookaside auto;

        /* Path to ISC DLV key */
        bindkeys-file "/etc/named.iscdlv.key";

        managed-keys-directory "/var/named/dynamic";
};

logging {
        channel default_debug {
                file "data/named.run";
                severity dynamic;
        };
};

zone "." IN {
        type hint;
        file "named.ca";
};

zone "scit.com" IN {
        type master;
        file "scit.com.zone";
        allow-update { none; };
};

include "/etc/named.rfc1912.zones";
include "/etc/named.root.key";
EOF

#echo zone info to file
cat > /var/named/scit.com.zone << EOF
\$TTL 1D
@       IN SOA  @ rname.invalid. (
                                        1       ; serial
                                        1D      ; refresh
                                        1H      ; retry
                                        1W      ; expire
                                        3H )    ; minimum
        NS      @
        A       127.0.0.1
        AAAA    ::1

        IN      MX      10      mail.scit.com.
www     IN      A       192.168.1.121
mail    IN      A       192.168.1.121
EOF

service named restart
chkconfig named on

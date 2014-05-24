#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import keystoneclient.v2_0.client as ksclient
import novaclient.v1_1.client as nvclient
from neutronclient.v2_0 import client as neutron_client


def get_keystone_creds():
    #get the keystone auth
    d = {}
    d['username'] = os.environ['OS_USERNAME']
    d['password'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['tenant_name'] = os.environ['OS_TENANT_NAME']

    return d


def get_nova_creds():
    d = {}
    d['username'] = os.environ['OS_USERNAME']
    d['api_key'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['project_id'] = os.environ['OS_TENANT_NAME']

    return d


def get_neutron_obj():
    creds = get_keystone_creds()
    neutron = neutron_client.Client(**creds)

    #433 line
    #print neutron.list_floatingips()
    

    #param = {'floatingip': {'floating_network_id': "0e13d973-f3a7-4e65-aba0-7d0f392ce13b"}}
    #neutron.create_floatingip(param)
    return neutron


def get_keystone_token():
    creds = get_keystone_creds()
    keystone = ksclient.Client(**creds)

    return keystone.auth_token


def get_nova_obj():
    creds = get_nova_creds()
    nova = nvclient.Client(**creds)

    #get the nova client obj
    return nova

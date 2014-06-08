#!/usr/bin/python
# -*- coding: utf-8 -*-
from scit_config import *
import MySQLdb

def getDbConn():
    conf = getScitConfig()
    dbhost = conf["db"]["db_host"]
    dbuser = conf["db"]["db_user"]
    dbpasswd = conf["db"]["db_pass"]
    dbname = conf["db"]["db_name"]

    #setup db connection
    conn = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db=dbname)
    return conn


def runSQL(sqltext):
    conn = getDbConn()
    cursor = conn.cursor()

    cursor.execute(sqltext)
    cursor.close()
    conn.close()


def addVm(vm_name, vm_fixip, vm_status):
    conn = getDbConn()
    cursor = conn.cursor()
    
    sql = "INSERT INTO scit_vm(vm_name, vm_fixip, vm_status) values(%s, %s, %s); commit;"
    param = (vm_name, vm_fixip, vm_status)
    n = cursor.execute(sql, param)

    cursor.close()
    conn.close()


def delVm(vm_name):
    conn = getDbConn()
    cursor = conn.cursor()

    if not vm_name:
        print "vm " + vm_name + " illegal!"
        return False

    sql = "DELETE FROM scit_vm WHERE vm_name = %s; commit;"
    param = (vm_name)
    n = cursor.execute(sql, param)

    cursor.close()
    conn.close()
    return True


def updateFloatip(vm_name, vm_floatip):
    conn = getDbConn()
    cursor = conn.cursor()
    
    vm_status = "RUN"
    sql = "UPDATE scit_vm SET vm_floatip = %s WHERE vm_name = %s; UPDATE scit_vm SET vm_status = %s WHERE vm_name = %s; commit;"
    param = (vm_floatip, vm_name, vm_status, vm_name)
    n = cursor.execute(sql, param)

    cursor.close()
    conn.close()


def updateVmStatus(vm_name, vm_status):
    conn = getDbConn()
    cursor = conn.cursor()

    sql = "UPDATE scit_vm SET vm_status = %s WHERE vm_name = %s; commit;"
    param = (vm_name, vm_status)
    n = cursor.execute(sql, param)

    cursor.close()
    conn.close()


def getVmByIP(float_ip):
    conn = getDbConn()
    cursor = conn.cursor()

    if not float_ip:
        print "illegal floatip arg."
        return ""

    vm_status = "RUN"
    sql = "SELECT vm_name FROM scit_vm WHERE vm_floatip = %s and vm_status = %s;"
    param = (float_ip, vm_status)
    n = cursor.execute(sql, param)

    server = []
    for row in cursor.fetchall():
        if len(server) < 1:
            server.append(row[0])
        else:
            break

    if server:
        return server[0]
    else:
        print "no matched floatip vm found.."
        return ""


def findReadyVm():
    conn = getDbConn()
    cursor = conn.cursor()

    sql = "SELECT vm_name FROM scit_vm WHERE vm_status = %s;"
    param = ("READY")
    n = cursor.execute(sql, param)

    server = []
    for row in cursor.fetchall():
        if len(server) < 1:
            server.append(row[0])
        else:
            break

    if server:
        return server[0]
    else:
        print "no error/timeout vm found.."
        return ""

def checkVm():
    conn = getDbConn()
    cursor = conn.cursor()

    sql = "SELECT vm_name FROM scit_vm WHERE vm_status IN (%s,%s);"
    param = ("ERROR", "TIMEOUT")
    n = cursor.execute(sql, param)

    #throw out one vm
    server = []
    for row in cursor.fetchall():
        if len(server) < 1:
            server.append(row[0])
        else:
            break

    if server:
        return server[0]
    else:
        print "no error/timeout vm found.."
        return ""


def watchTimeout(timeout):
    conn = getDbConn()
    cursor = conn.cursor()

    vm_status = "RUN"
    sql = "select vm_name from scit_vm where vm_status = %s and (CURRENT_TIMESTAMP() - vm_create_time) > %d;"
    param = (vm_status, int(timeout))
    n = cursor.execute(sql, param)

    server = []
    for row in cursor.fetchall():
        server.append(row[0])

    return server

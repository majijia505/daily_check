#!/bin/env python
#!econding=utf-8
import paramiko
sshclient = paramiko.SSHClient()
sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
sshclient.connect('192.168.137.128',\
            22,\
            'python',\
            '1234')
           
stdin, stdout, stderr = sshclient.exec_command("""find . -name "*gz" """)
message = ''.join(stdout.readlines())
sshclient.close()
print message
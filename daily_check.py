#!/data1/portal/python2.7/bin/python
# -*- coding: utf-8 -*-

import paramiko
import sys
from functools import partial
import time
import threading
import datetime
#定义相关指标使用的命令
#内存占用率
#linux版本
mem_usage_linux="""free -m | sed -n '3p' | awk '{printf "%.1f",($NF/($(NF-1)+$NF))*100}' """
#solaris版本，由于soalris无法直接获取内存利用率需进行计算，因此先获取使用量，在除以总量
mem_usage_solaris="""vmstat | sed -n '3p'  | awk '{printf "%.f",$5/1024}'"""
mem_sum={}
mem_sum['10.142.35.10']=16256
mem_sum['10.142.35.11']=16256
mem_sum['10.142.35.24']=65024
mem_sum['10.142.35.25']=65024
mem_sum['10.142.35.31']=32640
mem_sum['10.142.35.42']=31668
#CPU使用率
#linux版本
cpu_usage_linux="""vmstat | sed -n '3p' | awk '{printf "%d",(100-$(NF-2))}'"""
#solaris版本
cpu_usage_solaris="""vmstat | sed -n '3p'  | awk '{printf "%s",(100-$NF)}'"""
#磁盘空间占用率
disk_used="""df -h | sed -e '1d' -e '/cdrom/d' | sort -k5 | tail -1 | awk '{print $(NF-1)}'"""


#获取各结果使用的函数
def ssh_command(host_name,username,userpassword,*command):
    port=22
    #判断增加command为列表或者元组的支持，如果为列表或者元组则返回一个结果组成的列表
    sshclient = paramiko.SSHClient()
    sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshclient.connect(host_name,port,username,userpassword)
    back_message = []
    for comm in command:
        stdin, stdout, stderr = sshclient.exec_command(comm)
        message = ''.join(stdout.readlines())
        back_message.append(message)
    sshclient.close()
    return back_message
        
        

    
#定义加载配置文件参数
#配置文件为如下格式：hostanme|username|password|os_type，返回包含所有配置项的列表
def loadconfig():
    f=open('auto_check.cfg','r')
    config=[]
    for config_str in f:
        config_list = config_str.strip().split("|")
        if len(config_list) != 5:
            print "config file is error ,should be 'machine_name|hostanme|username|password|os_type' "
            f.close()
            return -1
        else:
            config_dict={}
            config_dict['machine_name'] = config_list[0]
            config_dict['hostname'] = config_list[1]
            config_dict['username'] = config_list[2]
            config_dict['userpass'] = config_list[3]
            config_dict['ostype']   = config_list[4]
            config.append(config_dict)
    f.close()
    return config
    
def get_data(config_dict):
    machine_name = config_dict['machine_name']
    remote_host = config_dict['hostname']
    user_name   = config_dict['username']
    user_password = config_dict['userpass']
    os_type = config_dict['ostype']
    #开始获取指标，获取linux指标项
    if os_type == 'linux':
        #ssh_command(host_name,username,userpassword,command,port=22)
        #ssh=partial(ssh_command,host_name = remote_host,username = user_name,userpassword = user_password)
        #print ssh
        #cpu_usage = ssh(command=cpu_usage_linux)
        #mem_usage = ssh(command=cpu_usage_linux)
        #disk_usage= ssh(command=disk_used)
        #使用新版程序，直接返回3个命令结果
        commands=[cpu_usage_linux,mem_usage_linux,disk_used]
        back_message=ssh_command(remote_host,user_name,user_password,*commands)
        #back_message=ssh(*commands)
        
        check_data={}
        check_data['machine_name'] = machine_name
        check_data['hostname'] = remote_host
        #check_data['cpu_usage'] = cpu_usage
        #check_data['mem_usage'] = mem_usage
        #check_data['disk_usage'] = disk_usage
        check_data['cpu_usage'] = back_message[0]
        check_data['mem_usage'] = back_message[1]
        check_data['disk_usage'] = back_message[2]
        print "%s|%s|%s|%s" %(check_data['machine_name'],check_data['mem_usage'],check_data['cpu_usage'],check_data['disk_usage']),
        
    elif os_type == 'solaris':
        #ssh_command(host_name,username,userpassword,command,port=22)
        #ssh=partial(ssh_command,remote_host,user_name,user_password)
        commands=[cpu_usage_solaris,mem_usage_solaris,disk_used]
        back_message=ssh_command(remote_host,user_name,user_password,*commands)
        cpu_usage = back_message[0]
        mem_free = back_message[1]
        disk_usage= back_message[2]
        
        mem_free = float("%.4f" %(float(mem_free)/float(mem_sum[remote_host])))
        mem_usage = "%.2f" %((1 - mem_free)*100)
        check_data={}
        check_data['machine_name'] = machine_name
        #check_data['hostname'] = remote_host
        check_data['cpu_usage'] = cpu_usage
        check_data['mem_usage'] = mem_usage
        check_data['disk_usage'] = disk_usage
        print "%s|%s|%s|%s" %(check_data['machine_name'],check_data['mem_usage'],check_data['cpu_usage'],check_data['disk_usage']),
    
if __name__ == '__main__':
    print "hostname|mem_usage|cpu_usage|disk_usage"
    start_time=time.clock()
    threads = []
    config_list=loadconfig()
    #print config_list
    for config_dict in config_list:
        #创建线程
        t=threading.Thread(target = get_data,args=(config_dict,))
        threads.append(t)
    thread_num = len(threads)
    #print thread_num
    
    thread_list=range(0,thread_num)
    
    for i in thread_list:
        threads[i].start()
        
    for i in thread_list:
        threads[i].join()
    end_time=time.clock()
    #print("The function run time is : %.03f seconds" %(end_time-start_time))

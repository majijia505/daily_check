# daily_check
巡检脚本，每次巡检将CPU、内存、磁盘的使用率以邮件的形式发送出去
脚本通过使用paramiko登录到各主机，取出各项参数，然后使用django的模板系统生成html
并使用smtplib发送出去

由于使用了django的模板系统和paramiko 因此需要paramiko库和django库

----20150909 添加第一版，打印数据到标准输出的脚本，目前可以运行。
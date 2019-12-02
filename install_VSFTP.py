#!/bin/python
# -*- coding: utf-8 -*-
import os
#"""
#######---lei insall VSftpd and Vuser login   update 2019-4.10  V2 ------#######################
#  pyhton3.7-2.7 centos7.4(64X)   install vsftpd  and config vuser
#  对应配置文件都在/etc/vsftpd/...
#w+：先清空所有文件内容，然后写入，然后你才可以读取你写入的内容
#r+：不清空内容，可以同时读和写入内容。 写入文件的最开始
#a+：追加写，所有写入的内容都在文件的最后
#测试成功
#运行之后  1.修改配置文件anonymous_enable=YES  YES改为NO
#          2.FTP目录可以后创建： 给目录文件-->实体用户赋权 即“testftp”   chown testftp:ftp -R  xxx 
#          3.启动
#"""

vuser_name_passws=[
    ['lili','abc123477','/home/www/html'],
    ['lucy','abc213277','/home/www/html'],
    ['lilei','abc213277','/home/www/html'],
    ['lihua','abc543277','/home/www/html']
                  ]
vuser_list='vuser_list'   #虚拟用户表
vuser_list_db='vuser_list_db'  #虚拟用户表  生成的 虚拟用户表数据文件
vuser_conf='vuser_conf'        #虚拟用户文件夹
testftp='testftp'     #虚拟用户绑定的实体用户名
listenport='21'

def install_sofat():
    os.system('yum -y update')
    os.system('yum install -y psmisc net-tools db4 systemd-devel libdb-devel perl-DBI vsftpd')

def vsuer_vsuserdb(vuser_name_passws,vuser_list,vuser_list_db):
    with open('/etc/vsftpd/'+vuser_list,'w+') as sconf:  # 打开一个文件用于读写。如果该文件已存在则打开文件，并从开头开始编辑，即原有内容会被删除。如果该文件不存在，创建新文件。
        for se in  vuser_name_passws:
            if se==vuser_name_passws[-1]:
                sconf.write(se[0] + '\n' + se[1])
            else:
               sconf.write(se[0] + '\n' + se[1] + '\n')
            #用户名和用户密码前后一定不要留空格 and if的作用： 最后一个密码后面不加\n
    os.system('db_load -T -t hash -f /etc/vsftpd/'+vuser_list+' /etc/vsftpd/'+vuser_list_db+'.db')
    os.system('chmod 600 /etc/vsftpd/'+vuser_list_db+'.db')

def pam_vsftpd(vuser_list_db):

    with open('/etc/pam.d/vsftpd', 'w+') as sconf:
        sconf.write('auth required /lib64/security/pam_userdb.so db=/etc/vsftpd/'+vuser_list_db+'\n')
        sconf.write('account required /lib64/security/pam_userdb.so db=/etc/vsftpd/'+vuser_list_db+ '\n')

def vuser_config(vuser_name_passws,vuser_conf):
    os.system('mkdir  /etc/vsftpd/'+'vuser_conf')
    #print('创建文件步骤：','/etc/vsftpd/'+'vuser_conf')
    for se in vuser_name_passws:
        with open('/etc/vsftpd/' + vuser_conf +'/'+ se[0], 'w+') as sconf:
            sconf.write('local_root=' +se[2]+ '\n')
            sconf.write('dirlist_enable=YES' + '\n')
            sconf.write('download_enable=YES' + '\n')
            #这个配置文件每一行结尾不能用空格
def create_user(testftp):
    os.system('useradd '+testftp+' -g ftp  -s /bin/false  ')


def Addvsftpdconfig(testftp,vuser_conf,listenport):
    with open('/etc/vsftpd/vsftpd.conf', 'a+') as sconf:
        sconf.write('listen_port='+listenport+ '\n')
        sconf.write('chroot_local_user=YES' + '\n')
        sconf.write('########### this is vuser conf ####################' + '\n')
        sconf.write('guest_enable=YES' + '\n')
        sconf.write('#启用虚拟用户功能' + '\n')
        sconf.write('guest_username='+testftp + '\n')
        sconf.write('#指定虚拟用户的宿主用户' + '\n')
        sconf.write('user_config_dir=/etc/vsftpd/'+vuser_conf + '\n')
        sconf.write('#设定虚拟用户个人配置文件目录' + '\n')
        sconf.write('allow_writeable_chroot=YES' + '\n')
        sconf.write('virtual_use_local_privs=YES' + '\n')
        sconf.write('#虚拟用户和本地用户有相同的权限' + '\n')
        sconf.write('pasv_enable=YES' + '\n')
        sconf.write('pasv_min_port=6666' + '\n')
        sconf.write('pasv_max_port=7000' + '\n')
        sconf.write('pasv_promiscuous=YES' + '\n')



if __name__ == "__main__":
    #1.安装基本软件
    install_sofat()
    #2.创建虚拟用户 以及生成DB文件
    vsuer_vsuserdb(vuser_name_passws,vuser_list,vuser_list_db)
    #3.更改pam 文件，
    pam_vsftpd(vuser_list_db)
    #4.创建虚拟用户配置文件
    vuser_config(vuser_name_passws,vuser_conf)
    #5.创建虚拟用户绑定的实体用户
    create_user(testftp)
    #6.vsftp基本配置后面添加虚拟用户配置
    Addvsftpdconfig(testftp, vuser_conf,listenport)
    #7,自己更改米名用户 和启动服务器。
    print('配置完成！,请检查iptables，用被动模式链接，放开6666-7000,已经测试ok！')
    print('修改配置文件anonymous_enable=YES  YES改为NO！ 给目录文件-->实体用户赋权 即“testftp”   chown testftp:ftp -R  xxx ')
    print('如果是云主机，需要添加设置：”pasv_addr_resolve=YES ，pasv_address=公网IP“ ！')

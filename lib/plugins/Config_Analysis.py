# coding:utf-8
from __future__ import print_function
import os, re
from lib.core.common import *
from lib.core.ip.ip import *
from subprocess import Popen, PIPE


# 作者：咚咚呛
# 配置安全类检测
# 1、dns配置检测
# 2、防火墙配置检测
# 3、hosts配置检测

class Config_Analysis:
    def __init__(self):
        self.config_suspicious = []
        self.ip_re = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

    # 检测dns设置
    def check_dns(self):
        suspicious, malice = False, False
        try:
            if os.path.exists('/etc/resolv.conf'):
                shell_process = os.popen(
                    'cat /etc/resolv.conf 2>/dev/null| grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}"').read().splitlines()
                for ip in shell_process:
                    if check_ip(ip):
                        self.config_suspicious.append(
                            {u'配置信息': u'DNS servername: %s' % ip, u'异常类型': u'境外dns', u'文件': u'/etc/resolv.conf'})
                        suspicious = True
            return suspicious, malice
        except:
            return suspicious, malice

    # 检测防火墙设置
    def check_iptables(self):
        suspicious, malice = False, False
        try:
            shell_process = os.popen("iptables -L -n 2>/dev/null| grep -v 'Chain'|grep 'ACCEPT'").read().splitlines()
            for iptables in shell_process:
                self.config_suspicious.append(
                    {u'配置信息': iptables, u'异常类型': u'存在iptables ACCEPT策略', u'手工确认': u'[1]iptables -L'})
                suspicious = True
            if os.path.exists('/etc/sysconfig/iptables'):
                with open('/etc/sysconfig/iptables') as f:
                    for line in f:
                        if len(line) > 5:
                            if (line[0] != '#') and ('ACCEPT' in line):
                                self.config_suspicious.append(
                                    {u'配置信息': line, u'异常类型': u'存在iptables ACCEPT策略', u'文件': u'/etc/sysconfig/iptables',
                                     u'手工确认': u'[1]cat /etc/sysconfig/iptables'})
                                suspicious = True
            return suspicious, malice
        except:
            return suspicious, malice

    # 检测hosts配置信息
    def check_hosts(self):
        suspicious, malice = False, False
        try:
            if not os.path.exists("/etc/hosts"): return suspicious, malice
            p1 = Popen("cat /etc/hosts 2>/dev/null", stdout=PIPE, shell=True)
            p2 = Popen("awk '{print $1}'", stdin=p1.stdout, stdout=PIPE, shell=True)
            shell_process = p2.stdout.read().splitlines()
            for ip_info in shell_process:
                if not re.search(self.ip_re, ip_info): continue
                ip = ip_info.strip().replace('\n', '')
                if check_ip(ip):
                    self.config_suspicious.append(
                        {u'配置信息': ip_info, u'异常类型': u'存在指定域名境外ip的配置信息', u'文件': u'/etc/hosts',
                         u'手工确认': u'[1]cat /etc/hosts'})
                    suspicious = True
            return suspicious, malice
        except:
            return suspicious, malice

    def run(self):
        print(u'\n开始配置类安全扫描')
        file_write(u'\n开始配置类安全扫描\n')

        string_output(u' [1]DNS设置扫描')
        suspicious, malice = self.check_dns()
        result_output_tag(suspicious, malice)

        string_output(u' [2]防火墙设置扫描')
        suspicious, malice = self.check_iptables()
        result_output_tag(suspicious, malice)

        string_output(u' [3]hosts设置扫描')
        suspicious, malice = self.check_hosts()
        result_output_tag(suspicious, malice)

        # 检测结果输出到文件
        result_output_file(u'可疑配置类如下：', self.config_suspicious)


if __name__ == '__main__':
    infos = Config_Analysis()
    infos.run()
    print(u"可疑配置类如下：")
    for info in infos.config_suspicious:
        print(info)

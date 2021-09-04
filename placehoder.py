import json
import sqlite3 as sq

import psutil
from Library.motd import *
import threading
from src import *



def bind(qqid,name,group):
    qxlist = []
    qlist = []
    xlist = []
    conn = sq.connect('data/xuid.db')
    c = conn.cursor()
    cursor = c.execute("SELECT *  from xboxid")
    for row in cursor:
        qq = row[0]
        xboxid = row[1]
        qxlist.append({'qq':qq,'id':xboxid})
        qlist.append(qq)
        xlist.append(xboxid)
    conn.close()

    #检测QQ是否绑定
    if qqid in qlist:
        for i in qxlist:
            if qqid == i['qq']:
                if Language['QQBinded'] != False:
                    sendGroupMsg(group,Language['QQBinded'].replace(r'%xboxid%',i['id']))
                return False

    #检测Xboid是否绑定
    if name in xlist:
        for i in qxlist:
            if name == i['id']:
                if Language['XboxIDBinded'] != False:
                    sendGroupMsg(group,Language['XboxIDBinded'].replace(r'%binderqq%',str(i['qq'])))
                return False

    #全部都不符合自动绑定
    conn = sq.connect('data/xuid.db')
    c = conn.cursor()
    c.execute("INSERT INTO xboxid (qq,xboxid) \
      VALUES (%i,'%s')" % (qqid,name))
    conn.commit()
    conn.close()
    #发群消息
    if Language['BindSuccessful'] != False:
        sendGroupMsg(group,Language['BindSuccessful'].replace(r'%xboxid%',name))
    #更改群名片
    if config['AtNoXboxid']['Rename']:
        changeName(qqid,group,name)
    #自动添加白名单
    if config['AutoBindWhitelist']:
        if __name__ == '__main__':
            from index import Botruncmd
            Botruncmd('whitelist add "%s"' % name)

#获取cpu状态
def getcpupercent():
    global cpup
    cpup = 0
    while True:
        psutil.cpu_percent(None)
        time.sleep(0.5)
        cpup = str(psutil.cpu_percent(None))
        time.sleep(2)

cp = threading.Thread(target=getcpupercent)
cp.setName('GetCpuPercent')
cp.start()

#

#解除绑定
def unbind(qqid,group):
    qxlist = []
    qlist = []
    xlist = []
    conn = sq.connect('data/xuid.db')
    c = conn.cursor()
    cursor = c.execute("SELECT *  from xboxid")
    for row in cursor:
        qq = row[0]
        xboxid = row[1]
        qxlist.append({'qq':qq,'id':xboxid})
        qlist.append(qq)
        xlist.append(xboxid)
    conn.close()
    #检测是否绑定
    if qqid in qlist:
        for i in qxlist:
            if i['qq'] == qqid:
                if Language['unBindSuccessful'] != False:
                    sendGroupMsg(group,Language['unBindSuccessful'].replace(r'%xboxid%',i['id']))
        conn = sq.connect('data/xuid.db')
        c = conn.cursor()
        c.execute("DELETE from xboxid where qq=%i;" % (qqid,))
        conn.commit()
        if config['AtNoXboxid']['Rename']:
            changeName(qqid,group,'')
    else:
        if Language['NotFoundXboxID'] != False:
            sendGroupMsg(group,Language['NotFoundXboxID'])


def replaceconsole(string):
    with open('Temp\\data','r') as f:
        Port = f.read()
    motdinfo = Server('127.0.0.1',int(Port)).motd()
    if motdinfo['status'] == 'online':
        server_motd = motdinfo['name']
        server_version = motdinfo['version']
        server_online = motdinfo['online']
        server_maxonline = motdinfo['upperLimit']
        server_levelname = motdinfo['save']
    else:
        server_motd = '服务器未启动'
        server_version = '服务器未启动'
        server_online = '0'
        server_maxonline = '0'
        server_levelname = '服务器未启动'
    # 系统的CPU利用率
    cpu = str(cpup)+'%'
    mem = psutil.virtual_memory()
    ram_1 = str(mem.total)+'%'
    ram_2 = str(int((mem.free/1024)/1024))+'MB'
    ram_3 = str(int((mem.used/1024)/1024))+'MB'
    ram_4 = str(mem.percent)+'%'
    s = string.replace(r'%cpu%',cpu).replace(r'%ram_1%',ram_1).replace(r'%ram_2%',ram_2).replace(r'%ram_3%',ram_3)\
            .replace(r'%ram_4%',ram_4).replace(r'%server_motd%',server_motd).replace(r'%server_version%',server_version)\
                .replace(r'%server_online%',server_online).replace(r'server_maxonline',server_maxonline).replace(r'%server_levelname%',server_levelname).replace('\\n','\n')
    return s

def replacegroup(string,qqnick,qqid):
    with open('Temp\\data','r') as f:
        Port = f.read()
    motdinfo = Server('localhost',int(Port)).motd()
    if motdinfo['status'] == 'online':
        server_motd = motdinfo['name']
        server_version = motdinfo['version']
        server_online = motdinfo['online']
        server_maxonline = motdinfo['upperLimit']
        server_levelname = motdinfo['save']
    else:
        server_motd = '服务器未启动'
        server_version = '服务器未启动'
        server_online = '0'
        server_maxonline = '0'
        server_levelname = '服务器未启动'
    # 系统的CPU利用率
    cpu = str(cpup)+'%'
    mem = psutil.virtual_memory()
    ram_1 = str(mem.total)+'%'
    ram_2 = str(int((mem.free/1024)/1024))+'MB'
    ram_3 = str(int((mem.used/1024)/1024))+'MB'
    ram_4 = str(mem.percent)+'%'
    #自动以qq号查找xboxid
    conn = sq.connect('data/xuid.db')
    c = conn.cursor()
    cursor = c.execute("SELECT *  from xboxid")
    xboxid = r'%xboxid%'
    for row in cursor:
        qq = row[0]
        if qqid == qq:
            xboxid = row[1]
    conn.close()
    #替换文本
    s = string.replace(r'%qqnick%',qqnick).replace(r'%qqid%',str(qqid)).replace(r'%xboxid%',xboxid)\
        .replace(r'%cpu%',cpu).replace(r'%ram_1%',ram_1).replace(r'%ram_2%',ram_2).replace(r'%ram_3%',ram_3)\
            .replace(r'%ram_4%',ram_4).replace(r'%server_motd%',server_motd).replace(r'%server_version%',server_version)\
                .replace(r'%server_online%',server_online).replace(r'%server_maxonline%',server_maxonline).replace(r'%server_levelname%',server_levelname).replace('\\n','\n')
    return s

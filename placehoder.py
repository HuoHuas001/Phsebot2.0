import sqlite3 as sq
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
                sendGroupMsg(group,Language['QQBinded'].replace(r'%xboxid%',i['id']))
                return False

    #检测Xboid是否绑定
    if name in xlist:
        for i in qxlist:
            if name == i['id']:
                sendGroupMsg(group,Language['XboxIDBinded'].replace(r'%binderqq%',str(i['qq'])))
                return False

    #全部都不符合自动绑定
    conn = sq.connect('data/xuid.db')
    c = conn.cursor()
    c.execute("INSERT INTO xboxid (qq,xboxid) \
      VALUES (%i,'%s')" % (qqid,name))
    conn.commit()
    conn.close()
    sendGroupMsg(group,Language['BindSuccessful'].replace(r'%xboxid%',name))

#解除绑定
def unbind(qqid,group):
    "unBindSuccessful"
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
                print('sended')
                sendGroupMsg(group,Language['unBindSuccessful'].replace(r'%xboxid%',i['id']))
        conn = sq.connect('data/xuid.db')
        c = conn.cursor()
        c.execute("DELETE from xboxid where qq=%i;" % (qqid,))
        conn.commit()
        
    else:
        sendGroupMsg(group,Language['NotFoundXboxID'])

def replacestr(string,qqnick,qqid,xboxid):
    """
%cpu%	√	√	当前CPU占用率(%)
%ram_1%	√	√	总物理内存(MB)
%ram_2%	√	√	可用物理内存(MB)
%ram_3%	√	√	已用物理内存(MB)
%ram_4%	√	√	物理内存使用率(%)
%qqnick%	√		发言人的群名片，未设置群名片则替换为昵称
%qqid%	√		发言人的QQ号
%xboxid%	√		发言人绑定的XboxID
%server_motd%	√	√	服务器介绍（目前好像只有ez可以改）
%server_version%	√	√	服务端版本
%server_online%	√	√	服务器在线人数
%server_maxonline%	√	√	服务器最大在线人数
%server_levelname%	√	√	服务器当前存档名
    """
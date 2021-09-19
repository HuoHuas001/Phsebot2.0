import json
import os
import re
import socket
import sqlite3 as sq
import threading
import time
import tkinter as tk
import urllib.request
import webbrowser
from datetime import date, datetime
from json.decoder import JSONDecodeError
from tkinter import messagebox as mBox
from tkinter import ttk

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        if '.json' in file:
            content = f.read().replace('\\n','\n')
            return json.loads(content)
        elif '.yml' in file:
            content = f.read().replace('\\n','\n')
            return yaml.load(content, Loader=yaml.FullLoader)

import psutil
import yaml
from websocket import create_connection
import Library.Libs.motd as motd
from Library.Libs.Logger import log_debug, log_error, log_info, log_warn
from main import *
from Library.Libs.global_var import *


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

def write_file(file,content):
    with open(file,'w',encoding='utf-8') as f:
        json.dump(content, f, indent=4, ensure_ascii=False, cls=ComplexEncoder)



def testupdate():
    try:
        log_info(PLP['Update.updating'])
        '''with open('FeHelper-20210913195839.json','r',encoding='utf8') as f:
            update = json.loads(f.read())'''
        update = json.loads(urllib.request.urlopen('https://api.github.com/repos/HuoHuas001/Phsebot/releases').read().decode("utf-8"))
        #请求更新版本号
        VERSION = ''
        BV = ''
        # HotFix
        for i in update[0]['name']:
            if i.isdigit():
                VERSION += i
        for i in BotVersion:
            if i.isdigit():
                BV += i
        VERSION = int(VERSION)
        BV = int(BV)

        #检测普通版本
        if VERSION > BV:
            title = PLP['Update.NewVersion']
            if update[0]['body'] != '':
                title += '\n'+PLP['Update.log']+update[0]['body']
            if mBox.askyesno(PLP['Update.title'],title):  
                webbrowser.open('https://gitee.com/HuoHuas001/Phsebot/releases/')
        elif VERSION > BV and 'HotFix' in update[0]['name'] and 'HotFix' not in BotVersion:
            title = PLP['Update.NewVersion']
            if update[0]['body'] != '':
                title += '\n'+PLP['Update.log']+update[0]['body']
            if mBox.askyesno(PLP['Update.title'],title):  
                webbrowser.open('https://gitee.com/HuoHuas001/Phsebot/releases/')
        else:
            log_info(PLP['Update.last'])

        #Beta版本提醒
        if 'Beta' in BotVersion:
            mBox.showwarning('Warning','This is a beta version of Phsebot, please timely feedback bugs')
    except Exception as e:
        log_debug(e)
        log_error(PLP['Update.faild'])


def bind(qqid,name,group):
    from main import bot
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
                    bot.sendGroupMsg(group,Language['QQBinded'].replace(r'%xboxid%',i['id']))
                return False

    #检测Xboid是否绑定
    if name in xlist:
        for i in qxlist:
            if name == i['id']:
                if Language['XboxIDBinded'] != False:
                    bot.sendGroupMsg(group,Language['XboxIDBinded'].replace(r'%binderqq%',str(i['qq'])))
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
        bot.sendGroupMsg(group,Language['BindSuccessful'].replace(r'%xboxid%',name))
    #更改群名片
    if config['AtNoXboxid']['Rename']:
        bot.changeName(qqid,group,name)

#获取cpu状态
cpup = 0
def getcpupercent():
    global cpup
    while True:
        psutil.cpu_percent(None)
        time.sleep(0.5)
        cpup = str(psutil.cpu_percent(None))
        time.sleep(2)



#解除绑定
def unbind(qqid,group):
    from main import bot
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
                    bot.sendGroupMsg(group,Language['unBindSuccessful'].replace(r'%xboxid%',i['id']))
        conn = sq.connect('data/xuid.db')
        c = conn.cursor()
        c.execute("DELETE from xboxid where qq=%i;" % (qqid,))
        conn.commit()
        if config['AtNoXboxid']['Rename']:
            bot.changeName(qqid,group,'')
    else:
        if Language['NotFoundXboxID'] != False:
            bot.sendGroupMsg(group,Language['NotFoundXboxID'])

def get_week_t():
  week_day_dict = {
    0 : '一',
    1 : '二',
    2 : '三',
    3 : '四',
    4 : '五',
    5 : '六',
    6 : '天',
  }
  day = datetime.now().weekday()
  return week_day_dict[day]

def get_week_j():
  week_day_dict = {
    0 : '日',
    1 : '月',
    2 : '火',
    3 : '水',
    4 : '木',
    5 : '金',
    6 : '土',
  }
  day = datetime.now().weekday()
  return week_day_dict[day]

def getAPM():
    h = int(datetime.now().strftime('%H'))
    if h < 12:
        return 'AM'
    else:
        return 'PM'

def replaceconsole(string):
    with open('Temp\\data','r') as f:
        Port = f.read()
    motdinfo = motd.Server('127.0.0.1',int(Port)).motd()
    if motdinfo['status'] == 'online':
        server_motd = motdinfo['name']
        server_version = motdinfo['version']
        server_online = motdinfo['online']
        server_maxonline = motdinfo['upperLimit']
        server_levelname = motdinfo['save']
    else:
        server_motd = PLP['Server.Norun']
        server_version = PLP['Server.Norun']
        server_online = '0'
        server_maxonline = '0'
        server_levelname = PLP['Server.Norun']
    # 系统的CPU利用率
    cpu = str(cpup)+'%'
    mem = psutil.virtual_memory()
    ram_1 = str(mem.total)+'%'
    ram_2 = str(int((mem.free/1024)/1024))+'MB'
    ram_3 = str(int((mem.used/1024)/1024))+'MB'
    ram_4 = str(mem.percent)+'%'
    #时间类
    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H:%M:%S')
    year = datetime.now().strftime('%Y')
    month = datetime.now().strftime('%m')
    hour_12 = str(int(datetime.now().strftime('%H'))-12)
    hour_24 = datetime.now().strftime('%H')
    week_n = str(datetime.now().weekday()+1)
    week_t = get_week_t()
    week_j = get_week_j()
    day = datetime.now().strftime('%d')
    APM = getAPM()
    mins = datetime.now().strftime('%M')
    sec = datetime.now().strftime('%S')
    s = string.replace(r'%cpu%',cpu)\
        .replace(r'%ram_1%',ram_1)\
        .replace(r'%ram_2%',ram_2)\
        .replace(r'%ram_3%',ram_3)\
        .replace(r'%ram_4%',ram_4)\
        .replace(r'%server_motd%',server_motd)\
        .replace(r'%server_version%',server_version)\
        .replace(r'%server_online%',server_online)\
        .replace(r'server_maxonline',server_maxonline)\
        .replace(r'%server_levelname%',server_levelname)\
        .replace('\\n','\n')\
        .replace(r'%date%',date)\
        .replace(r'%time%',time)\
        .replace(r'%year%',year)\
        .replace(r'%month%',month)\
        .replace(r'%week_n%',week_n)\
        .replace(r'%week_t%',week_t)\
        .replace(r'%week_j%',week_j)\
        .replace(r'%day%',day)\
        .replace(r'%hour_12%',hour_12)\
        .replace(r'%hour_24%',hour_24)\
        .replace(r'%ampm%',APM)\
        .replace(r'%min%',mins)\
        .replace(r'%sec%',sec)
    return s

def replacegroup(string,qqnick,qqid):
    with open('Temp\\data','r') as f:
        Port = f.read()
    motdinfo = motd.Server('localhost',int(Port)).motd()
    if motdinfo['status'] == 'online':
        server_motd = motdinfo['name']
        server_version = motdinfo['version']
        server_online = motdinfo['online']
        server_maxonline = motdinfo['upperLimit']
        server_levelname = motdinfo['save']
    else:
        server_motd = PLP['Server.Norun']
        server_version = PLP['Server.Norun']
        server_online = '0'
        server_maxonline = '0'
        server_levelname = PLP['Server.Norun']
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
    #时间类
    date = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H:%M:%S')
    year = datetime.now().strftime('%Y')
    month = datetime.now().strftime('%m')
    hour_12 = str(int(datetime.now().strftime('%H'))-12)
    hour_24 = datetime.now().strftime('%H')
    week_n = str(datetime.now().weekday()+1)
    week_t = get_week_t()
    week_j = get_week_j()
    day = datetime.now().strftime('%d')
    APM = getAPM()
    mins = datetime.now().strftime('%M')
    sec = datetime.now().strftime('%S')
    #替换文本
    s = string.replace(r'%qqnick%',qqnick)\
        .replace(r'%qqid%',str(qqid))\
        .replace(r'%xboxid%',xboxid)\
        .replace(r'%cpu%',cpu)\
        .replace(r'%ram_1%',ram_1)\
        .replace(r'%ram_2%',ram_2)\
        .replace(r'%ram_3%',ram_3)\
        .replace(r'%ram_4%',ram_4)\
        .replace(r'%server_motd%',server_motd)\
        .replace(r'%server_version%',server_version)\
        .replace(r'%server_online%',server_online)\
        .replace(r'%server_maxonline%',server_maxonline)\
        .replace(r'%server_levelname%',server_levelname)\
        .replace('\\n','\n')\
        .replace(r'%date%',date)\
        .replace(r'%time%',time)\
        .replace(r'%year%',year)\
        .replace(r'%month%',month)\
        .replace(r'%week_n%',week_n)\
        .replace(r'%week_t%',week_t)\
        .replace(r'%week_j%',week_j)\
        .replace(r'%day%',day)\
        .replace(r'%hour_12%',hour_12)\
        .replace(r'%hour_24%',hour_24)\
        .replace(r'%ampm%',APM)\
        .replace(r'%min%',mins)\
        .replace(r'%sec%',sec)
    return s

if __name__ == '__main__':
    os._exit(0)
else:
    cp = threading.Thread(target=getcpupercent)
    cp.setName('GetCpuPercent')
    cp.start()
    
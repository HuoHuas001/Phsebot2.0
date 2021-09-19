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

import psutil
import yaml
from websocket import create_connection

from Library.Logger import log_debug, log_error, log_info, log_warn
from Library.motd import *


def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        if '.json' in file:
            content = f.read().replace('\\n','\n')
            return json.loads(content)
        elif '.yml' in file:
            content = f.read().replace('\\n','\n')
            return yaml.load(content, Loader=yaml.FullLoader)

 
def checkprocess(processname):
    try:
        pl = psutil.pids()
        for pid in pl:
            if psutil.Process(pid).name() == processname:
                return True
    except:
        return True

 
def check(p):
    if p.poll() == None:
        return True
    else:
        return False


def sendGroupMsg(group,text):
    global num
    s = threading.Thread(target=Sbot.sendGroupMsg2,args=(group,text))
    s.setName('SendGroupMsg'+str(num))
    s.start()
    num += 1

# 弹窗
class PopupDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__()
        self.title('Phsebot - '+PLP['EditConfig.title'])
        
        self.parent = parent # 显式地保留父窗口
        self.iconbitmap(r'Library/Images/bot.ico')
        self.geometry('400x205')
        self.resizable(0,0)
        ms = ttk.LabelFrame(self, text=PLP['EditConfig.frame'],width=9,height=10)
        ms.grid(column=0, row=0, padx=7, pady=4)
        
        # 第一行（两列）
        row1 = tk.Frame(ms)
        row1.pack(fill="x")
        tk.Label(row1, text=PLP['EditConfig.EditPath'], width=10).pack(side=tk.LEFT,pady=4)
        self.path = tk.StringVar()
        self.path.set(config['ServerPath'])
        path = tk.Entry(row1, textvariable=self.path, width=42)
        path.pack(side=tk.LEFT)
        
        # 第二行
        row2 = tk.Frame(ms)
        row2.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row2, text=PLP['EditConfig.EditFile'], width=10).pack(side=tk.LEFT,pady=4)
        self.file = tk.StringVar()
        self.file.set(config['ServerCmd'])
        file = tk.Entry(row2, textvariable=self.file, width=42)
        file.pack(side=tk.LEFT)

        # 第三行
        row3 = tk.Frame(ms)
        row3.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row3, text=PLP['EditConfig.AdminList'], width=10).pack(side=tk.LEFT,pady=4)
        self.admin = tk.StringVar()
        admins = ''
        for i in config['Admin']:
            if admins == '':
                admins += str(i)
            else:
                admins += '|'+str(i)
        self.admin.set(admins)
        admin = tk.Entry(row3, textvariable=self.admin, width=42)
        admin.pack(side=tk.LEFT)

        # 第四行
        row4 = tk.Frame(ms)
        row4.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row4, text=PLP['EditConfig.Group'], width=10).pack(side=tk.LEFT,pady=4)
        self.group = tk.StringVar()
        groups = ''
        for i in config['Group']:
            if groups == '':
                groups += str(i)
            else:
                groups += '|'+str(i)
        self.group.set(groups)
        group = tk.Entry(row4, textvariable=self.group, width=42)
        group.pack(side=tk.LEFT)

        #第五行
        row5 = tk.Frame(ms)
        row5.pack(fill="x")
        self.autostatus=tk.IntVar()
        self.auto = tk.Checkbutton(row5, text=PLP['EditConfig.Restart'],variable=self.autostatus)
        if config['AutoRestart']:
            self.auto.select()
        self.auto.pack(side=tk.LEFT)
        
        # 第六行
        row6 = tk.Frame(ms)
        row6.pack(fill="x")
        tk.Button(row6, text=PLP['EditConfig.Save'], command=self.ok).pack(side=tk.LEFT)
        tk.Button(row6, text=PLP['EditConfig.Canel'], command=self.cancel).pack(side=tk.RIGHT)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        
    def on_closing(self):
        if mBox.askyesno(PLP['EditConfig.Ask'],PLP['EditConfig.Message']):
            self.ok()
        else:
            self.cancel()

        
    def ok(self):
        # 显式地更改父窗口参数

        #文件
        config['ServerCmd'] = self.file.get()

        #路径
        config['ServerPath'] = self.path.get()

        #管理员列表
        admins = []
        for i in self.admin.get().split('|'):
            admins.append(int(i))
        config['Admin'] = admins

        #群组列表
        groups = []
        for i in self.group.get().split('|'):
            groups.append(int(i))
        config['Group'] = groups

        #自动重启
        auto = False
        if self.autostatus.get() == 1:
            auto = True
        else:
            auto = False
        config['AutoRestart'] = auto

        #写入文件
        with open('data/config.yml','w') as f:
            y = yaml.dump(config)
            f.write(y)

        
        #写入bat
        with open('Library\index.bat','w') as f:
            run = '''@echo off
cd "%s"
%s'''
            f.write(run % (config['ServerPath'],config['ServerCmd']))
        
        self.destroy() # 销毁窗口
        
    def cancel(self):
        self.destroy()





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
        update = json.loads(urllib.request.urlopen('https://api.github.com/repos/HuoHuas001/Phsebot2.0/releases').read().decode("utf-8"))
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
                webbrowser.open('https://github.com/HuoHuas001/Phsebot2.0/releases')
        elif VERSION > BV and 'HotFix' in update[0]['name'] and 'HotFix' not in BotVersion:
            title = PLP['Update.NewVersion']
            if update[0]['body'] != '':
                title += '\n'+PLP['Update.log']+update[0]['body']
            if mBox.askyesno(PLP['Update.title'],title):  
                webbrowser.open('https://github.com/HuoHuas001/Phsebot2.0/releases')
        else:
            log_info(PLP['Update.last'])

        #Beta版本提醒
        if 'Beta' in BotVersion:
            mBox.showwarning('Warning','This is a beta version of Phsebot, please timely feedback bugs')
    except Exception as e:
        log_debug(e)
        log_error(PLP['Update.faild'])


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
        Sbot.changeName(qqid,group,name)

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
            Sbot.changeName(qqid,group,'')
    else:
        if Language['NotFoundXboxID'] != False:
            sendGroupMsg(group,Language['NotFoundXboxID'])

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
    motdinfo = Server('127.0.0.1',int(Port)).motd()
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
    motdinfo = Server('localhost',int(Port)).motd()
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

def send_app(ws,group,code):
    msgjson = {
        "target":group,
        "messageChain":[{
    "type": "App",
    "content": code
}]
    }
    mj = {
        "syncId": 12345,
        "command": "sendGroupMessage",
        "subCommand": None,
        "content": msgjson
    }
    ws.send(json.dumps(mj))



def ChangeBotName(Started):
    if Started:
        with open('Temp\\data','r') as f:
            Port = f.read()
        Motd = Server('127.0.0.1',int(Port)).motd()
        if Motd['status'] == 'online':
            server_online = Motd['online']
            server_maxonline = Motd['upperLimit']
            for i in config['Group']:
                Sbot.changeName(config['Bot'],i,config['AutoChangeBotName']['String'].replace(r'%Online%',str(server_online))\
                    .replace(r'%Max%',str(server_maxonline)))
    else:
        if config['AutoChangeBotName']['StopReset'] != False:
            for i in config['Group']:
                Sbot.changeName(config['Bot'],i,config['AutoChangeBotName']['StopReset'])

class Bot():
    def __init__(self) -> None:
        pass

    def login(self):
        try:
            key = config['Key']
            url = config['BotURL']
            self.ws = create_connection(url+'/all?verifyKey=%s&qq=%i' % (key,config['Bot']))
            self.connect = True
            log_info('%i %s' % (config['Bot'],PLP['Login.success']))
            return True
        except Exception as e:
            self.connect = False
            log_debug(e)
            return False

    def send_at(self,group,senderqq,msg):
        msgjson = {
            "target":group,
            "messageChain":[{"type": "At", "target": senderqq, "display": ""}]
        }
        if msg != False:
            msgjson['messageChain'].append({"type":"Plain", "text":msg})

        mj = {
            "syncId": 1234,
            "command": "sendGroupMessage",
            "subCommand": None,
            "content": msgjson
        }
        self.ws.send(json.dumps(mj))


    def recallmsg(self,Sourceid):
        recjson = {
            "target":Sourceid
        }
        mj = {
            "syncId": 12345,
            "command": "recall",
            "subCommand": None,
            "content": recjson
        }
        self.ws.send(json.dumps(mj))

    #修改群名
    def changeName(self,member,group,name):
        namejson = {
            "target": group,
            "memberId": member,
            "info": {
                "name": name,
            }
        }
        mj = {
            "syncId": 1234,
            "command": "memberInfo",
            "subCommand": 'update',
            "content": namejson
        }
        self.ws.send(json.dumps(mj))

    def sendGroupMsg2(self,group,text):
        try:
            msgjson = {
            "target":group,
            "messageChain":[
                { "type":"Plain", "text":text.replace('\\n','\n')},
            ]
        }
            mj = {
            "syncId": 123,
            "command": "sendGroupMessage",
            "subCommand": None,
            "content": msgjson
        }
            self.ws.send(json.dumps(mj))
        except Exception as e:
            log_debug(e)

def reconnect():
    disconnect()
    log_info(PLP['Mirai.reconnect'])
    if not Sbot.login():
        log_error(PLP['Mirai.reconnect.faild'])

def disconnect():
    try:
        Sbot.ws.close(0)
    except AttributeError:
        pass

    

if __name__ == '__main__':
    os._exit(0)
else:
    cp = threading.Thread(target=getcpupercent)
    cp.setName('GetCpuPercent')
    cp.start()
    config = read_file('data/config.yml')
    Language = read_file('data/Language.yml')
    cron = read_file('data/Cron.json')
    NoOut = read_file('data/NoOut.yml')
    PLP = read_file('Library/Language/'+config['LangPack']+'.yml')
    num = 0
    BotVersion = '2.0.1-release'
    HotFix = True
    from botmain import BDSServer,Window
    server = BDSServer()
    window_root = Window()
    window_root.create_window_content()
    Sbot = Bot()
    if Sbot.login():
        pass
    else:
        mBox.showerror(PLP['Start.Connect.Faild.title'],PLP['Start.Connect.Faild.message'])
    

        
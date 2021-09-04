import json
import os
import re
import socket
import sqlite3 as sq
import threading
import time
import tkinter as tk
import webbrowser
from datetime import date, datetime
from json.decoder import JSONDecodeError
from tkinter import messagebox as mBox
from tkinter import ttk

import psutil
import requests
import yaml
from websocket import create_connection
from Library.motd import *

from Library.Logger import log_error, log_info, log_warn


def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        if '.json' in file:
            content = f.read()
            return json.loads(content)
        elif '.yml' in file:
            content = f.read()
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
    if checkprocess(p):
        return True
    else:
        return False


def loginQQ():
    global sessionKey
    url = config["BotURL"]
    key = config['Key']
    qq = config['Bot']
    try:
        authCode = requests.post(url+'/verify',json={"verifyKey":key})
    except:
        mBox.showwarning('Phsebot', '无法连接到Mirai，请检查地址是否正确或是否开启')
        os._exit(0)

    authCode = json.loads(authCode.text)
    if authCode['code'] == 0:
        sessionKey = authCode['session']
        bindCode = requests.post(url+'/bind',json={"sessionKey":sessionKey,'qq':qq})
        bindCode = json.loads(bindCode.text)
        if bindCode['code'] == 0:
            log_info('%i 登陆成功' % (qq))
    else:
        sessionKey = ''
        log_error('在登录时出现了错误')

def sendGroupMsg(group,text):
    global num
    s = threading.Thread(target=sendGroupMsg2,args=(group,text))
    s.setName('SendGroupMsg'+str(num))
    s.start()
    num += 1

def sendGroupMsg2(group,text):
    url = config["BotURL"]
    msgjson = {
        "sessionKey":sessionKey,
        "target":group,
        "messageChain":[
            { "type":"Plain", "text":text.replace('\\n','\n')},
        ]
    }
    r = requests.post(url+'/sendGroupMessage',json=msgjson)
    try:
        j = json.loads(r.text)
        if j['code'] == 0 and j['messageId'] == -1:
            log_warn('消息已发送，但可能遭到屏蔽')
        return True
    except JSONDecodeError as e:
        log_error('发送消息时出现了内部错误')



# 弹窗
class PopupDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__()
        self.title('Phsebot - 编辑配置')
        
        self.parent = parent # 显式地保留父窗口
        self.iconbitmap(r'Library/Images/bot.ico')
        self.geometry('400x205')
        self.resizable(0,0)
        ms = ttk.LabelFrame(self, text='修改配置',width=9,height=10)
        ms.grid(column=0, row=0, padx=7, pady=4)
        
        # 第一行（两列）
        row1 = tk.Frame(ms)
        row1.pack(fill="x")
        tk.Label(row1, text=' 服务端目录：', width=10).pack(side=tk.LEFT,pady=4)
        self.path = tk.StringVar()
        self.path.set(config['ServerPath'])
        path = tk.Entry(row1, textvariable=self.path, width=42)
        path.pack(side=tk.LEFT)
        
        # 第二行
        row2 = tk.Frame(ms)
        row2.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row2, text=' 服务端文件：', width=10).pack(side=tk.LEFT,pady=4)
        self.file = tk.StringVar()
        self.file.set(config['ServerFile'])
        file = tk.Entry(row2, textvariable=self.file, width=42)
        file.pack(side=tk.LEFT)

        # 第三行
        row3 = tk.Frame(ms)
        row3.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row3, text=' 管理员列表：', width=10).pack(side=tk.LEFT,pady=4)
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
        tk.Label(row4, text=' 群消息列表：', width=10).pack(side=tk.LEFT,pady=4)
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
        self.auto = tk.Checkbutton(row5, text="崩服自动重启",variable=self.autostatus)
        if config['AutoRestart']:
            self.auto.select()
        self.auto.pack(side=tk.LEFT)
        
        # 第六行
        row6 = tk.Frame(ms)
        row6.pack(fill="x")
        tk.Button(row6, text="保存", command=self.ok).pack(side=tk.LEFT)
        tk.Button(row6, text="取消", command=self.cancel).pack(side=tk.RIGHT)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        
    def on_closing(self):
        if mBox.askyesno('提示','您确认保存吗？'):
            self.ok()
        else:
            self.cancel()

        
    def ok(self):
        # 显式地更改父窗口参数

        #文件
        config['ServerFile'] = self.file.get()

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
cd %s
%s'''
            f.write(run % (config['ServerPath'],config['ServerFile']))
        
        self.destroy() # 销毁窗口
        
    def cancel(self):
        self.destroy()

#修改群名
def changeName(member,group,name):
    url = config["BotURL"]
    namejson = {
        "sessionKey": sessionKey,
        "target": group,
        "memberId": member,
        "info": {
            "name": name,
        }
    }
    m = requests.post(url+'/memberInfo',json=namejson)
    j = json.loads(m.text)
    if j['code'] == 10:
        log_warn('已尝试修改 %i 的群名片，但没有权限' % member)

#退出释放资源
def releaseSession():
    url = config["BotURL"]
    requests.post(url+'/release',json={'sessionKey':sessionKey,'qq':config['Bot']})



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


def send_at(group,senderqq,msg):
    url = config["BotURL"]
    msgjson = {
        "sessionKey":sessionKey,
        "target":group,
        "messageChain":[{"type": "At", "target": senderqq, "display": ""}]
    }
    if msg != False:
        msgjson['messageChain'].append({"type":"Plain", "text":msg})
    requests.post(url+'/sendGroupMessage',json=msgjson)

def recallmsg(Sourceid):
    url = config["BotURL"]
    recjson = {
        "sessionKey":sessionKey,
        "target":Sourceid
    }
    requests.post(url+'/recall',json=recjson)

def testupdate():
    try:
        log_info('正在请求更新')
        update = json.loads(requests.get('https://api.github.com/repos/HuoHuas001/Phsebot/releases').text)
        if float(update[0]["tag_name"]) > BotVersion:
            if mBox.askyesno('提示','Phsebot有新版本了，是否去更新'):  
                webbrowser.open("https://github.com/HuoHuas001/Phsebot/releases")
        else:
            log_info('该版本是最新版本')
    except:
        log_error('获取更新时失败')


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



config = read_file('data/config.yml')
Language = read_file('data/Language.yml')
cron = read_file('data/Cron.json')
num = 0
BotVersion = 0.8
cp = threading.Thread(target=getcpupercent)
cp.setName('GetCpuPercent')
cp.start()


    
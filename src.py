import psutil
import requests
import socket
import json
import yaml
import threading
import re
import sqlite3
from websocket import create_connection
from tkinter import messagebox as mBox
import os
import tkinter as tk
from tkinter import ttk

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

config = read_file('data/config.yml')
Language = read_file('data/Language.yml')
cron = read_file('data/Cron.json')

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
            print('[INFO] %i 登陆成功' % (qq))
    else:
        print('[ERROR] 在登录时出现了错误')

def sendGroupMsg(group,text):
    s = threading.Thread(target=sendGroupMsg2,args=(group,text))
    s.start()

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
    j = json.loads(r.text)
    if j['code'] == 0 and j['messageId'] == -1:
        print('[INFO] 消息已发送，但可能遭到屏蔽')
    return True

def useconsoleregular(text):
    rt = {}
    regular = {'Console':[],'Group':[],'Msg':[]}
    conn = sqlite3.connect('data/regular.db')
    c = conn.cursor()
    cursor = c.execute("SELECT *  from interactive")
    cmd = ''
    for row in cursor:
        r = row[0]
        by = row[1]
        perm = row[2]
        cmd = row[3]
        if perm == '管理员':
            perm = True
        else:
            perm = False
        if by == '控制台':
            regular['Console'].append({'regular':r,'perm':perm,'run':cmd})
    conn.close()

    for i in regular['Console']:
        p = re.findall(i['regular'],text)
        #执行操作
        if p != []:
            if type(p[0]) == tuple:
                if len(p[0]) == 1:
                    cmd = i['run'].replace('$1',p[0][0])
                elif len(p[0]) == 2:
                    cmd = i['run'].replace('$1',p[0][0]).replace('$2',p[0][1])
                elif len(p[0]) == 3:
                    cmd = i['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2])
                elif len(p[0]) == 4:
                    cmd = i['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2]).replace('$4',p[0][3])
                elif len(p[0]) == 5:
                    cmd = i['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2]).replace('$4',p[0][3]).replace('$5',p[0][4])
                elif len(p[0]) == 6:
                    cmd = i['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2]).replace('$4',p[0][3]).replace('$5',p[0][4]).replace('$6',p[0][5])
                elif len(p[0]) == 7:
                    cmd = i['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2]).replace('$4',p[0][3]).replace('$5',p[0][4]).replace('$6',p[0][5]).replace('$7',p[0][6])
                elif len(p[0]) == 8:
                    cmd = i['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2]).replace('$4',p[0][3]).replace('$5',p[0][4]).replace('$6',p[0][5]).replace('$7',p[0][6]).replace('$8',p[0][7])
                elif len(p[0]) == 9:
                    cmd = i['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2]).replace('$4',p[0][3]).replace('$5',p[0][4]).replace('$6',p[0][5]).replace('$7',p[0][6]).replace('$8',p[0][7]).replace('$9',p[0][8])
            elif type(p[0]) == str:
                cmd = i['run']
            #发群消息
            if i['run'][:2] == '>>':
                for g in config["Group"]:
                    sendGroupMsg(g,cmd[2:])
                rt = {'Type':'Sended'}
            #执行命令
            elif i['run'][:2] == '<<':
                rt = {'Type':'Cmd','Cmd':cmd}
        else:
            rt = {'Type':'None'}
    return rt

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

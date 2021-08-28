
#======================
# imports
#======================
from placehoder import *
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import Spinbox
from tkinter import messagebox as mBox
import subprocess
import threading
import time
from tkinter.constants import END
from src import *
import os
import re
from croniter import croniter
from croniter import CroniterNotAlphaError
from croniter import CroniterBadCronError
from datetime import datetime
from motd import *
from tkinter import *
from json import JSONDecodeError
from placehoder import *
print('[INFO] 启动时间:',datetime.now())

#全局变量
StartedServer = False
Used = False
NormalStop = False
Sended = []


class MultiListbox(Frame):
    def __init__(self,master,lists):
        Frame.__init__(self,master)
        self.lists = []
        for l, w in lists:
            frame = Frame(self)
            frame.pack(side=LEFT, expand=YES, fill=BOTH)
            Label(frame, text=l, borderwidth=1, relief=RAISED).pack(fill=X)
            lb = Listbox(frame, width=w, borderwidth=0, selectborderwidth=0, relief=FLAT, exportselection=FALSE,height=19)
            lb.pack(expand=YES, fill=BOTH)
            self.lists.append(lb)
            lb.bind("<B1-Motion>",lambda e, s=self: s._select(e.y))
            lb.bind("<Button-1>",lambda e,s=self: s._select(e.y))
            lb.bind("<Leave>",lambda e: "break")
            lb.bind("<B2-Motion>",lambda e,s=self: s._b2motion(e.x,e.y))
            lb.bind("<Button-2>",lambda e,s=self: s._button2(e.x,e.y))
        frame = Frame(self)
        frame.pack(side=LEFT, fill=Y)
        Label(frame, borderwidth=1, relief=RAISED).pack(fill=X)
        sb = Scrollbar(frame,orient=VERTICAL, command=self._scroll)
        sb.pack(side=LEFT, fill=Y)
        self.lists[0]["yscrollcommand"] = sb.set

    def _select(self, y):
        row = self.lists[0].nearest(y)
        self.selection_clear(0, END)
        self.selection_set(row)
        return "break"

    def _button2(self, x, y):
        for l in self.lists:
            l.scan_mark(x,y)
        return "break"

    def _b2motion(self, x, y):
        for l in self.lists:
            l.scan_dragto(x, y)
        return "break"

    def _scroll(self, *args):
        for l in self.lists:
            l.yview(*args)
        return "break"

    def curselection(self):
        return self.lists[0].curselection()

    def delete(self, first, last=None):
        for l in self.lists:
            l.delete(first,last)

    def get(self, first, last=None):
        result = []
        for l in self.lists:
            result.append(l.get(first,last))
        if last:
            return map(*[None] + result)
        return result

    def index(self, index):
        self.lists[0],index(index)

    def insert(self, index, *elements):
        for e in elements:
            i = 0
            for l in self.lists:
                l.insert(index, e[i])
                i = i + 1

    def size(self):
        return self.lists[0].size()

    def see(self, index):
        for l in self.lists:
            l.see(index)

    def selection_anchor(self, index):
        for l in self.lists:
            l.selection_anchor(index)

    def selection_clear(self, first, last=None):
        for l in self.lists:
            l.selection_clear(first,last)

    def selection_includes(self, index):
        return self.lists[0].seleciton_includes(index)

    def selection_set(self, first, last=None):
        for l in self.lists:
            l.selection_set(first, last)

 
#由于tkinter中没有ToolTip功能，所以自定义这个功能如下
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
 
    def showtip(self, text):
        try:
            "Display text in tooltip window"
            self.text = text
            if self.tipwindow or not self.text:
                return
            x, y, _cx, cy = self.widget.bbox("insert")
            x = x + self.widget.winfo_rootx() + 27
            y = y + cy + self.widget.winfo_rooty() +27
            self.tipwindow = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(1)
            tw.wm_geometry("+%d+%d" % (x, y))
 
            label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
            label.pack(ipadx=1)
        except TypeError:
            pass
 
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()
            
#===================================================================          
def createToolTip( widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
 
# Create instance
win = tk.Tk()   
 
# Add a title       
win.title("Phsebot")
 
# Disable resizing the GUI
win.resizable(0,0)
 
# Tab Control introduced here --------------------------------------
tabControl = ttk.Notebook(win)          # Create Tab Control
 
tab1 = ttk.Frame(tabControl)            # Create a tab 
tabControl.add(tab1, text='BDS控制台')      # Add the tab
 
tab2 = ttk.Frame(tabControl)            # Add a second tab
tabControl.add(tab2, text='正则表达式')      # Make second tab visible
 
tab3 = ttk.Frame(tabControl)            # Add a third tab
tabControl.add(tab3, text='Cron表达式')      # Make second tab visible
 
tabControl.pack(expand=1, fill="both")  # Pack to make visible
# ~ Tab Control introduced here -----------------------------------------
 
#---------------Tab1控件介绍------------------#
# We are creating a container tab3 to hold all other widgets
'''monty = ttk.LabelFrame(tab1, text='BDS控制台')
monty.grid(column=0, row=0, padx=7'''

monty = ttk.LabelFrame(tab1, text='BDS控制台',width=500,height=100)
monty.grid(column=0, row=0, padx=1, pady=10,)
 
# Modified Button Click Function
def runcmd():
    global NormalStop
    result=nameEntered.get()+'\r\n'
    cmd = result.encode('utf8')
    if cmd == b'stop\r\n':
        NormalStop = True
    obj.stdin.write(cmd)
    obj.stdin.flush()
    nameEntered.delete(0, 'end')

def motdServer(ip,port,group):
    motd = Server(ip,int(port))
    jmotd = motd.motd()
    if jmotd['status'] == 'online':
        sendmsg = Language['MotdSuccessful'].replace(r'%ip%',jmotd['ip']).replace(r'%port%',str(jmotd['port'])).replace(r'%motd%',jmotd['name'])\
            .replace(r'%agreement%',jmotd['protocol']).replace(r'%version%',jmotd['version']).replace(r'%delay%',str(jmotd['delay'])+'ms')\
                .replace(r'%online%',jmotd['online']).replace(r'%max%',jmotd['upperLimit']).replace(r'%gamemode%',jmotd['gamemode'])

        sendGroupMsg(group,sendmsg.replace('\\n','\n'))
    else:
        sendGroupMsg(group,Language['MotdFaild'])

def Botruncmd(text):
    global NormalStop
    result=text+'\r\n'
    cmd = result
    #开服
    if text == 'start':
        if not StartedServer:
            runserver()
        else:
            for i in config['Group']:
                sendGroupMsg(i,Language['ServerRunning'])
                
    #正常关服
    elif text == 'stop':
        NormalStop = True
        if StartedServer:
            obj.stdin.write(cmd.encode('utf8'))
            obj.stdin.flush()
        else:
            for i in config['Group']:
                sendGroupMsg(i,Language['ServerNotRunning'])

    #绑定XboxID
    elif 'bindid' in text:
        args = text.split(' ')
        qqid = int(args[1])
        group = int(args[-1])
        name = args[2]
        bind(qqid,name,group)

    #解绑XboxID
    elif 'unbind' in text:
        args = text.split(' ')
        qqid = int(args[1])
        group = int(args[-1])
        unbind(qqid,group)

    #Motd请求
    elif 'motd' in text:
        args = text.split(' ')
        addr = ''
        port = ''
        group = int(args[-1])
        args.remove(str(group))
        #匹配域名
        for i in args:
            if re.search(r'(([01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])\.){3}([01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])',i) or re.search(r'[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+.?',i):
                addr = i
        #赋值地址
        if ':' in addr:
            d = addr.split(':')
            addr = d[0]
            port = d[1]
        else:
            port = '19132'

        m = threading.Thread(target=motdServer,args=(addr,port,group))
        m.setName('MotdServer')
        m.start()

    #执行指令
    else:
        if StartedServer:
            obj.stdin.write(cmd.encode('utf8'))
            obj.stdin.flush()
        else:
            for i in config['Group']:
                sendGroupMsg(i,Language['ServerNotRunning'])

def checkBDS():
    global StartedServer
    time.sleep(1)
    while True:
        time.sleep(1)
        if not check(config['ServerFile']) and NormalStop == True and StartedServer:
            runserverb.configure(state='normal')
            runserverc.configure(state='normal')
            stoper.configure(state='disabled')
            StartedServer = False
            scr.insert('end','[INFO] 进程已停止')
            ServerNow.configure(text='服务器状态：未启动')
            GameFile.configure(text='服务器存档：')
            GameVersion.configure(text='服务器版本：')
            break
        elif not check(config['ServerFile']) and NormalStop == False and config['AutoRestart'] and StartedServer:
            for i in config['Group']:
                sendGroupMsg(i,Language['AbendServer'])
                sendGroupMsg(i,Language['RestartServer'])
            ServerNow.configure(text='服务器状态：未启动')
            GameFile.configure(text='服务器存档：')
            GameVersion.configure(text='服务器版本：')
            runserver()
            break
        elif not check(config['ServerFile']) and NormalStop == False and config['AutoRestart'] == False and StartedServer:
            for i in config['Group']:
                sendGroupMsg(i,Language['AbendServer'])
            runserverb.configure(state='normal')
            runserverc.configure(state='normal')
            stoper.configure(state='disabled')
            StartedServer = False
            scr.insert('end','[INFO] 进程已停止')
            ServerNow.configure(text='服务器状态：未启动')
            GameFile.configure(text='服务器存档：')
            GameVersion.configure(text='服务器版本：')
            break

def showinfo():
    global StartedServer,Version,Sended,World,ServerPort
    line = []
    updateLine = ''
    
    while StartedServer:
        time.sleep(0.0005)
        obj.stdin.flush()
        if os.path.isfile('console.txt'):
            with open('console.txt','r',encoding='utf8') as f:
                lines = f.readlines()
                if line == []:
                    line = lines
                else:
                    if lines != line:
                        line = lines
                        try:
                            updateLine = lines[-1]
                            back = useconsoleregular(updateLine)
                            #玩家退服
                            if re.findall(r'^\[INFO\]\sPlayer\sdisconnected:\s(.+?),\sxuid:\s(.+?)$',updateLine) != [] and Language['PlayerJoin'] != False:
                                r = re.findall(r'^\[INFO\]\sPlayer\sdisconnected:\s(.+?),\sxuid:\s(.+?)$',updateLine)
                                for g in config["Group"]:
                                    sendGroupMsg(g,Language['PlayerLeft'].replace('%player%',r[0][0]).replace(r'%xuid%',r[0][1]))

                            #玩家进服
                            if re.findall(r'^\[INFO\]\sPlayer\sconnected:\s(.+?),\sxuid:\s(.+?)$',updateLine) != [] and Language['PlayerJoin'] != False:
                                r = re.findall(r'^\[INFO\]\sPlayer\sconnected:\s(.+?),\sxuid:\s(.+?)$',updateLine)
                                for g in config["Group"]:
                                    sendGroupMsg(g,Language['PlayerJoin'].replace('%player%',r[0][0]).replace(r'%xuid%',r[0][1]))

                            if back['Type'] == 'Cmd':
                                Botruncmd(back['Cmd'])
                        except IndexError:
                            pass

                        scr.delete(1.0,'end')
                        scr.insert('end','[INFO] 进程已开始\n')
                        for i in lines:
                            scr.insert('end',i)
                            #版本
                            if 'INFO] Version' in i:
                                Version = re.findall(r'Version\s(.+?)[\r\s]',i)[0]
                                GameVersion.configure(text='服务器版本：'+Version)
                                d = read_file('Temp/data.json')
                                d['Version'] = Version
                                write_file('Temp/data.json',d)
                                if 'SendedVersion' not in Sended:
                                    Sended.append('SendedVersion')
                                    if Language['ServerVersion'] != False:
                                        for b in config["Group"]:
                                            sendGroupMsg(b,Language['ServerVersion'].replace('%Version%',Version))
                            #打开世界
                            if 'opening' in i:
                                World = re.findall(r'opening\s(.+?)[\r\s]',i)[0]
                                GameFile.configure(text='服务器存档：'+World)
                                d = read_file('Temp/data.json')
                                d['World'] = World
                                write_file('Temp/data.json',d)
                                if 'OpenWorld' not in Sended:
                                    Sended.append('OpenWorld')
                                    if Language['OpenWorld'] != False:
                                        for b in config["Group"]:
                                            sendGroupMsg(b,Language['OpenWorld'].replace('%World%',World))

                            #加载端口
                            if 'IPv4' in i:
                                Port = int(re.findall(r'^\[INFO\]\sIPv4\ssupported,\sport:\s(.+?)$',i)[0])
                                d = read_file('Temp/data.json')
                                d['Port'] = Port
                                write_file('Temp/data.json',d)
                                if 'PortOpen' not in Sended:
                                    Sended.append('PortOpen')
                                    if Language['PortOpen'] != False:
                                        for b in config["Group"]:
                                            sendGroupMsg(b,Language['PortOpen'].replace('%Port%',str(Port)))

                            #开服完成
                            if 'Server started.' in i:
                                if 'ServerStart' not in Sended:
                                    Sended.append('ServerStart')
                                    if Language['ServerStart'] != False:
                                        for b in config["Group"]:
                                            sendGroupMsg(b,Language['ServerStart'])

                            #关服中
                            if '[INFO] Server stop requested.' in i:
                                if 'ServerStopping' not in Sended:
                                    Sended.append('ServerStopping')
                                    if Language['ServerStopping'] != False:
                                        for b in config["Group"]:
                                            sendGroupMsg(b,Language['ServerStopping'])

                            #关服完成
                            if 'Quit correctly' in i:
                                if 'ServerStoped' not in Sended:
                                    Sended.append('ServerStoped')
                                    if Language['ServerStoped'] != False:
                                        for b in config["Group"]:
                                            sendGroupMsg(b,Language['ServerStoped'])

                            #崩溃
                            if 'Crashed' in i:
                                if 'Crashed' not in Sended:
                                    Sended.append('Crashed')
                                    if Language['Crashed'] != False:
                                        for b in config["Group"]:
                                            sendGroupMsg(b,Language['Crashed'])

                        scr.see(END)

def stoperd():
    global NormalStop
    answer = mBox.askyesno("强制停止服务器", "你确定吗？") 
    if answer == True:
        NormalStop = True
        os.system('taskkill /f /im %s' % config['ServerFile'])
        for i in config['Group']:
            sendGroupMsg(i,Language['ForcedStop'])
        
def runserver():
    global obj,StartedServer,Sended,NormalStop
    NormalStop = False
    Sended = []
    StartedServer = True
    nameEntered.configure(state='normal')
    action.configure(state='normal')
    scr.delete(1.0,'end')
    runserverb.configure(state='disabled')
    runserverc.configure(state='disabled')
    stoper.configure(state='normal')
    ServerNow.configure(text='服务器状态：已启动')
    obj = subprocess.Popen("Library\index.bat > console.txt", stdin=subprocess.PIPE, 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    show = threading.Thread(target=showinfo)
    show.setName('ShowBDSConsole')
    show.start()
    c = threading.Thread(target=checkBDS)
    c.setName('CheckBDS')
    c.start()
    for i in config['Group']:
        sendGroupMsg(i,Language['Starting'])

def runfileserver():
    global obj
    scr.delete(1.0,'end')
    obj = os.system("start Library\index.bat")
    runserverb.configure(state='disabled')
    runserverc.configure(state='disabled')
    stoper.configure(state='normal')
    ServerNow.configure(text='服务器状态：已启动')
    c = threading.Thread(target=checkBDS)
    c.setName('CheckBDS')
    c.start()


#BDS控制台日志输出  
scrolW  = 75; scrolH  =  21
scr = scrolledtext.ScrolledText(monty, width=scrolW, height=scrolH, wrap=tk.WORD)
scr.grid(column=0, row=0,columnspan=3)
#scr.configure(state='disabled')

#命令输入
ttk.Label(monty, text="键入命令：").grid(column=0, row=2, sticky='W')
name = tk.StringVar()
nameEntered = ttk.Entry(monty, width=70, textvariable=name)
nameEntered.grid(column=0, row=2, sticky='W')
nameEntered.configure(state='disabled')

#执行命令
action = ttk.Button(monty,text="执行",width=5,command=runcmd)   
action.grid(column=1,row=2,rowspan=2)
action.configure(state='disabled')


createToolTip(action,'执行BDS命令')

#createToolTip(bookChosen, '这是一个Combobox.')
createToolTip(scr,'BDS日志输出')
createToolTip(nameEntered,'键入命令')

infos = ttk.LabelFrame(tab1, text='信息展示',width=500,height=100)
infos.grid(column=1, row=0, padx=1, pady=10,)

#QQ信息
QQInfo = ttk.LabelFrame(infos, text='机器人信息')
QQid = ttk.Label(QQInfo, text="账号：",width=20)
QQid.grid(column=0, row=0,sticky='W')
use = ttk.Label(QQInfo, text="授权状态：",width=20)
use.grid(column=0, row=1,sticky='W')
version = ttk.Label(QQInfo, text="Bot版本："+str(BotVersion),width=20).grid(column=0, row=2,sticky='W')
QQInfo.grid(column=0, row=0, padx=5, pady=10,sticky='W')
QQid.configure(text='账号：%i' % (config['Bot']))
try:
    j = json.loads(requests.get('http://www.txssb.cn/phsebot').text)
    if str(config['Bot']) in j:
        Used = True
        use.configure(text='授权状态：已授权')
    else:
        use.configure(text='授权状态：未授权')
except:
    use.configure(text='授权状态：未授权')
ttk.Label(infos, text="",width=20).grid(column=0, row=2)

#服务器信息
Serverinfos = ttk.LabelFrame(infos, text='服务器信息')
ServerNow = ttk.Label(Serverinfos, text="服务器状态：未启动",width=20)
ServerNow.grid(column=0, row=3)
ttk.Label(Serverinfos, text="=====================",width=20).grid(column=0, row=4)
GameVersion = ttk.Label(Serverinfos, text="服务器版本：",width=20)
GameVersion.grid(column=0, row=5)
GameFile = ttk.Label(Serverinfos, text="服务器存档：",width=20)
GameFile.grid(column=0, row=6)
Serverinfos.grid(column=0, row=1, padx=5, pady=10,sticky='W')

ttk.Label(infos, text="",width=20).grid(column=0, row=6)

#服务器操作
ServerUse = ttk.LabelFrame(infos, text='服务器操作',width=500,height=100)
runserverb = ttk.Button(ServerUse,text=">",width=2,command=runserver)   
runserverb.grid(column=0,row=5)
ttk.Label(ServerUse, text="从配置启动",width=17).grid(column=1, row=5)

runserverc = ttk.Button(ServerUse,text=">",width=2,command=runfileserver)   
runserverc.grid(column=0,row=6)
ttk.Label(ServerUse, text="从文件启动",width=17).grid(column=1, row=6)

stoper = ttk.Button(ServerUse,text=">",width=2,command=stoperd)   
stoper.grid(column=0,row=7)
ttk.Label(ServerUse, text="强制停止",width=17,foreground='red').grid(column=1, row=7)
stoper.configure(state='disabled')

#重载所有文件
def filereload():
    global config,Language,cron
    config = read_file('data/config.yml')
    Language = read_file('data/Language.yml')
    cron = read_file('data/Cron.json')
    conn = sq.connect('data/regular.db')
    c = conn.cursor()
    cursor = c.execute("SELECT *  from interactive")
    cmd = ''
    mlc.delete(END)
    mlb.delete(END)
    for row in cursor:
        r = row[0]
        by = row[1]
        perm = row[2]
        cmd = row[3]
        mlb.insert(END,(r,cmd,perm,by))
    conn.close()
    with open('data/Cron.json','r',encoding='utf-8') as f:
        cronl = json.loads(f.read())
    for i in cronl:
        mlc.insert(END,(i['cron'],i['cmd']))
    crontab()
    mBox.showinfo('重载文件','重载文件完成\nCrontab计划任务重新计时')
    print('[INFO] 内置计划任务已重新计时')

reload = ttk.Button(ServerUse,text=">",width=2,command=filereload)   
reload.grid(column=0,row=8)
ttk.Label(ServerUse, text="重载文件",width=17).grid(column=1, row=8)

ServerUse.grid(column=0, row=2, padx=5, pady=10,sticky='W')




# 一次性控制各控件之间的距离
for child in infos.winfo_children(): 
    child.grid_configure(padx=3,pady=1)
'''# 单独控制个别控件之间的距离
action.grid(column=2,row=1,rowspan=2,padx=6)'''
#---------------Tab1控件介绍------------------#
 
 
#---------------Tab2控件介绍------------------#
# We are creating a container tab3 to hold all other widgets -- Tab2
monty2 = ttk.LabelFrame(tab2, text='正则表达式预览 (请使用滚动条拉取页面避免出现错位的情况)')
monty2.grid(column=0, row=0, padx=8, pady=4)

mlb = MultiListbox(monty2,(('正则', 57),('执行', 20),("权限", 10),("捕获",10)))
conn = sq.connect('data/regular.db')
c = conn.cursor()
cursor = c.execute("SELECT *  from interactive")
cmd = ''
for row in cursor:
    r = row[0]
    by = row[1]
    perm = row[2]
    cmd = row[3]
    mlb.insert(END,(r,cmd,perm,by))
conn.close()

mlb.pack(expand=YES, fill=BOTH)

#---------------Tab2控件介绍------------------#
 

#---------------Tab3控件介绍------------------#
monty3 = ttk.LabelFrame(tab3, text='Cron预览 (请使用滚动条拉取页面避免出现错位的情况)')
monty3.grid(column=0, row=0, padx=8, pady=4)
mlc = MultiListbox(monty3,(('Crontab表达式', 50),('执行任务', 47)))
with open('data/Cron.json','r',encoding='utf-8') as f:
    cronl = json.loads(f.read())
for i in cronl:
    mlc.insert(END,(i['cron'],i['cmd']))
mlc.pack(expand=YES, fill=BOTH)
#---------------Tab3控件介绍------------------#
 
 
#----------------菜单栏介绍-------------------#    
# Exit GUI cleanly
def _quit():
    win.quit()
    win.destroy()
    exit()
    
# Creating a Menu Bar
menuBar = Menu(win)
win.config(menu=menuBar)
 
# Add menu items
def configw():
    pw = PopupDialog(win)
    win.wait_window(pw)

fileMenu = Menu(menuBar, tearoff=0)
fileMenu.add_command(label="配置",command=configw)
fileMenu.add_separator()
fileMenu.add_command(label="退出", command=_quit)
menuBar.add_cascade(label="显示", menu=fileMenu)
 
#----------------菜单栏介绍-------------------#
 
 
# Change the main windows icon
win.iconbitmap(r'Library/Images/bot.ico')
win.geometry('725x380')
# Place cursor into name Entry
#nameEntered.focus()      
#======================
# Start GUI
#======================
print('[INFO] Phsebot启动成功 作者：HuoHuaX')
print('[INFO] 特别鸣谢：McPlus Yanhy2000')
loginQQ()

def writeconfig():
    run = '''@echo off
cd %s
%s'''
    with open('Library\index.bat','w') as f:
        f.write(run % (config['ServerPath'],config['ServerFile']))

    with open('Temp/data.json','w') as f:
        f.write("""{
    "Version":"",
    "Port":0,
    "World":""
}
        """)
writeconfig()

def usegroupregular():
    global sessionKey
    url = config['BotWSURL']
    key = config['Key']
    url2 = config["BotURL"]
    ws = create_connection(url+'/message?verifyKey=%s&qq=%i' % (key,config['Bot']))
    while True:
        time.sleep(0.005)
        rt = {}
        regular = {'Console':[],'Group':[],'Msg':[]}
        conn = sq.connect('data/regular.db')
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
            if by == '群消息':
                regular['Group'].append({'regular':r,'perm':perm,'run':cmd})
        conn.close()
        j = json.loads(ws.recv())
        if 'type' in j['data']:
            if j['data']['type'] == "GroupMessage":
                group = j['data']["sender"]['group']['id']
                senderqq = j['data']['sender']["id"]
                sendername = j['data']['sender']["memberName"]
                Sourceid = 0
                msg = ''
                if len(j['data']["messageChain"]) == 1:
                    for i in j['data']["messageChain"]:
                        if i['type'] == 'Plain':
                            msg = i["text"]
                        elif i['type'] == 'Source':
                            Sourceid = i['id']
                else:
                    msg = ''
                    for i in j['data']["messageChain"]:
                        if i['type'] == 'Plain':
                            msg += i["text"]
                        elif i['type'] == 'At':
                            msg += str(i['target'])
                        elif i['type'] == 'Source':
                            Sourceid = i['id']
                #验证是否是管理的群
                if group in config['Group']:
                    #验证正则
                    for b in regular['Group']:
                        p = re.findall(b['regular'],msg)
                        if p != []:
                            if type(p[0]) == tuple:
                                if len(p[0]) == 1:
                                    cmd = b['run'].replace('$1',p[0][0])
                                elif len(p[0]) == 2:
                                    cmd = b['run'].replace('$1',p[0][0]).replace('$2',p[0][1])
                                elif len(p[0]) == 3:
                                    cmd = b['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2])
                                elif len(p[0]) == 4:
                                    cmd = b['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2]).replace('$4',p[0][3])
                                elif len(p[0]) == 5:
                                    cmd = b['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2]).replace('$4',p[0][3]).replace('$5',p[0][4])
                                elif len(p[0]) == 6:
                                    cmd = b['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2]).replace('$4',p[0][3]).replace('$5',p[0][4]).replace('$6',p[0][5])
                                elif len(p[0]) == 7:
                                    cmd = b['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2]).replace('$4',p[0][3]).replace('$5',p[0][4]).replace('$6',p[0][5]).replace('$7',p[0][6])
                                elif len(p[0]) == 8:
                                    cmd = b['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2]).replace('$4',p[0][3]).replace('$5',p[0][4]).replace('$6',p[0][5]).replace('$7',p[0][6]).replace('$8',p[0][7])
                                elif len(p[0]) == 9:
                                    cmd = b['run'].replace('$1',p[0][0]).replace('$2',p[0][1]).replace('$3',p[0][2]).replace('$4',p[0][3]).replace('$5',p[0][4]).replace('$6',p[0][5]).replace('$7',p[0][6]).replace('$8',p[0][7]).replace('$9',p[0][8])
                            elif type(p[0]) == str:
                                cmd = b['run'].replace('$1',p[0])
                            #发群消息
                            rps = replacegroup(cmd[2:],sendername,senderqq)
                            if b['perm'] == True:
                                if senderqq in config['Admin']:
                                    if b['run'][:2] == '>>':
                                        for g in config["Group"]:
                                            sendGroupMsg(g,rps)
                                    #执行命令
                                    elif b['run'][:2] == '<<':
                                        if 'motd' in cmd[2:]:
                                            Botruncmd(rps+' '+str(group))
                                        elif 'bindid' in cmd[2:]:
                                            Botruncmd(rps+' '+str(group))
                                        elif 'unbind' in cmd[2:]:
                                            Botruncmd(rps+' '+str(group))
                                        else:
                                            Botruncmd(rps)
                                else:
                                    sendGroupMsg(group,Language['NoPermission'])

                            else:
                                if b['run'][:2] == '>>':
                                    for g in config["Group"]:
                                        sendGroupMsg(g,rps)
                                #执行命令
                                elif b['run'][:2] == '<<':
                                    if 'motd' in cmd[2:]:
                                        Botruncmd(rps+' '+str(group))
                                    elif 'bind' in cmd[2:]:
                                        Botruncmd(rps+' '+str(group))
                                    elif 'unbind' in cmd[2:]:
                                        Botruncmd(rps+' '+str(group))
                                    else:
                                        Botruncmd(rps)
                        else:
                            rt = {'Type':'None'}
                    
                    #绑定xboxid
                    if config['AtNoXboxid']['Enable']:
                        qlist = []
                        conn = sq.connect('data/xuid.db')
                        c = conn.cursor()
                        cursor = c.execute("SELECT *  from xboxid")
                        for row in cursor:
                            qq = row[0]
                            qlist.append(qq)
                        conn.close()
                        if senderqq not in qlist:
                            #撤回消息
                            if config['AtNoXboxid']['Recall']:
                                recallmsg(Sourceid)
                            send_at(group,senderqq)
def useconsoleregular(text):
    rt = {}
    regular = {'Console':[],'Group':[],'Msg':[]}
    conn = sq.connect('data/regular.db')
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
            rps = replaceconsole(cmd[2:])
            if i['run'][:2] == '>>':
                for g in config["Group"]:
                    sendGroupMsg(g,rps)
                rt = {'Type':'Sended'}
            #执行命令
            elif i['run'][:2] == '<<':
                rt = {'Type':'Cmd','Cmd':rps}
        else:
            rt = {'Type':'None'}
    return rt

#解析cron
def crontab():
    croncomment = []
    cronl = cron
    str_time_now=datetime.now()
    for i in cronl:
        try:
            iter=croniter(i['cron'],str_time_now)
            time = iter.get_next(datetime).strftime("%Y-%m-%d-%H-%M-%S")
            cmd = i['cmd']
            croncomment.append({'time':time,'cmd':cmd,'cron':i['cron']})
        except CroniterNotAlphaError:
            print('[ERRO]',i['cron'],'无法被解析')
        except CroniterBadCronError:
            print('[ERRO]',i['cron'],'无法被解析')
    write_file('Temp/crontab.json',croncomment)
    print('[INFO] 内置计划任务已开始运行')

#运行计划任务
def runcron():
    while True:
        time.sleep(0.05)
        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        nowlist = now.split('-')
        timelist = []
        for i in nowlist:
            timelist.append(int(i))
        try:
            with open('Temp/crontab.json','r',encoding='utf-8') as f:
                croncmd = json.loads(f.read())
        except JSONDecodeError:
            croncmd = []

        for i in croncmd:
            crontime = []
            for t in i['time'].split('-'):
                crontime.append(int(t))
            #触发条件
            if timelist[0] >= crontime[0] and timelist[1] >= crontime[1] and \
                timelist[2] >= crontime[2] and timelist[3] >= crontime[3] and\
                    timelist[4] >= crontime[4] and timelist[5] >= crontime[5]:
                rps = replaceconsole(i['cmd'][2:])
                #群消息
                if i['cmd'][:2] == '>>':
                    for g in config['Group']:
                        sendGroupMsg(g,rps)
                #控制台
                elif i['cmd'][:2] == '<<':
                    Botruncmd(rps)
                #运行程序
                elif i['cmd'][:2] == '^^':
                    os.system('start '+cmd[2:])

                #执行完毕重新解析
                str_time_now=datetime.now()
                iter=croniter(i['cron'],str_time_now)
                times = iter.get_next(datetime).strftime("%Y-%m-%d-%H-%M-%S")
                cmd = i['cmd']
                croncmd.remove(i)
                croncmd.append({'time':times,'cmd':cmd,'cron':i['cron']})
                write_file('Temp/crontab.json',croncmd)
        
#生成计划任务
crontab()
if config['EnableCron']:
    croncmdt = threading.Thread(target=runcron)
    croncmdt.setName('Cron_Timer')
    croncmdt.start()

if config['EnableGroup']:
    gmsp = threading.Thread(target=usegroupregular)
    gmsp.setName('RecvGroupMsg')
    gmsp.start()

def on_closing():
    if mBox.askyesno('退出','您即将关闭Phsebot，确认吗？'):
        print('[INFO] 正在执行Exit事件')
        win.destroy()
        print('[INFO] 正在释放Mirai资源，请稍后')
        releaseSession()
        os._exit(0)

win.protocol("WM_DELETE_WINDOW", on_closing)
testupdate()
try:
    win.mainloop()
except KeyboardInterrupt:
    on_closing()

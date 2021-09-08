#======================
# imports
#======================
import os
import re
import subprocess
import threading
import time
import tkinter as tk
from datetime import datetime
from json import JSONDecodeError
from tkinter import *
from tkinter import Menu, Spinbox
from tkinter import messagebox as mBox
from tkinter import scrolledtext, ttk
from tkinter.constants import END

from croniter import CroniterBadCronError, CroniterNotAlphaError, croniter
from Library.motd import *

from Library.Logger import log_error, log_info, log_warn, log_debug
from src import *


Used = False
NormalStop = False



# 弹窗
class Editregular(tk.Toplevel):
    def __init__(self, parent,content,tf):
        super().__init__()
        self.title('Phsebot - 编辑正则')
        self.content = content
        self.parent = parent # 显式地保留父窗口
        self.iconbitmap(r'Library/Images/bot.ico')
        self.geometry('400x205')
        self.tf = tf
        self.resizable(0,0)
        ms = ttk.LabelFrame(self, text='修改配置',width=9,height=10)
        ms.grid(column=0, row=0, padx=7, pady=4)
        
        # 第一行（两列）
        row1 = tk.Frame(ms)
        row1.pack(fill="x")
        tk.Label(row1, text=' 正则：', width=10).pack(side=tk.LEFT)
        self.path = tk.StringVar()
        self.path.set(content[0])
        path = tk.Entry(row1, textvariable=self.path, width=42)
        path.pack(side=tk.LEFT)
        
        # 第二行
        row2 = tk.Frame(ms)
        row2.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row2, text=' 执行：', width=10).pack(side=tk.LEFT)
        self.file = tk.StringVar()
        self.file.set(content[1])
        file = tk.Entry(row2, textvariable=self.file, width=42)
        file.pack(side=tk.LEFT)

        # 第三行
        row3 = tk.Frame(ms)
        row3.pack(fill="x")
        self.autostatus=tk.IntVar()
        self.auto = tk.Checkbutton(row3, text="需要管理员权限",variable=self.autostatus)
        if content[2] == '管理员':
            self.auto.select()
        self.auto.pack(side=tk.LEFT)

        # 第四行
        row4 = tk.Frame(ms)
        row4.pack(fill="x", ipadx=1, ipady=1)
        self.iv_default = tk.IntVar()
        self.rb_default_Label = tk.Label(row4, text='选择来源：')
        self.rb_default1 = tk.Radiobutton(row4, text='控制台', value=1, variable=self.iv_default)
        self.rb_default2 = tk.Radiobutton(row4, text='群消息', value=2, variable=self.iv_default)
        self.rb_default_Label.grid(row=2, column=0, sticky='E')
        self.rb_default1.grid(row=4, column=1, sticky='W')
        self.rb_default2.grid(row=4, column=2, sticky='W')
        if content[3] == '控制台':
            self.rb_default1.select()
        elif content[3] == '群消息':
            self.rb_default2.select()


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
        conn = sq.connect('data/regular.db')
        c = conn.cursor()
        #正则
        regular = self.path.get()
        #执行
        run = self.file.get()
        #权限
        if self.autostatus.get() == 1:
            admin = '管理员'
        else:
            admin = ''
        #捕获
        if self.iv_default.get() == 1:
            find = '控制台'
        else:
            find = '群消息'
        
        if self.tf:
            #修改原文
            c.execute(
                'UPDATE interactive set 正则="%s",捕获="%s",权限="%s",执行="%s" where rowid=%i'
                % (regular,find,admin,run,self.content[4]+2)
            )
            conn.commit()
        else:
            #提交新的正则
            c.execute("INSERT INTO interactive (正则,捕获,权限,执行) \
            VALUES ('%s','%s','%s','%s')" % (regular,find,admin,run))
        conn.commit()
        conn.close()
        
        update()
        self.destroy() # 销毁窗口
        
    def cancel(self):
        self.destroy()

def edit_ragular(content):
    Editregular(win,content,True)

class MultiListbox(Frame):
    def __init__(self,master,lists):
        Frame.__init__(self,master)
        self.lists = []
        for l, w in lists:
            frame = Frame(self)
            frame.pack(side=LEFT, expand=YES, fill=BOTH)
            Label(frame, text=l, borderwidth=1, relief=RAISED).pack(fill=X)
            lb = Listbox(frame, width=w, borderwidth=0, selectborderwidth=0, relief=FLAT, exportselection=FALSE,height=16)
            lb.pack(expand=YES, fill=BOTH)
            self.lists.append(lb)
            lb.bind("<B1-Motion>",lambda e, s=self: s._select(e.y))
            lb.bind("<Button-1>",lambda e,s=self: s._selects(e.y))
            lb.bind("<Double-Button-1>",lambda e,s=self: s._select(e.y))
            lb.bind("<Leave>",lambda e: "break")
            lb.bind("<MouseWheel>",lambda e,s=self: s._b2motion(e.x,e.y))
            lb.bind("<Button-2>",lambda e,s=self: s._button2(e.x,e.y))
        frame = Frame(self)
        frame.pack(side=LEFT, fill=Y)
        Label(frame, borderwidth=1, relief=RAISED).pack(fill=X)
        sb = Scrollbar(frame,orient=VERTICAL, command=self._scroll)
        sb.pack(side=LEFT, fill=Y)
        self.lists[0]["yscrollcommand"] = sb.set

    def _selects(self, y):
        global csd
        row = self.lists[0].nearest(y)
        a = self.selection_clear(0, END)
        se = self.selection_set(row)
        csd = []
        for i in self.lists:
            content = i.get(row)
            csd.append(content)
        return "break"

    def _select(self, y):
        row = self.lists[0].nearest(y)
        a = self.selection_clear(0, END)
        se = self.selection_set(row)
        c = []
        for i in self.lists:
            content = i.get(row)
            c.append(content)
        c.append(row)
        if len(c) == 5:
            edit_ragular(c)
        return "break"

    def _button2(self, x, y):
        for l in self.lists:
            l.scan_mark(x,y)
        return "break"

    def _b2motion(self, x, y):
        for l in self.lists:
            l.scan_dragto(0, y)
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
        except TypeError as e:
            log_debug(e)
 
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
 
def build_window():
    global win,monty,tab1,tab2,tab3
    win = tk.Tk()   
    win.title("Phsebot")
    win.resizable(0,0)
    tabControl = ttk.Notebook(win)          
    tab1 = ttk.Frame(tabControl)           
    tabControl.add(tab1, text='BDS控制台')      
    tab2 = ttk.Frame(tabControl)            
    tabControl.add(tab2, text='正则表达式')      
    tab3 = ttk.Frame(tabControl)            
    tabControl.add(tab3, text='Cron表达式')      
    tabControl.pack(expand=1, fill="both")

    monty = ttk.LabelFrame(tab1, text='BDS控制台',width=500,height=100)
    monty.grid(column=0, row=0, padx=1, pady=10,)
    win.iconbitmap(r'Library/Images/bot.ico')
    win.geometry('725x400')
 
def runcmd():
    try:
        global NormalStop
        result=nameEntered.get()+'\r\n'
        cmd = result.encode('utf-8')
        if result.encode('utf-8') == b'stop\r\n':
            NormalStop = True
        obj.stdin.write(result.encode('utf-8'))
        obj.stdin.flush()
        nameEntered.delete(0, 'end')
    except Exception as e:
        log_debug(e)

def motdServer(ip,port,group):
    motd = Server(ip,int(port))
    jmotd = motd.motd()
    if jmotd['status'] == 'online':
        if Language['MotdSuccessful'] != False:
            sendmsg = Language['MotdSuccessful'].replace(r'%ip%',jmotd['ip']).replace(r'%port%',str(jmotd['port'])).replace(r'%motd%',jmotd['name'])\
            .replace(r'%agreement%',jmotd['protocol']).replace(r'%version%',jmotd['version']).replace(r'%delay%',str(jmotd['delay'])+'ms')\
                .replace(r'%online%',jmotd['online']).replace(r'%max%',jmotd['upperLimit']).replace(r'%gamemode%',jmotd['gamemode'])

            sendGroupMsg(ws,group,sendmsg.replace('\\n','\n'))
    else:
        if Language['MotdFaild'] != False:
            sendGroupMsg(ws,group,Language['MotdFaild'])

def Botruncmd(text):
    global NormalStop
    result=text+'\r\n'
    cmd = result
    #开服
    if text == 'start':
        if not check(obj):
            runserver()
        else:
            if Language['ServerRunning'] != False:
                for i in config['Group']:
                    sendGroupMsg(ws,i,Language['ServerRunning'])
                
    #正常关服
    elif text == 'stop':
        NormalStop = True
        if check(obj):
            obj.stdin.write(cmd.encode('utf8'))
            obj.stdin.flush()
        else:
            if Language['ServerNotRunning'] != False:
                for i in config['Group']:
                    sendGroupMsg(ws,i,Language['ServerNotRunning'])

    #绑定XboxID
    elif 'bindid' in text:
        if '"' not in text:
            args = text.split(' ')
            qqid = int(args[1])
            group = int(args[-1])
            name = args[2]
            bind(qqid,name,group)
        else:
            args = text.split(' ')
            qqid = int(args[1])
            group = int(args[-1])
            name = re.search(r'\"(.*)\"',text)[0].replace('"','')
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
        if check(obj):
            obj.stdin.write(cmd.encode('utf8'))
            obj.stdin.flush()
        else:
            if Language['ServerNotRunning']:
                for i in config['Group']:
                    sendGroupMsg(ws,i,Language['ServerNotRunning'])

Restart = 0
def checkBDS():
    global StartedServer,Restart
    while True:
        time.sleep(1)
        if not check(obj) and NormalStop == True:
            runserverb.configure(state='normal')
            runserverc.configure(state='normal')
            stoper.configure(state='disabled')
            scr.insert('end','[INFO] 进程已停止')
            ServerNow.configure(text='服务器状态：未启动')
            GameFile.configure(text='服务器存档：')
            GameVersion.configure(text='服务器版本：')
            action.configure(state='disabled')
            nameEntered.configure(state='disabled')
            break

        elif not check(obj) and NormalStop == False and config['AutoRestart']:
            if Language['AbendServer'] != False:
                for i in config['Group']:
                    sendGroupMsg(ws,i,Language['AbendServer'])
            if Language['RestartServer'] != False:
                for i in config['Group']:
                    sendGroupMsg(ws,i,Language['RestartServer'])
            ServerNow.configure(text='服务器状态：未启动')
            GameFile.configure(text='服务器存档：')
            GameVersion.configure(text='服务器版本：')
            if config['MaxAutoRestart'] > Restart:
                runserver()
                Restart += 1
            else:
                for i in config['Group']:
                    sendGroupMsg(ws,i,Language['MaxRestart'])
                Restart = 0
            break

        elif not check(obj) and NormalStop == False and config['AutoRestart'] == False:
            if Language['AbendServer'] != False:
                for i in config['Group']:
                    sendGroupMsg(ws,i,Language['AbendServer'])
            runserverb.configure(state='normal')
            runserverc.configure(state='normal')
            stoper.configure(state='disabled')
            scr.insert('end','[INFO] 进程已停止')
            ServerNow.configure(text='服务器状态：未启动')
            GameFile.configure(text='服务器存档：')
            GameVersion.configure(text='服务器版本：')
            action.configure(state='disabled')
            nameEntered.configure(state='disabled')
            break

def showinfo():
    global Version,Sended,World,Port
    for line in iter(obj.stdout.readline, b''):
        try:
            line = line.decode('utf8')
        except UnicodeDecodeError:
            line = line.decode('gbk')
        #删除颜色代码
        colorre = r'\[(.+?)m'
        linec = re.findall(colorre,line)
        for i in linec:
            line = line.replace('\033['+i+'m','')

        #自定义屏蔽输出
        if config['NoOut']:
            #字符串
            if NoOut['AllLine'] != None:
                for i in NoOut['AllLine']:
                    if i in line:
                        line = ''
            
            #替换
            if NoOut['ReplaceLine'] != None:
                for i in NoOut['ReplaceLine']:
                    line = line.replace(i,'')

            #正则
            if NoOut['Regular'] != None:
                for i in NoOut['Regular']:
                    if re.search(i,line) != None:
                        line = ''

        if line != '':
            scr.insert('end',line)
            scr.see(END)


        #使用控制台正则
        try:
            updateLine = line
            back = useconsoleregular(updateLine)
            #玩家退服
            if re.findall(r'^\[INFO\]\sPlayer\sdisconnected:\s(.+?),\sxuid:\s(.+?)$',updateLine) != []:
                r = re.findall(r'^\[INFO\]\sPlayer\sdisconnected:\s(.+?),\sxuid:\s(.+?)$',updateLine)
                if Language['PlayerLeft'] != False:
                    for g in config["Group"]:
                        sendGroupMsg(ws,g,Language['PlayerLeft'].replace('%player%',r[0][0]).replace(r'%xuid%',r[0][1]))

            #玩家进服
            if re.findall(r'^\[INFO\]\sPlayer\sconnected:\s(.+?),\sxuid:\s(.+?)$',updateLine) != []:
                r = re.findall(r'^\[INFO\]\sPlayer\sconnected:\s(.+?),\sxuid:\s(.+?)$',updateLine)
                if Language['PlayerJoin'] != False:
                    for g in config["Group"]:
                        sendGroupMsg(ws,g,Language['PlayerJoin'].replace('%player%',r[0][0]).replace(r'%xuid%',r[0][1]))

            if back['Type'] == 'Cmd':
                Botruncmd(back['Cmd'])
        except Exception as e:
            log_debug(e)
            

        #内置正则
            #版本
        if 'INFO] Version' in line:
            Version = re.findall(r'Version\s(.+?)[\r\s]',line)[0]
            GameVersion.configure(text='服务器版本：'+Version)
            if Language['ServerVersion'] != False:
                for b in config["Group"]:
                    sendGroupMsg(ws,b,Language['ServerVersion'].replace('%Version%',Version))
            #打开世界
        if 'opening' in line:
            World = re.findall(r'opening\s(.+?)[\r\s]',line)[0]
            GameFile.configure(text='服务器存档：'+World)
            if Language['OpenWorld'] != False:
                for b in config["Group"]:
                    sendGroupMsg(ws,b,Language['OpenWorld'].replace('%World%',World))
            #加载端口
        if 'IPv4' in line:
            Port = int(re.findall(r'^\[INFO\]\sIPv4\ssupported,\sport:\s(.+?)$',line)[0])
            try:
                with open('Temp\\data','w') as f:
                    f.write(str(Port))
            except Exception as e:
                log_debug(e)
            if Language['PortOpen'] != False:
                for b in config["Group"]:
                    sendGroupMsg(ws,b,Language['PortOpen'].replace('%Port%',str(Port)))

            #开服完成
        if 'Server started' in line:
            if Language['ServerStart'] != False:
                for b in config["Group"]:
                    sendGroupMsg(ws,b,Language['ServerStart'])

            #关服中
        if '[INFO] Server stop requested.' in line:
            if Language['ServerStopping'] != False:
                for b in config["Group"]:
                    sendGroupMsg(ws,b,Language['ServerStopping'])

            #关服完成
        if 'Quit correctly' in line:
            if Language['ServerStoped'] != False:
                for b in config["Group"]:
                    sendGroupMsg(ws,b,Language['ServerStoped'])

            #崩溃
        if 'Crashed' in line:
            if Language['Crashed'] != False:
                for b in config["Group"]:
                    sendGroupMsg(ws,b,Language['Crashed'])


    obj.stdout.close()
    obj.wait()

def stoperd():
    global NormalStop
    answer = mBox.askyesno("强制停止服务器", "你确定吗？") 
    if answer == True:
        NormalStop = True
        subprocess.Popen("cmd.exe /k taskkill /F /T /PID %i" % obj.pid , shell=True)  
        if Language['ForcedStop'] != False:
            for i in config['Group']:
                sendGroupMsg(ws,i,Language['ForcedStop'])
        action.configure(state='disabled')
        nameEntered.configure(state='disabled')
        
def runserver():
    global obj,Sended,NormalStop
    NormalStop = False
    Sended = []
    nameEntered.configure(state='normal')
    action.configure(state='normal')
    scr.delete(1.0,'end')
    runserverb.configure(state='disabled')
    runserverc.configure(state='disabled')
    stoper.configure(state='normal')
    ServerNow.configure(text='服务器状态：已启动')

    #旧版控制台
    '''obj = subprocess.Popen("Library\index.bat > Temp/console.txt", stdin=subprocess.PIPE, 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    show = threading.Thread(target=showinfo)
    show.setName('ShowBDSConsole')
    show.start()'''

    #新版控制台
    obj = subprocess.Popen('Library\index.bat', stdout=subprocess.PIPE, stdin=-1,bufsize=1,shell=True)
    show = threading.Thread(target=showinfo)
    show.setName('ShowBDSConsole')
    show.start()

    c = threading.Thread(target=checkBDS)
    c.setName('CheckBDS')
    c.start()
    if Language['Starting'] != False:
        for i in config['Group']:
            sendGroupMsg(ws,i,Language['Starting'])

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

def create_content():
    global runserverb,runserverc,stoper,ServerNow,scr,nameEntered,action,GameFile,GameVersion,ServerUse,infos,mlb,mlc
    #BDS控制台日志输出 
    scrolW  = 75; scrolH  =  21
    scr = scrolledtext.ScrolledText(monty, width=scrolW, height=scrolH, wrap=tk.WORD)
    scr.grid(column=0, row=0,columnspan=3)

    #命令输入
    ttk.Label(monty, text="键入命令：").grid(column=0, row=2, sticky='W')
    name = tk.StringVar()
    nameEntered = ttk.Entry(monty, width=70, textvariable=name)
    nameEntered.grid(column=0, row=2, sticky='W')
    

    #执行命令
    action = ttk.Button(monty,text="执行",width=5,command=runcmd)   
    action.grid(column=1,row=2,rowspan=2)
    action.configure(state='disabled')
    nameEntered.configure(state='disabled')

    createToolTip(action,'执行BDS命令')

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
    except Exception as e:
        log_debug(e)
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

    reload = ttk.Button(ServerUse,text=">",width=2,command=filereload)   
    reload.grid(column=0,row=8)
    ttk.Label(ServerUse, text="重载文件",width=17).grid(column=1, row=8)

    ServerUse.grid(column=0, row=2, padx=5, pady=10,sticky='W')
    # 一次性控制各控件之间的距离
    for child in infos.winfo_children(): 
        child.grid_configure(padx=3,pady=1)
    #---------------Tab1控件介绍------------------#
 
    lbv=tk.StringVar()#绑定变量
    #---------------Tab2控件介绍------------------#
    def new_regular():
        Editregular(win,['','','','控制台'],False)
    
    def delete_regular():
        global csd
        if csd != []:
            #删除正则
            if len(csd) == 4:
                conn = sq.connect('data/regular.db')
                c = conn.cursor()
                c.execute("DELETE from interactive where 正则='%s';" % csd[0])
                conn.commit()
                mBox.showinfo('删除成功','您已删除正则:\n%s' % csd[0])
                update()
                csd = []
        else:
            mBox.showwarning('警告','你没有选中正则')
    monty2 = ttk.LabelFrame(tab2, text='正则表达式 (请使用滚动条拉取页面避免出现错位的情况)')
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

    newregular = tk.Button(monty2,text='新建',width=10,command=new_regular)
    newregular.pack(side=LEFT)

    deleter = tk.Button(monty2,text='删除',width=10,command=delete_regular)
    deleter.pack(side=LEFT,padx=3)

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
    fileMenu.add_command(label="退出", command=on_closing)
    menuBar.add_cascade(label="显示", menu=fileMenu)
 
#----------------菜单栏介绍-------------------#

#更新预览
def update():
    global config,Language,cron
    conn = sq.connect('data/regular.db')
    c = conn.cursor()
    cursor = c.execute("SELECT *  from interactive")
    cmd = ''
    mlb.delete(0,END)
    for row in cursor:
        r = row[0]
        by = row[1]
        perm = row[2]
        cmd = row[3]
        mlb.insert(END,(r,cmd,perm,by))
    conn.close()



#重载所有文件
def filereload():
    global config,Language,cron,NoOut
    config = read_file('data/config.yml')
    Language = read_file('data/Language.yml')
    cron = read_file('data/Cron.json')
    conn = sq.connect('data/regular.db')
    NoOut = read_file('data/NoOut.yml')
    c = conn.cursor()
    cursor = c.execute("SELECT *  from interactive")
    cmd = ''
    mlc.delete(0,END)
    mlb.delete(0,END)
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
    log_info('内置计划任务已重新计时')


def writeconfig():
    run = '''@echo off
cd "%s"
%s'''
    with open('Library\index.bat','w') as f:
        f.write(run % (config['ServerPath'],config['ServerCmd']))

    with open('Temp\\data','w') as f:
        f.write("0")


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
        except CroniterNotAlphaError as e:
            log_debug(e)
            log_error(i['cron'],'无法被解析')
        except CroniterBadCronError as e:
            log_debug(e)
            log_error(i['cron'],'无法被解析')
    write_file('Temp/crontab.json',croncomment)
    log_info('内置计划任务已开始运行')

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
        except JSONDecodeError as e:
            log_debug(e)
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
                        sendGroupMsg(ws,g,rps)
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

def usegroupregular():
    global sessionKey,ws
    
    
    url2 = config["BotURL"]
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
        try:
            j = json.loads(ws.recv())
        except ConnectionResetError as e:
            log_debug(e)
            mBox.showerror('错误','Mirai已断开连接')
            break
        except Exception as e:
            log_debug(e)
            mBox.showerror('错误','出现了内部错误')
            break
        if 'data' in j and 'type' in j['data'] and j['syncId'] != '123':
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
                                            sendGroupMsg(ws,g,rps)
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
                                    if Language['NoPermission'] != False:
                                        sendGroupMsg(ws,group,Language['NoPermission'])

                            else:
                                if b['run'][:2] == '>>':
                                    for g in config["Group"]:
                                        sendGroupMsg(ws,g,rps)
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
                                recallmsg(ws,Sourceid)
                            send_at(ws,group,senderqq,Language['AtNotXboxid'])
            #检测改名
            elif j['data']['type'] == "MemberCardChangeEvent":
                qqid = j['data']['member']['id']
                group = j['data']['member']['group']['id']
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
                #检测是否是管理的群
                if group in config['Group']:
                    #检测是否绑定白名单
                    if qqid in qlist and qqid not in config['CheckNick']['WhiteList']:
                        for p in qxlist:
                            if p['qq'] == qqid:
                                if j['data']['current'] != p['id']:
                                    changeName(ws,qqid,group,p['id'])
                                    if Language['ChangeNick'] != False:
                                        send_at(ws,group,qqid,Language['ChangeNick'])

            #检测成员离开群聊
            elif 'MemberLeaveEventKick' == j['data']['type'] or "MemberLeaveEventQuit" == j['data']['type']:
                memberid = j['data']['member']['id']
                group = j['data']['member']['group']['id']
                #验证管理群号
                if group in config['Group'] and config['LeftRemove']:
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
                    if memberid in qlist:
                        wl = read_file(config['ServerPath']+'\\whitelist.json')
                        wlrun = False
                        xboxid = r'%xboxid%'
                        for x in qxlist:
                            if x['qq'] == memberid:
                                xboxid = x['id']
                        for names in wl:
                            if names['name'] == xboxid:
                                wlrun = True
                        if wlrun:
                            if Language['LeftGroup'] != False:
                                sendGroupMsg(ws,group,Language['LeftGroup'].replace(r'%xboxid%',xboxid))
                            Botruncmd('whitelist remove "%s"' % xboxid)
        elif j['syncId'] == '123' and 'data' in j:
            try:
                ij = j['data']
                if ij['code'] == 0 and ij['messageId'] == -1:
                    log_warn('消息已发送，但可能遭到屏蔽')
                if ij['code'] == 10:
                    log_warn('已尝试修改群名片，但没有权限')
            except JSONDecodeError as e:
                log_debug(e)
                log_error('发送消息时出现了内部错误')

        elif j['syncId'] == '1234' and 'data' in j:
            try:
                ij = j['data']
                if ij['code'] == 10:
                    log_warn('已尝试修改群名片，但没有权限')
            except JSONDecodeError as e:
                log_debug(e)
                log_error('修改群名片时出现了内部错误')
        

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
                    sendGroupMsg(ws,g,rps)
                rt = {'Type':'Sended'}
            #执行命令
            elif i['run'][:2] == '<<':
                rt = {'Type':'Cmd','Cmd':rps}
        else:
            rt = {'Type':'None'}
    return rt

def on_closing():
    if mBox.askyesno('退出','您即将关闭Phsebot，确认吗？'):
        log_info('正在执行Exit事件')
        win.destroy()
        log_info('正在释放Mirai资源，请稍后')
        os._exit(0)
        
#生成计划任务
if __name__ == '__main__':
    os.system('title Phsebot-V'+str(BotVersion))
    log_info('启动时间:'+str(datetime.now()))
    #全局变量
    testupdate()
    build_window()
    create_content()
    if login():
        from src import ws
    else:
        mBox.showerror('连接Mirai失败','连接Mirai失败，请检查\n更多详情请查看控制台Debug日志信息')
        os._exit(0)
    log_info('Phsebot启动成功 作者：HuoHuaX')
    log_info('特别鸣谢：McPlus Yanhy2000')
    writeconfig()
    crontab()
    obj = subprocess.Popen('echo xxxx', stdout=subprocess.PIPE, stdin=-1,bufsize=1,shell=True)
    if config['EnableCron']:
        croncmdt = threading.Thread(target=runcron)
        croncmdt.setName('Cron_Timer')
        croncmdt.start()

    if config['EnableGroup']:
        gmsp = threading.Thread(target=usegroupregular)
        gmsp.setName('RecvGroupMsg')
        gmsp.start()

    win.protocol("WM_DELETE_WINDOW", on_closing)
    try:
        win.mainloop()
    except KeyboardInterrupt as e:
        log_debug(e)
        on_closing()


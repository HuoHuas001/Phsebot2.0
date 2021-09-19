import os
import re
import sys

#添加工作目录
sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('.')+'\\Library\\PLib')

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
import tkinter.font as tf

from Library.src import *
from Library.Tool import *
from Library.FakePlayer import *
from Library.window import *

class Window():
    def __init__(self) -> None:
        #创建窗口
        self.win = tk.Tk()   
        self.win.title("Phsebot")
        self.win.resizable(0,0)

        #翻页栏
        self.tabControl = ttk.Notebook(self.win)          
        self.tab1 = ttk.Frame(self.tabControl)           
        self.tabControl.add(self.tab1, text=PLP['MainUI.BDS'])      
        self.tab2 = ttk.Frame(self.tabControl)            
        self.tabControl.add(self.tab2, text=PLP['MainUI.regular'])      
        self.tab3 = ttk.Frame(self.tabControl)            
        self.tabControl.add(self.tab3, text=PLP['MainUI.cron']) 
        self.tab4 = ttk.Frame(self.tabControl)           
        self.tabControl.add(self.tab4, text=PLP['MainUI.Contrl'])          
        self.tabControl.pack(expand=1, fill="both")

        #窗口frame
        self.monty = ttk.LabelFrame(self.tab1, text=PLP['BDSUI.frame'],width=500,height=100)
        self.monty.grid(column=0, row=0, padx=1, pady=10,)
        #self.win.iconbitmap(r'Library/Images/Sbot.ico')
        self.win.iconphoto(True, tk.PhotoImage(file='Library/Images/window.png'))
        self.win.geometry('725x415')

        #加载窗口事件
        self.win.protocol("WM_DELETE_WINDOW", self.on_closing)

    #构建窗口内容
    def create_window_content(self):
        from Library.src import server
        scrolW  = 75; scrolH  =  23.1
        self.scrc = scrolledtext.ScrolledText(self.monty, width=scrolW, height=scrolH, wrap=tk.WORD)
        self.scrc.grid(column=0, row=0,columnspan=3)

        #命令输入
        ttk.Label(self.monty, text=PLP['BDSUI.InputCommand']).grid(column=0, row=2, sticky='W')
        name = tk.StringVar()
        self.nameEntered = ttk.Entry(self.monty, width=70, textvariable=name)
        self.nameEntered.grid(column=0, row=2, sticky='W')
        self.nameEntered.configure(state='disabled')

        #执行命令
        self.action = ttk.Button(self.monty,text=PLP['BDSUI.run'],width=5,command=server.Runcmd)   
        self.action.grid(column=1,row=2,rowspan=2)
        self.action.configure(state='disabled')

        #加入提示
        createToolTip(self.action,PLP['BDSUI.Runcommand'])
        createToolTip(self.scrc,PLP['BDSUI.log'])
        createToolTip(self.nameEntered,PLP['BDSUI.Input'])

        #信息栏
        infos = ttk.LabelFrame(self.tab1, text=PLP['BDSUI.ShowInfo.frame'])
        infos.grid(column=1, row=0, padx=1, pady=10,)

            #QQ信息
        self.QQInfo = ttk.LabelFrame(infos, text=PLP['BDSUI.ShowInfo.BotInfo'])
        self.QQid = ttk.Label(self.QQInfo, text=PLP['BDSUI.ShowInfo.account'],width=20)
        self.QQid.grid(column=0, row=0,sticky='W')

        version = ttk.Label(self.QQInfo, text=PLP['BDSUI.ShowInfo.Version']+str(BotVersion),width=20).grid(column=0, row=2,sticky='W')
        self.QQInfo.grid(column=0, row=0, padx=5, pady=10,sticky='W')
        self.QQid.configure(text='%s %i' % (PLP['BDSUI.ShowInfo.account'],config['Bot']))

            #服务器信息
        Serverinfos = ttk.LabelFrame(infos, text=PLP['BDSUI.ShowInfo.Server.frame'])
        self.ServerNow = ttk.Label(Serverinfos, text='%s %s' % (PLP['BDSUI.State'],PLP['Server.NoRunning']),width=20)
        self.ServerNow.grid(column=0, row=3)
        ttk.Label(Serverinfos, text="=====================",width=20).grid(column=0, row=4)
        self.GameVersion = ttk.Label(Serverinfos, text=PLP['BDSUI.Version'],width=20)
        self.GameVersion.grid(column=0, row=5)
        self.GameFile = ttk.Label(Serverinfos, text=PLP['BDSUI.World'],width=20)
        self.GameFile.grid(column=0, row=6)
        self.CpuC = ttk.Label(Serverinfos, text=PLP['MainUI.CPU']+' '+str(cpup)+'%',width=20)
        self.CpuC.grid(column=0, row=7)
        Serverinfos.grid(column=0, row=1, padx=5, pady=10,sticky='W')

            #服务器操作
        ServerUse = ttk.LabelFrame(infos, text=PLP['BDSUI.ShowInfo.Action.frame'],width=500,height=100)
        self.runserverb = ttk.Button(ServerUse,text=">",width=2,command=server.RunServer)   #
        self.runserverb.grid(column=0,row=5)
        ttk.Label(ServerUse, text=PLP['BDSUI.ShowInfo.Action.config'],width=17).grid(column=1, row=5)

        self.runserverc = ttk.Button(ServerUse,text=">",width=2)   #,command=runfileserver
        self.runserverc.grid(column=0,row=6)
        ttk.Label(ServerUse, text=PLP['BDSUI.ShowInfo.Action.file'],width=17).grid(column=1, row=6)

        self.stoper = ttk.Button(ServerUse,text=">",width=2)   #,command=stoperd
        self.stoper.grid(column=0,row=7)
        ttk.Label(ServerUse, text=PLP['BDSUI.ShowInfo.Action.stop'],width=17,foreground='red').grid(column=1, row=7)
        self.stoper.configure(state='disabled')

        reload = ttk.Button(ServerUse,text=">",width=2,command=filereload)   
        reload.grid(column=0,row=8)
        ttk.Label(ServerUse, text=PLP['BDSUI.ShowInfo.Action.reload'],width=17).grid(column=1, row=8)

        ServerUse.grid(column=0, row=2, padx=5, pady=10,sticky='W')
        # 一次性控制各控件之间的距离
        for child in infos.winfo_children(): 
            child.grid_configure(padx=3,pady=1)

        #---------------Tab2控件介绍------------------#
        def new_regular():
            from Library.window import Editregular
            Editregular(self.win,['','','','控制台'],False)
    
        def delete_regular():
            global csd
            from Library.Tool import csd
            if csd != []:
                #删除正则
                if len(csd) == 4:
                    conn = sq.connect('data/regular.db')
                    c = conn.cursor()
                    c.execute("DELETE from interactive where 正则='%s';" % csd[0])
                    conn.commit()
                    mBox.showinfo(PLP['RemoveRegular.Ask.title'],'%s\n%s' % (PLP['RemoveRegular.Ask.message'],csd[0]))
                    import Library.Tool as tool
                    tool.update()
                    csd = []
            else:
                mBox.showwarning(PLP['RemoveRegular.Warning.title'],PLP['RemoveRegular.Warning.message'])

        monty2 = ttk.LabelFrame(self.tab2, text=PLP['ShowRegular.frame'])
        monty2.grid(column=0, row=0, padx=8, pady=4)

        self.mlb = MultiListbox(monty2,((PLP['ShowRegular.List.regular'], 57),(PLP['ShowRegular.List.run'], 20),(PLP['ShowRegular.List.perm'], 10),(PLP['ShowRegular.List.catch'],10)))
        conn = sq.connect('data/regular.db')
        c = conn.cursor()
        cursor = c.execute("SELECT *  from interactive")
        cmd = ''
        for row in cursor:
            r = row[0]
            by = row[1]
            perm = row[2]
            cmd = row[3]
            self.mlb.insert(END,(r,cmd,perm,by))
        conn.close()
        self.mlb.pack(expand=YES, fill=BOTH)

        newregular = tk.Button(monty2,text=PLP['ShowRegular.new'],width=10,command=new_regular)
        newregular.pack(side=LEFT)

        deleter = tk.Button(monty2,text=PLP['ShowRegular.remove'],width=10,command=delete_regular)
        deleter.pack(side=LEFT,padx=3)
        #---------------Tab2控件介绍------------------#

        #---------------Tab3控件介绍------------------#
        monty3 = ttk.LabelFrame(self.tab3, text=PLP['ShowCron.frame'])
        monty3.grid(column=0, row=0, padx=8, pady=4)
        self.mlc = MultiListbox(monty3,((PLP['ShowCron.List.cron'], 50),(PLP['ShowCron.List.run'], 47)))
        with open('data/Cron.json','r',encoding='utf-8') as f:
            cronl = json.loads(f.read())
        for i in cronl:
            self.mlc.insert(END,(i['cron'],i['cmd']))
        self.mlc.pack(expand=YES, fill=BOTH)
        #---------------Tab3控件介绍------------------#

        #---------------Tab4控件介绍------------------#

        scolW  = 99; scolH  =  28
        self.sc = scrolledtext.ScrolledText(self.tab4, width=scolW, height=scolH, wrap=tk.WORD)
        self.sc.grid(column=0, row=0,columnspan=3)
        self.sc.configure(state='disabled')
        #---------------Tab4控件介绍------------------#

        #----------------菜单栏介绍-------------------#    
        # Creating a Menu Bar
        menuBar = Menu(self.win)
        self.win.config(menu=menuBar)
 
        # Add menu items
        def configw():
            pw = PopupDialog(self.win)
            self.win.wait_window(pw)

        fileMenu = Menu(menuBar, tearoff=0)
        fileMenu.add_command(label=PLP['Menu.config'],command=configw)
        fileMenu.add_separator()
        fileMenu.add_command(label=PLP['Menu.exit'], command=self.on_closing)
        menuBar.add_cascade(label=PLP['Menu.title'], menu=fileMenu)

    def on_closing(self):
        if mBox.askyesno(PLP['Exit.title'],PLP['Exit.message']):
            log_info(PLP['Exit.runExit'])
            from Library.Loader.Plugin import Events
            for e in Events['Exit']:
                try:
                    e()
                except Exception as e:
                    log_debug(e)
            log_info(PLP['Exit.release'])
            os._exit(0)

    def insertscrc(self,line):
        self.scrc.configure(state='normal')
        self.scrc.insert(END,line)

#Plugin类
class Plugin():
    def __init__(self) -> None:
        #检测头
        self.loader = False

    def checkcmd(self,cmd:str):
        #检查命令
        if self.loader:
            from Library.Loader.Plugin import cmds
            if cmd.split(' ')[0] in cmds:
                return True
            else:
                return False
        else:
            return False

    def pluginCmd(self,cmd:str,g,i,n):
        from Library.Loader.Plugin import cmds
        class Args():
            def __init__(self,group:int,sender:int,name:str,args = None) -> None:
                self.group = group
                self.senderId = sender
                self.senderName = name
                self.args = args

        if cmds[cmd.split(' ')[0]].type == 'ordinary':
            args = Args(g,i,n)
            cmds[cmd].function(args)
        elif cmds[cmd.split(' ')[0]].type == 'args':
            cmdarg = cmd.split(' ')
            log_debug(cmdarg)
            args = Args(g,i,n,cmdarg)

#BDS类
class BDSServer():
    def __init__(self) -> None:
        self.NormalStop = False
        self.Started = False
        self.Last = ''
        self.Restart = 0
        self.Players = {
            "Now":0,
            "Max":0,
            "Player":''
        }

    def RunServer(self) -> None:
        from Library.src import Sbot
        from Library.src import window_root
        self.NormalStop = False

        #窗口
        window_root.nameEntered.configure(state='normal')
        window_root.action.configure(state='normal')
        window_root.scrc.delete(1.0,'end')
        window_root.runserverb.configure(state='disabled')
        window_root.runserverc.configure(state='disabled')
        window_root.stoper.configure(state='normal')
        window_root.ServerNow.configure(text='%s %s' % (PLP['BDSUI.State'],PLP['Server.Running']))

        #新版控制台
        self.bds = subprocess.Popen('Temp\\run.bat', stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=-1,bufsize=1,shell=True)
        self.show = threading.Thread(target=self.insert_info)
        self.show.setName('ShowBDSConsole')
        self.show.start()

        self.check = threading.Thread(target=self.checkBDS)
        self.check.setName('CheckBDS')
        self.check.start()
        if Language['Starting'] != False:
            for i in config['Group']:
                sendGroupMsg(i,Language['Starting'])
        from Library.Loader.Plugin import Events
        for e in Events['StartingServer']:
            try:
                e()
            except Exception as e:
                log_debug(e)

    def insert_info(self):
        for line in iter(self.bds.stdout.readline, b''):
            self.insertscr(line)
            from Library.Loader.Plugin import Events
            for e in Events['ConsoleUpdate']:
                try:
                    e(line)
                except Exception as e:
                    log_debug(e)
        for li in iter(self.bds.stderr.readline, b''):
            self.insertscr(li)
            from Library.Loader.Plugin import Events
            for e in Events['ConsoleUpdate']:
                try:
                    e(li)
                except Exception as e:
                    log_debug(e)
        self.bds.stdout.close()
        self.bds.wait()

    def insertscr(self,line:bytes):
        from Library.src import window_root
        #解码
        try:
            line = line.decode('utf8')
        except UnicodeDecodeError:
            line = line.decode('gbk')
        #删除颜色代码
        colorre = r'\[(.+?)m'
        linec = re.findall(colorre,line)
        for i in linec:
            line = line.replace('\033['+i+'m','')

        #捕捉玩家列表
        pl = re.findall(r'^There\sare(.+?)\/(.+?)\sp',line)
        if pl != []:
            self.Players['Now'] = int(pl[0][0])
            self.Players['Max'] = int(pl[0][1])

        #存储上一个
        if re.search(r'^There\sare(.+?)\/(.+?)\sp',self.Last) != None:
            self.Players['Player'] = line.replace('\n','')
        
        self.Last = line

        #触发自动改名
        if config['AutoChangeBotName']['Enable'] and self.Started:
            ChangeBotName(self.Started)
    
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
            try:
                window_root.scrc.configure(state='normal')
                window_root.scrc.insert('end',line)
                window_root.scrc.see(END)
                if config['AutoRecordBDS']:
                    try:
                        with open('Temp/BDSConsole.txt','a',encoding='utf8') as f:
                            f.write(line[:-2]+'\n')
                    except FileNotFoundError:
                        with open('Temp/BDSConsole.txt','w',encoding='utf8') as f:
                            f.write(line[:-2]+'\n')
                window_root.scrc.configure(state='disabled')
                self.inlineregular(line)
            except RuntimeError:
                pass

    def inlineregular(self,line):
        from Library.src import window_root
        #使用控制台正则
        try:
            updateLine = line
            #back = useconsoleregular(updateLine)
            #玩家退服
            if re.findall(r'^\[INFO\]\sPlayer\sdisconnected:\s(.+?),\sxuid:\s(.+?)$',updateLine) != []:
                r = re.findall(r'^\[INFO\]\sPlayer\sdisconnected:\s(.+?),\sxuid:\s(.+?)$',updateLine)
                from Library.Loader.Plugin import Events
                for e in Events['PlayerExit']:
                    try:
                        e(r[0][0])
                    except Exception as e:
                        log_debug(e)
                if Language['PlayerLeft'] != False:
                    for g in config["Group"]:
                        sendGroupMsg(g,Language['PlayerLeft'].replace('%player%',r[0][0]).replace(r'%xuid%',r[0][1]))

            #玩家进服
            if re.findall(r'^\[INFO\]\sPlayer\sconnected:\s(.+?),\sxuid:\s(.+?)$',updateLine) != []:
                r = re.findall(r'^\[INFO\]\sPlayer\sconnected:\s(.+?),\sxuid:\s(.+?)$',updateLine)
                from Library.Loader.Plugin import Events
                for e in Events['PlayerJoin']:
                    try:
                        e(r[0][0])
                    except Exception as e:
                        log_debug(e)
                if Language['PlayerJoin'] != False:
                    for g in config["Group"]:
                        sendGroupMsg(g,Language['PlayerJoin'].replace('%player%',r[0][0]).replace(r'%xuid%',r[0][1]))

            '''if back['Type'] == 'Cmd':
                Botruncmd(back['Cmd'])'''
        except OSError as e:
            log_debug(e)
        

        #内置正则
            #版本
        if 'INFO] Version' in line:
            Version = re.findall(r'Version\s(.+?)[\r\s]',line)[0]
            window_root.GameVersion.configure(text=PLP['BDSUI.Version']+Version)
            from Library.Loader.Plugin import Events
            for e in Events['LoadVersion']:
                try:
                    e(Version)
                except Exception as e:
                    log_debug(e)
            if Language['ServerVersion'] != False:
                for b in config["Group"]:
                    sendGroupMsg(b,Language['ServerVersion'].replace('%Version%',Version))
            #打开世界
        if 'opening' in line:
            World = re.findall(r'opening\s(.+?)[\r\s]',line)[0]
            window_root.GameFile.configure(text=PLP['BDSUI.World']+World)
            from Library.Loader.Plugin import Events
            for e in Events['OpenWorld']:
                try:
                    e(World)
                except Exception as e:
                    log_debug(e)
            if Language['OpenWorld'] != False:
                for b in config["Group"]:
                    sendGroupMsg(b,Language['OpenWorld'].replace('%World%',World))
            #加载端口
        if 'IPv4' in line:
            Port = int(re.findall(r'^\[INFO\]\sIPv4\ssupported,\sport:\s(.+?)$',line)[0])
            from Library.Loader.Plugin import Events
            for e in Events['LoadPort']:
                try:
                    e(Port)
                except Exception as e:
                    log_debug(e)
            try:
                with open('Temp\\data','w') as f:
                    f.write(str(Port))
            except Exception as e:
                log_debug(e)
            if Language['PortOpen'] != False:
                for b in config["Group"]:
                    sendGroupMsg(b,Language['PortOpen'].replace('%Port%',str(Port)))

            #开服完成
        if 'Server started' in line:
            if Language['ServerStart'] != False:
                for b in config["Group"]:
                    sendGroupMsg(b,Language['ServerStart'])
            #触发假人服务
            ConnectAllPlayer()
            self.Started = True
            from Library.Loader.Plugin import Events
            for e in Events['ServerStarted']:
                try:
                    e()
                except Exception as e:
                    log_debug(e)

            #关服中
        if '[INFO] Server stop requested.' in line:
            if Language['ServerStopping'] != False:
                for b in config["Group"]:
                    sendGroupMsg(b,Language['ServerStopping'])
                ChangeBotName(self.Started)
            from Library.Loader.Plugin import Events
            for e in Events['StoppingServer']:
                try:
                    e()
                except Exception as e:
                    log_debug(e)
        

        #关服完成
        if 'Quit correctly' in line:
            if Language['ServerStoped'] != False:
                for b in config["Group"]:
                    sendGroupMsg(b,Language['ServerStoped'])
            from Library.Loader.Plugin import Events
            for e in Events['StoppedServer']:
                try:
                    e()
                except Exception as e:
                    log_debug(e)

            #崩溃
        if 'Crashed' in line:
            if Language['Crashed'] != False:
                for b in config["Group"]:
                    sendGroupMsg(b,Language['Crashed'])
            from Library.Loader.Plugin import Events
            for e in Events['Crash']:
                try:
                    e()
                except Exception as e:
                    log_debug(e)

    def getBDSPoll(self) -> bool:
        #获取bds是否运行中
        try:
            if self.bds.poll() == None:
                return True
            else:
                return False
        except:
            return False

    #输出list名单
    def outList(self):
        time.sleep(1)
        if Language['OnlineList'] != False:
            l = Language['OnlineList'].replace(r'%Online%',str(self.Players['Now'])).replace(r'%Max%',str(self.Players['Max'])).replace(r'%Player%',self.Players['Player'])
            for i in config['Group']:
                sendGroupMsg(i,l)

    def cardlist(self):
        time.sleep(1)
        if config['ServerInfoCard']['Enable']:
            card = config['ServerInfoCard']['CardJson']
            #改变
            card = card.replace('%Online%',str(self.Players['Now']))
            card = card.replace('%Max%',str(self.Players["Max"]))
            card = card.replace('%Players%',self.Players['Player'])
            #替换logo
            if config['ServerInfoCard']['Logo'] != '':
                card = card.replace(r'%Logo%','https:\/\/z3.ax1x.com\/2021\/09\/09\/hOPbZQ.png')
            else:
                card = card.replace(r'%Logo%',config['ServerInfoCard']['Logo'])
            for i in config['Group']:
                Sbot.send_app(i,card)
    
    def Runcmd(self,text=None):
        from Library.src import window_root
        #运行一个bds命令
        cmd = text
        if text == None:
            cmd = window_root.nameEntered.get()
            window_root.nameEntered.delete(0, 'end')
        
        if self.getBDSPoll():
            from Library.Loader.Plugin import Events
            for e in Events['RunCmd']:
                try:
                    e(cmd)
                except Exception as e:
                    log_debug(e)
            if '\r\n' not in cmd:
                cmd += '\r\n'
            self.bds.stdin.write(cmd.encode('utf8'))
            self.bds.stdin.flush()
            if cmd == 'stop':
                self.NormalStop = True
                self.Started = False
        else:
            if Language['ServerNotRunning']:
                for i in config['Group']:
                    sendGroupMsg(i,Language['ServerNotRunning'])

    def Botruncmd(self,text:str):
        global NormalStop,Started
        result=text+'\r\n'
        cmd = result

        #开服
        if text == 'start':
            if not self.getBDSPoll():
                self.RunServer
            else:
                if Language['ServerRunning'] != False:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['ServerRunning'])
                    
        #正常关服
        elif text == 'stop':
            NormalStop = True
            DisConnectAllPlayer()
            Started = False
            if self.getBDSPoll():
                self.bds.stdin.write(cmd.encode('utf8'))
                self.bds.stdin.flush()
            else:
                if Language['ServerNotRunning'] != False:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['ServerNotRunning'])

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

        #发送卡片list
        elif 'cardlist' == text:
            if self.getBDSPoll():
                self.Runcmd('list')
                cl = threading.Thread(target=self.cardlist)
                cl.setName('CardList')
                cl.start()
            else:
                if Language['ServerNotRunning']:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['ServerNotRunning'])

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
            import Library.Tool as tool
            m = threading.Thread(target=tool.motdServer,args=(addr,port,group))
            m.setName('MotdServer')
            m.start()

        #输出名单
        elif 'outlist' == text:
            if self.getBDSPoll():
                self.Runcmd('list')
                cl = threading.Thread(target=self.outList)
                cl.setName('OutList')
                cl.start()
            else:
                if Language['ServerNotRunning']:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['ServerNotRunning'])

        #解析假人命令
        elif 'FakePlayer' in text:
            args = text.split(' ')
            #获取假人名
            if '"' in text:
                name = re.search(r'\"(.*)\"',text)[0].replace('"','')
            else:
                if len(args) > 2:
                    name = args[2]
                else:
                    name = ''

            #添加假人FakePlayer add Test <Steve> <AllowChat>
            if args[1] == 'add':
                if len(args) >= 5:
                    if args[4] == 'true':
                        b = True
                    else:
                        b = False
                    AddFakePlayer(name,args[3],b)
                
                elif len(args) == 4:
                    AddFakePlayer(name,args[3])

                elif len(args) == 3:
                    AddFakePlayer(name)
                
                else:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['FakePlayerError'].replace(r'%error%',PLP['FakePlayer.ARGError']))
            
            #移除假人FakePlayer remove Test:
            elif args[1] == 'remove':
                if len(args) == 3:
                    RemoveFakePlayer(name)
                else:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['FakePlayerError'].replace(r'%error%',PLP['FakePlayer.ARGError']))

            #断开连接假人FakePlayer disconnect Test:
            elif args[1] == 'disconnect':
                if len(args) == 3:
                    RemoveFakePlayer(name)
                else:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['FakePlayerError'].replace(r'%error%',PLP['FakePlayer.ARGError']))

            #连接假人
            elif args[1] == 'connect':
                if len(args) == 3:
                    ConnectPlayer(name)
                else:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['FakePlayerError'].replace(r'%error%',PLP['FakePlayer.ARGError']))

            #设置聊天
            elif args[1] == 'setchat':
                if len(args) == 4:
                    setChatControl(name,args[3])
                elif len(args) == 3:
                    setChatControl(name)
                else:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['FakePlayerError'].replace(r'%error%',PLP['FakePlayer.ARGError']))

            #获取状态
            elif args[1] == 'getstate':
                if len(args) == 3:
                    GetState(name)
                else:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['FakePlayerError'].replace(r'%error%',PLP['FakePlayer.ARGError']))

            #获取所有状态
            elif args[1] == 'allstate':
                GetAllState()

            #获取所有假人
            elif args[1] == 'list':
                GetList()

            #移除所有假人
            elif args[1] == 'removeall':
                Remove_All()
        #执行指令
        else:
            self.Runcmd(text)

    def checkBDS(self):
        from Library.src import window_root
        while True:
            time.sleep(1)
            if not self.getBDSPoll() and self.NormalStop == True:
                window_root.runserverb.configure(state='normal')
                window_root.runserverc.configure(state='normal')
                window_root.stoper.configure(state='disabled')
                window_root.scrc.insert('end','[INFO] %s' % PLP['BDSContorl.Poll.stop'])
                window_root.ServerNow.configure(text='%s %s' % (PLP['BDSUI.State'],PLP['Server.NoRunning']))
                window_root.GameFile.configure(text=PLP['BDSUI.World'])
                window_root.GameVersion.configure(text=PLP['BDSUI.Version'])
                window_root.action.configure(state='disabled')
                window_root.nameEntered.configure(state='disabled')
                break

            elif not self.getBDSPoll() and self.NormalStop == False and config['AutoRestart']:
                if Language['AbendServer'] != False:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['AbendServer'])
                if Language['RestartServer'] != False:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['RestartServer'])
                window_root.ServerNow.configure(text='%s %s' % (PLP['BDSUI.State'],PLP['Server.NoRunning']))
                window_root.GameFile.configure(text=PLP['BDSUI.World'])
                window_root.GameVersion.configure(text=PLP['BDSUI.Version'])
                if config['MaxAutoRestart'] > self.Restart:
                    self.RunServer()
                    self.Restart += 1
                else:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['MaxRestart'])
                    self.Restart = 0
                break

            elif not self.getBDSPoll() and self.NormalStop == False and config['AutoRestart'] == False:
                if Language['AbendServer'] != False:
                    for i in config['Group']:
                        sendGroupMsg(i,Language['AbendServer'])
                window_root.runserverb.configure(state='normal')
                window_root.runserverc.configure(state='normal')
                window_root.stoper.configure(state='disabled')
                window_root.scrc.insert('end','[INFO] %s' % PLP['BDSContorl.Poll.stop'])
                window_root.ServerNow.configure(text='%s %s' % (PLP['BDSUI.State'],PLP['Server.NoRunning']))
                window_root.GameFile.configure(text=PLP['BDSUI.World'])
                window_root.GameVersion.configure(text=PLP['BDSUI.Version'])
                window_root.action.configure(state='disabled')
                window_root.nameEntered.configure(state='disabled')
                break

    def stoperd(self):
        from Library.src import window_root
        answer = mBox.askyesno(PLP['BDSUI.ForceStop.title'], PLP['BDSUI.ForceStop.message']) 
        if answer == True:
            self.NormalStop = True
            subprocess.Popen("cmd.exe /k taskkill /F /T /PID %i" % self.bds.pid,stdout=subprocess.PIPE)  
            if Language['ForcedStop'] != False:
                for i in config['Group']:
                    sendGroupMsg(i,Language['ForcedStop'])
            window_root.action.configure(state='disabled')
            window_root.nameEntered.configure(state='disabled')
            from Library.Loader.Plugin import Events
            for e in Events['ForcedStop']:
                try:
                    e()
                except Exception as e:
                    log_debug(e)
    
    def runfileserver(self):
        from Library.src import window_root
        window_root.scrc.delete(1.0,'end')
        self.bds = os.system("start Temp/run.bat")
        window_root.runserverb.configure(state='disabled')
        window_root.runserverc.configure(state='disabled')
        window_root.stoper.configure(state='normal')
        window_root.ServerNow.configure(text='%s %s' % (PLP['BDSUI.State'],PLP['Server.Running']))
        c = threading.Thread(target=self.checkBDS)
        c.setName('CheckBDS')
        c.start()

#控制台正则匹配
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

#群聊消息接收
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
            j = json.loads(Sbot.ws.recv())
            #log_debug(j)
        except ConnectionResetError as e:
            log_debug(e)
            mBox.showerror(PLP['Mirai.title'],PLP['Mirai.close'])
            break
        except Exception as e:
            log_debug(e)
            mBox.showerror(PLP['Mirai.title'],PLP['Mirai.insideError'])
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
                                            sendGroupMsg(g,rps)
                                    #执行命令
                                    elif b['run'][:2] == '<<':
                                        if 'motd' in cmd[2:]:
                                            server.Botruncmd(rps+' '+str(group))
                                        elif 'bindid' in cmd[2:]:
                                            server.Botruncmd(rps+' '+str(group))
                                        elif 'unbind' in cmd[2:]:
                                            server.Botruncmd(rps+' '+str(group))
                                        elif plugin.checkcmd(rps):
                                            plugin.pluginCmd(rps,group,senderqq,sendername)
                                        else:
                                            server.Botruncmd(rps)
                                else:
                                    if Language['NoPermission'] != False:
                                        sendGroupMsg(group,Language['NoPermission'])

                            else:
                                if b['run'][:2] == '>>':
                                    for g in config["Group"]:
                                        sendGroupMsg(g,rps)
                                #执行命令
                                elif b['run'][:2] == '<<':
                                    if 'motd' in cmd[2:]:
                                        server.Botruncmd(rps+' '+str(group))
                                    elif 'bind' in cmd[2:]:
                                        server.Botruncmd(rps+' '+str(group))
                                    elif 'unbind' in cmd[2:]:
                                        server.Botruncmd(rps+' '+str(group))
                                    elif plugin.checkcmd(rps):
                                        plugin.pluginCmd(rps,group,senderqq,sendername)
                                    else:
                                        server.Botruncmd(rps)
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
                                Sbot.recallmsg(Sourceid)
                            Sbot.send_at(group,senderqq,Language['AtNotXboxid'])
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
                                    Sbot.changeName(qqid,group,p['id'])
                                    if Language['ChangeNick'] != False:
                                        Sbot.send_at(group,qqid,Language['ChangeNick'])

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
                                sendGroupMsg(group,Language['LeftGroup'].replace(r'%xboxid%',xboxid))
                            server.Botruncmd('whitelist remove "%s"' % xboxid)
        elif j['syncId'] == '123' and 'data' in j:
            try:
                ij = j['data']
                if ij['code'] == 0 and ij['messageId'] == -1:
                    log_warn(PLP['Mirai.send.shield'])
            except JSONDecodeError as e:
                log_debug(e)
                log_error(PLP['Mirai.send.insideError'])

        elif j['syncId'] == '1234' and 'data' in j:
            try:
                ij = j['data']
                if ij['code'] == 10:
                    log_warn(PLP['Mirai.change.NoPermissions'])
            except JSONDecodeError as e:
                log_debug(e)
                log_error(PLP['Mirai.change.insideError'])
            
        elif j['syncId'] == '12345' and 'data' in j:
            try:
                ij = j['data']
                if ij['messageId'] == -1:
                    log_warn(PLP['Mirai.card.shield'])
            except JSONDecodeError as e:
                log_debug(e)
                log_error(PLP['Mirai.card.insideError'])


def update_window():
    while True:
        time.sleep(2)
        from Library.src import cpup
        from Library.src import window_root
        try:
            window_root.CpuC.configure(text=PLP['MainUI.CPU']+' '+str(cpup)+'%')
        except:
            pass


if __name__ == '__main__':
    from Library.src import server
    plugin = Plugin()

    #启用线程
    upd = threading.Thread(target=update_window)
    upd.setDaemon(True)
    upd.setName('UpWindow')
    upd.start()

    updv = threading.Thread(target=testupdate)
    updv.setDaemon(True)
    updv.setName('UpDateBot')
    updv.start()
    
    
    #写入bat
    with open('Temp\\run.bat','w',encoding='utf8') as f:
        lines = '''@echo off
cd "%s"
%s'''
        f.write(lines % (config['ServerPath'],config['ServerCmd']))

    #导入加载器
    try:
        from Library.Loader.Plugin import Author
        from Library.Loader.Plugin import Type
    except ImportError:
        pass
    else:
        #完成全部导入
        log_info(PLP['Plugin.load'].replace(r'%TYPE%',Type).replace(r'%AUTHOR%',Author))
        from Library.Loader.Plugin import *
    
        plugin.loader = True
        from Library.Loader.Plugin import Events
        for e in Events['Running']:
            try:
                e()
            except Exception as e:
                log_debug(e)

    #假人服务
    from Library.FakePlayer import *
    if config['FakePlayerService']['Enable']:
        if Build_Connect():
            log_info(PLP['Start.FakePlayer.Connected'])
        else:
            log_error(PLP['Start.FakePlayer.Failed'])

    #杂项
    import Library.Tool as tool
    tool.writeconfig()
    tool.crontab()
    if config['EnableCron']:
        croncmdt = threading.Thread(target=runcron)
        croncmdt.setName('Cron_Timer')
        croncmdt.start()

    if config['EnableGroup']:
        gmsp = threading.Thread(target=usegroupregular)
        gmsp.setName('RecvGroupMsg')
        gmsp.start()

    #输出废话
    log_info('Phsebot was successfully started')
    log_info('Author: HuoHuaX')
    log_info('Special Thanks McPlus Yanhy2000 strong support for this project')
    
    #更新窗口
    try:
        window_root.win.mainloop()
    except KeyboardInterrupt as e:
        window_root.on_closing()
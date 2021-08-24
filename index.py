
#======================
# imports
#======================
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
from datetime import datetime
print('[INFO] 启动时间:',datetime.now())

#全局变量
StartedServer = False
Used = False
Sended = []
 
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
monty = ttk.LabelFrame(tab1, text='BDS控制台')
monty.grid(column=0, row=0, padx=7, pady=4)
 
# Modified Button Click Function
def runcmd():
    result=nameEntered.get()+'\r\n'
    cmd = result.encode('utf8')
    obj.stdin.write(cmd)
    obj.stdin.flush()
    nameEntered.delete(0, 'end')

def checkBDS():
    global StartedServer
    time.sleep(1)
    while True:
        time.sleep(0.5)
        if not check("bedrock_server.exe"):
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
    global StartedServer,Version,Sended
    line = []
    updateLine = ''
    while StartedServer:
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
                                if 'SendedVersion' not in Sended:
                                    Sended.append('SendedVersion')
                                    if Language['ServerVersion'] != False:
                                        for b in config["Group"]:
                                            sendGroupMsg(b,Language['ServerVersion'].replace('%Version%',Version))
                            #打开世界
                            if 'opening' in i:
                                World = re.findall(r'opening\s(.+?)[\r\s]',i)[0]
                                GameFile.configure(text='服务器存档：'+World)
                                if 'OpenWorld' not in Sended:
                                    Sended.append('OpenWorld')
                                    if Language['OpenWorld'] != False:
                                        for b in config["Group"]:
                                            sendGroupMsg(b,Language['OpenWorld'].replace('%World%',World))

                            #加载端口
                            if 'IPv4' in i:
                                Port = re.findall(r'^\[INFO\]\sIPv4\ssupported,\sport:\s(.+?)$',i)[0]
                                if 'PortOpen' not in Sended:
                                    Sended.append('PortOpen')
                                    if Language['PortOpen'] != False:
                                        for b in config["Group"]:
                                            sendGroupMsg(b,Language['PortOpen'].replace('%Port%',Port))

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

    
        
def runserver():
    global obj,StartedServer,Sended
    Sended = []
    StartedServer = True
    scr.delete(1.0,'end')
    runserverb.configure(state='disabled')
    runserverc.configure(state='disabled')
    stoper.configure(state='normal')
    ServerNow.configure(text='服务器状态：已启动')
    obj = subprocess.Popen("Library\index.bat > console.txt", stdin=subprocess.PIPE, 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    show = threading.Thread(target=showinfo)
    show.start()
    c = threading.Thread(target=checkBDS)
    c.start()

def runfileserver():
    global obj
    scr.delete(1.0,'end')
    obj = subprocess.Popen("cmd.exe /C Library\index.bat", stdin=subprocess.PIPE, 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    runserverb.configure(state='disabled')
    runserverc.configure(state='disabled')
    stoper.configure(state='normal')
    ServerNow.configure(text='服务器状态：已启动')
    c = threading.Thread(target=checkBDS)
    c.start()


#BDS控制台日志输出  
scrolW  = 75; scrolH  =  21
scr = scrolledtext.ScrolledText(monty, width=scrolW, height=scrolH, wrap=tk.WORD)
scr.grid(column=0, row=0, sticky='WE', columnspan=3)
#scr.configure(state='disabled')

#命令输入
ttk.Label(monty, text="键入命令：").grid(column=0, row=2, sticky='W')
name = tk.StringVar()
nameEntered = ttk.Entry(monty, width=70, textvariable=name)
nameEntered.grid(column=0, row=3, sticky='W')

#执行命令
action = ttk.Button(monty,text="执行",width=5,command=runcmd)   
action.grid(column=2,row=3,rowspan=2)


createToolTip(action,'执行BDS命令')

#createToolTip(bookChosen, '这是一个Combobox.')
createToolTip(scr,'BDS日志输出')
createToolTip(nameEntered,'键入命令')

infos = ttk.LabelFrame(tab1, text='信息展示',width=500,height=100)
infos.grid(column=1, row=0, padx=1, pady=10,)

#QQ信息
QQInfo = ttk.LabelFrame(infos, text='QQ信息')
QQid = ttk.Label(QQInfo, text="账号：",width=20)
QQid.grid(column=0, row=0,sticky='W')
use = ttk.Label(QQInfo, text="授权状态：",width=20)
use.grid(column=0, row=1,sticky='W')
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
runserverb.grid(column=0,row=5,rowspan=2)
ttk.Label(ServerUse, text="从配置启动",width=17).grid(column=1, row=5)

runserverc = ttk.Button(ServerUse,text=">",width=2,command=runfileserver)   
runserverc.grid(column=0,row=7,rowspan=2)
ttk.Label(ServerUse, text="从文件启动",width=17).grid(column=1, row=7)

stoper = ttk.Button(ServerUse,text=">",width=2,command=runcmd)   
stoper.grid(column=0,row=10,rowspan=2)
ttk.Label(ServerUse, text="强制停止",width=17,foreground='red').grid(column=1, row=10)
stoper.configure(state='disabled')

ServerUse.grid(column=0, row=2, padx=5, pady=10,sticky='W')

ttk.Label(infos, text="",width=20).grid(column=0, row=10)
ttk.Label(infos, text="",width=20).grid(column=0, row=11)
ttk.Label(infos, text="",width=20).grid(column=0, row=12)


# 一次性控制各控件之间的距离
for child in monty.winfo_children(): 
    child.grid_configure(padx=3,pady=1)
for child in infos.winfo_children(): 
    child.grid_configure(padx=3,pady=1)
'''# 单独控制个别控件之间的距离
action.grid(column=2,row=1,rowspan=2,padx=6)'''
#---------------Tab1控件介绍------------------#
 
 
#---------------Tab2控件介绍------------------#
# We are creating a container tab3 to hold all other widgets -- Tab2
monty2 = ttk.LabelFrame(tab2, text='控件示范区2')
monty2.grid(column=0, row=0, padx=8, pady=4)
# Creating three checkbuttons
chVarDis = tk.IntVar()
check1 = tk.Checkbutton(monty2, text="失效选项", variable=chVarDis, state='disabled')
check1.select()  
check1.grid(column=0, row=0, sticky=tk.W)                 
 
chVarUn = tk.IntVar()
check2 = tk.Checkbutton(monty2, text="遵从内心", variable=chVarUn)
check2.deselect()   #Clears (turns off) the checkbutton.
check2.grid(column=1, row=0, sticky=tk.W )                  
 
chVarEn = tk.IntVar()
check3 = tk.Checkbutton(monty2, text="屈于现实", variable=chVarEn)
check3.deselect()
check3.grid(column=2, row=0, sticky=tk.W)                 
 
# GUI Callback function 
def checkCallback(*ignoredArgs):
    # only enable one checkbutton
    if chVarUn.get(): check3.configure(state='disabled')
    else:             check3.configure(state='normal')
    if chVarEn.get(): check2.configure(state='disabled')
    else:             check2.configure(state='normal') 
 
# trace the state of the two checkbuttons  #？？
chVarUn.trace('w', lambda unused0, unused1, unused2 : checkCallback())    
chVarEn.trace('w', lambda unused0, unused1, unused2 : checkCallback())   
 
# Radiobutton list
values = ["富强民主", "文明和谐", "自由平等","公正法治","爱国敬业","诚信友善"]
 
# Radiobutton callback function
def radCall():
    radSel=radVar.get()
    if   radSel == 0: monty2.configure(text='富强民主')
    elif radSel == 1: monty2.configure(text='文明和谐')
    elif radSel == 2: monty2.configure(text='自由平等')
    elif radSel == 3: monty2.configure(text='公正法治')
    elif radSel == 4: monty2.configure(text='爱国敬业')
    elif radSel == 5: monty2.configure(text='诚信友善')
 
# create three Radiobuttons using one variable
radVar = tk.IntVar()
 
# Selecting a non-existing index value for radVar
radVar.set(99)    
 
# Creating all three Radiobutton widgets within one loop
for col in range(4):
    #curRad = 'rad' + str(col)  
    curRad = tk.Radiobutton(monty2, text=values[col], variable=radVar, value=col, command=radCall)
    curRad.grid(column=col, row=6, sticky=tk.W, columnspan=3)
for col in range(4,6):
    #curRad = 'rad' + str(col)  
    curRad = tk.Radiobutton(monty2, text=values[col], variable=radVar, value=col, command=radCall)
    curRad.grid(column=col-4, row=7, sticky=tk.W, columnspan=3)
 
style = ttk.Style()
style.configure("BW.TLabel", font=("Times", "10",'bold'))
ttk.Label(monty2, text="   社会主义核心价值观",style="BW.TLabel").grid(column=2, row=7,columnspan=2, sticky=tk.EW)
 
# Create a container to hold labels
labelsFrame = ttk.LabelFrame(monty2, text=' 嵌套区域 ')
labelsFrame.grid(column=0, row=8,columnspan=4)
 
# Place labels into the container element - vertically
ttk.Label(labelsFrame, text="你才25岁，你可以成为任何你想成为的人。").grid(column=0, row=0)
ttk.Label(labelsFrame, text="不要在乎一城一池的得失，要执着。").grid(column=0, row=1,sticky=tk.W)
 
# Add some space around each label
for child in labelsFrame.winfo_children(): 
    child.grid_configure(padx=8,pady=4)
#---------------Tab2控件介绍------------------#
 
 
#---------------Tab3控件介绍------------------#
tab3 = tk.Frame(tab3, bg='#AFEEEE')
tab3.pack()
for i in range(2):
    canvas = 'canvas' + str(col)
    canvas = tk.Canvas(tab3, width=162, height=95, highlightthickness=0, bg='#FFFF00')
    canvas.grid(row=i, column=i)
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
fileMenu = Menu(menuBar, tearoff=0)
fileMenu.add_command(label="新建")
fileMenu.add_separator()
fileMenu.add_command(label="退出", command=_quit)
menuBar.add_cascade(label="文件", menu=fileMenu)
 
 
# Display a Message Box
def _msgBox1():
    mBox.showinfo('Python Message Info Box', '通知：程序运行正常！')
def _msgBox2():
    mBox.showwarning('Python Message Warning Box', '警告：程序出现错误，请检查！')
def _msgBox3():
    mBox.showwarning('Python Message Error Box', '错误：程序出现严重错误，请退出！')
def _msgBox4():
    answer = mBox.askyesno("Python Message Dual Choice Box", "你喜欢这篇文章吗？\n您的选择是：") 
    if answer == True:
        mBox.showinfo('显示选择结果', '您选择了“是”，谢谢参与！')
    else:
        mBox.showinfo('显示选择结果', '您选择了“否”，谢谢参与！')
 
# Add another Menu to the Menu Bar and an item
msgMenu = Menu(menuBar, tearoff=0)
msgMenu.add_command(label="通知 Box", command=_msgBox1)
msgMenu.add_command(label="警告 Box", command=_msgBox2)
msgMenu.add_command(label="错误 Box", command=_msgBox3)
msgMenu.add_separator()
msgMenu.add_command(label="判断对话框", command=_msgBox4)
menuBar.add_cascade(label="消息框", menu=msgMenu)
#----------------菜单栏介绍-------------------#
 
 
# Change the main windows icon
win.iconbitmap(r'Library/Images/bot.ico')
win.geometry('742x397')
# Place cursor into name Entry
#nameEntered.focus()      
#======================
# Start GUI
#======================
loginQQ()
try:
    win.mainloop()
except KeyboardInterrupt:
    print('[INFO] 退出程序...')
    os._exit(0)

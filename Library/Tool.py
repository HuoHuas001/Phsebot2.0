from botmain import *
from Library.motd import *
from Library.src import *
from datetime import datetime
from croniter import CroniterBadCronError, CroniterNotAlphaError, croniter

import tkinter as tk
from datetime import datetime
from json import JSONDecodeError
from tkinter import *
from tkinter import Menu, Spinbox
from tkinter import messagebox as mBox
from tkinter import scrolledtext, ttk
from tkinter.constants import END
import tkinter.font as tf

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
    str_time_now= datetime.now()
    for i in cronl:
        try:
            iter=croniter(i['cron'],str_time_now)
            time = iter.get_next(datetime).strftime("%Y-%m-%d-%H-%M-%S")
            cmd = i['cmd']
            croncomment.append({'time':time,'cmd':cmd,'cron':i['cron']})
        except CroniterNotAlphaError as e:
            log_debug(e)
            log_error(i['cron'],PLP['Cron.parsefaild'])
        except CroniterBadCronError as e:
            log_debug(e)
            log_error(i['cron'],PLP['Cron.parsefaild'])
    write_file('Temp/crontab.json',croncomment)
    log_info(PLP['Retime.reload'])

#运行计划任务
def runcron():
    from botmain import server
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
                        sendGroupMsg(g,rps)
                #控制台
                elif i['cmd'][:2] == '<<':
                    server.Botruncmd(rps)
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

def edit_ragular(content):
    from Library.window import Editregular
    from botmain import window_root
    Editregular(window_root.win,content,True)

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



def motdServer(ip,port,group):
    motd = Server(ip,int(port))
    jmotd = motd.motd()
    if jmotd['status'] == 'online':
        if Language['MotdSuccessful'] != False:
            sendmsg = Language['MotdSuccessful'].replace(r'%ip%',jmotd['ip']).replace(r'%port%',str(jmotd['port'])).replace(r'%motd%',jmotd['name'])\
            .replace(r'%agreement%',jmotd['protocol']).replace(r'%version%',jmotd['version']).replace(r'%delay%',str(jmotd['delay'])+'ms')\
                .replace(r'%online%',jmotd['online']).replace(r'%max%',jmotd['upperLimit']).replace(r'%gamemode%',jmotd['gamemode'])

            sendGroupMsg(group,sendmsg.replace('\\n','\n'))
    else:
        if Language['MotdFaild'] != False:
            sendGroupMsg(group,Language['MotdFaild'])




#重载所有文件
def filereload():
    from botmain import window_root
    global config,Language,cron,NoOut
    config = read_file('data/config.yml')
    Language = read_file('data/Language.yml')
    cron = read_file('data/Cron.json')
    conn = sq.connect('data/regular.db')
    NoOut = read_file('data/NoOut.yml')
    c = conn.cursor()
    cursor = c.execute("SELECT *  from interactive")
    cmd = ''
    window_root.mlc.delete(0,END)
    window_root.mlb.delete(0,END)
    for row in cursor:
        r = row[0]
        by = row[1]
        perm = row[2]
        cmd = row[3]
        window_root.mlb.insert(END,(r,cmd,perm,by))
    conn.close()
    with open('data/Cron.json','r',encoding='utf-8') as f:
        cronl = json.loads(f.read())
    for i in cronl:
        window_root.mlc.insert(END,(i['cron'],i['cmd']))
    crontab()
    mBox.showinfo(PLP['Reload.title'],PLP['Reload.message'].replace('\\n','\n'))
    log_info(PLP['Retime.reload'])

def createToolTip( widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

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
                        sendGroupMsg(g,rps)
                #控制台
                elif i['cmd'][:2] == '<<':
                    server.Botruncmd(rps)
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

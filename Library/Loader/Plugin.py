#定义加载头
Author = 'HuoHuaX'
Type = 'official'

#定义加载器方法
import sys
import os
#添加工作目录
sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('.')+'\\Library\\PLib')

from Library.Logger import *
from Library.src import *
import sqlite3 as sq
import threading
import time


cmds = {}
Events = {
    'PlayerJoin':[],#玩家加入 -> playername:str
    'PlayerExit':[],#玩家退出 -> playername:str
    'LoadVersion':[],#加载版本号 -> version:str
    'OpenWorld':[],#加载存档 -> world:str
    'LoadPort':[],#加载端口 -> port:int
    'ServerStarted':[],#服务器开服完成 -> 无
    'StoppingServer':[],#关服中 -> 无
    'StoppedServer':[],#服务器关服完成 ->无
    'Crash':[],#服务器崩溃 -> 无
    'StartingServer':[],#开服中 -> 无
    'ForcedStop':[],#强制停止 -> 无
    'ConsoleUpdate':[],#控制台更新 -> line:str
    'RunCmd':[],#运行命令 -> cmd:str
    'Exit':[],#程序退出 -> 无
    'Running':[]#程序开启 -> 无
}
PluginCmd = {

}
class Cmd():
    def __init__(self,ctype:str,command:str,func):
        self.type = ctype
        self.command = command
        self.function = func


# 定义一个MyThread.py线程类
class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
    def run(self):
        time.sleep(2)
        self.result = self.func(*self.args)
    def get_result(self):
        threading.Thread.join(self)  # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None

#注册一个botcmd
def regBotCmd(cmd:str,function) -> dict:
    '''注册一个普通命令
    :param cmd: 需要注册的命令
    :param function: 回调函数,(不需要括号)
    '''
    global cmds
    if cmd not in cmds:
        cmds[cmd] = Cmd('ordinary',cmd,function)
        return {'code':0,'msg':'register cmd success'}
    else:
        return {'code':2,'msg':'This command is registered'}

def regArgCmd(cmd_m:str,function) -> dict:
    '''注册一个参数命令
    :param cmd_m: 需要注册的命令关键字
    :param function: 回调函数,(不需要括号)
    '''
    global cmds
    if cmd_m not in cmds:
        cmds[cmd_m] = Cmd('args',cmd_m,function)
        return {'code':0,'msg':'register cmd success'}
    else:
        return {'code':2,'msg':'This command is registered'}

#向所有群发送消息
def SendAllGroup(text:str) -> dict:
    '''向所有群发消息
    :param text: 发送的文本
    '''

    for i in config['Group']:
        sendGroupMsg(i,text)
    return {'code':0,'msg':'Send message success'}

#指定群发消息
def SendGroup(group:int,text:str):
    '''向指定群发消息
    :param group: 指定的群号
    :param text: 发送的文本
    '''
    if group in config['Group']:
        sendGroupMsg(group,text)
        return {'code':0,'msg':'Send message success'}
    else:
        return {'code':1,'msg':'Not Found Group'}

#使用QQ号获取Xboxid
def getXboxID(qqid) -> str:
    '''使用QQ号获取xboxid
    :param qqid: QQ号
    注：未绑定为%Xboxid%
    '''
    conn = sq.connect('data/xuid.db')
    c = conn.cursor()
    cursor = c.execute("SELECT *  from xboxid")
    name = r'%Xboxid%'
    for row in cursor:
        qq = row[0]
        xboxid = row[1]
        if qqid == qq:
            name = xboxid
    conn.close()
    return name


#注册一个事件
def regEvent(Event:str,function) -> dict:
    '''注册一个事件
    :param Event: 事件名称
    :param function: 回调函数
    '''
    global Events
    if Event in Events:
        Events[Event].append(function)
        return {'code':0,'msg':'register event success'}
    else:
        return {'code':1,'msg':'Not Found '+Event}

#键入指令
def Runcmd(cmd:str):
    '''运行一个命令
    :param cmd: 命令
    '''
    from Library.src import server
    server.Runcmd(cmd)

def getlistT():
    time.sleep(1)
    from Library.src import server
    return server.Players

#返回在线的玩家列表
def getList() -> dict:
    '''返回在线的玩家列表
    '''
    Runcmd('list')
    l = MyThread(getlistT)
    l.start()
    l.join()
    result = l.get_result()
    log_debug(result)
    result['Player'] = result['Player'].split(', ')
    return result

#注册一个Pcmd
def regPCmd(cmd_main:str,function) -> dict:
    '''注册一个PCmd
    :param cmd_main: 命令关键字
    :param function: 回调函数
    '''
    global PluginCmd
    if cmd_main not in PluginCmd:
        PluginCmd[cmd_main] = Cmd('plugincmd',cmd,function)
        return {'code':0,'msg':'register cmd success'}
    else:
        return {'code':2,'msg':'This command is registered'}


#加载的插件
from Plugin import loadlist
for i in loadlist:
    log_info(PLP['Plugin.loading'].replace('%plugin%',i))
from Plugin import *
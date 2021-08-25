import psutil
import requests
import socket
import json
import yaml
import threading
import re
import sqlite3
from websocket import create_connection

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
    authCode = requests.post(url+'/verify',json={"verifyKey":key})
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





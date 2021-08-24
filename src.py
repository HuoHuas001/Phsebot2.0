import psutil
import requests
import socket
import json
import yaml
import threading

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

config = read_file('data/config.json')
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
            { "type":"Plain", "text":text },
        ]
    }
    r = requests.post(url+'/sendGroupMessage',json=msgjson)
    j = json.loads(r.text)
    if j['code'] == 0 and j['messageId'] == -1:
        print('[INFO] 消息已发送，但可能遭到屏蔽')
    return True





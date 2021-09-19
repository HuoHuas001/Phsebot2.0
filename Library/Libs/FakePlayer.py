#导入模块
from os import remove
from websocket import create_connection
from Library.Libs.basic import *
import json
from Library.Libs.Logger import log_error, log_info, log_warn, log_debug

ConnectED = False
ControlList = config['FakePlayerService']['Control']
EnableFakePlayer = config['FakePlayerService']['Enable']
Eventa = config['FakePlayerService']['Event']
def state(num):
    if num == 0:
        return '连接中'
    elif num == 1:
        return '已连接'
    elif num == 2:
        return '断开连接中'
    elif num == 3:
        return '已断开连接'
    elif num == 4:
        return '重新连接中'
    elif num == 5:
        return '停止中'
    elif num == 6:
        return '已停止'

def RecvEvent():
    while ConnectED:
        time.sleep(0.1)
        #接受数据
        try:
            j = json.loads(fws.recv())
        except Exception as e:
            j = {}
            log_debug(e)
            log_error('假人服务出现了未知错误')


        #列表(list)
        if j['type'] == 'list' and Eventa['list']:
            namelist = ''
            for i in j['data']['list']:
                if namelist == '':
                    namelist += i
                else:
                    namelist += '\n'+i
            for i in config['Group']:
                if Language['FakePlayerList'] != False:
                    sendGroupMsg(i,Language['FakePlayerList'].replace(r'%list%',namelist))

        #添加(add)
        elif j['type'] == 'add' and Eventa['add']:
            if j['data']['success']:
                for i in config['Group']:
                    if Language['FakePlayerInfo'] != False:
                        sendGroupMsg(i,Language['FakePlayerInfo'].replace(r'%info%','假人添加完成'))
            else:
                for i in config['Group']:
                    if Language['FakePlayerError'] != False:
                        sendGroupMsg(i,Language['FakePlayerError'].replace(r'%error%',j['data']['reason']))

        #移除(remove)
        elif j['type'] == 'remove' and Eventa['remove']:
            if j['data']['success']:
                for i in config['Group']:
                    if Language['FakePlayerInfo'] != False:
                        sendGroupMsg(i,Language['FakePlayerInfo'].replace(r'%info%','假人移除完成'))
            else:
                for i in config['Group']:
                    if Language['FakePlayerError'] != False:
                        sendGroupMsg(i,Language['FakePlayerError'].replace(r'%error%',j['data']['reason']))

        #获取状态(getState)
        elif j['type'] == 'getState' and Eventa['getstate']:
            if j['data']['success']:
                for i in config['Group']:
                    if Language['FakePlayerInfo'] != False:
                        sendGroupMsg(i,Language['FakePlayerInfo'].replace(r'%info%',j['data']['name']+'状态为'+state(j['data']['state'])))
            else:
                for i in config['Group']:
                    if Language['FakePlayerError'] != False:
                        sendGroupMsg(i,Language['FakePlayerError'].replace(r'%error%',j['data']['reason']))

        #获取假人状态
        elif j['type'] == "getState_all" and Eventa['getstate_all']:
            states = ''
            for f in j['data']["playersData"]:
                if states == '':
                    states += f+'状态为'+state(j['data']["playersData"][f])
                else:
                    states += '\n'+f+'状态为'+state(j['data']["playersData"][f])
            for i in config['Group']:
                if Language['FakePlayerInfo'] != False:
                    sendGroupMsg(i,Language['FakePlayerInfo'].replace(r'%info%',states))

        #断开连接假人响应
        elif j['type'] == "disconnect" and Eventa['disconnect']:
            if j['data']['success']:
                for i in config['Group']:
                    if Language['FakePlayerInfo'] != False:
                        sendGroupMsg(i,Language['FakePlayerInfo'].replace(r'%info%',j['data']['name']+'已断开连接'))
            else:
                for i in config['Group']:
                    if Language['FakePlayerError'] != False:
                        sendGroupMsg(i,Language['FakePlayerError'].replace(r'%error%',j['data']['reason']))

        #连接假人响应
        elif j['type'] == 'connect' and Eventa['connect']:
            if j['data']['success']:
                for i in config['Group']:
                    if Language['FakePlayerInfo'] != False:
                        sendGroupMsg(i,Language['FakePlayerInfo'].replace(r'%info%',j['data']['name']+'已连接'))
            else:
                for i in config['Group']:
                    if Language['FakePlayerError'] != False:
                        sendGroupMsg(i,Language['FakePlayerError'].replace(r'%error%',j['data']['reason']))
        
        #移除全部假人响应
        elif j['type'] == 'remove_all' and Eventa['remove_all']:
            states = ''
            for f in j['data']["list"]:
                    states += '\n'+f
            for i in config['Group']:
                if Language['FakePlayerInfo'] != False:
                    sendGroupMsg(i,Language['FakePlayerInfo'].replace(r'%info%','已移除'+states))
        
        #移除全部假人响应
        elif j['type'] == 'disconnect_all' and Eventa['disconnect_all']:
            states = ''
            for f in j['data']["list"]:
                    states += '\n'+f
            for i in config['Group']:
                if Language['FakePlayerInfo'] != False:
                    sendGroupMsg(i,Language['FakePlayerInfo'].replace(r'%info%','已断开'+states))

        #移除全部假人响应
        elif j['type'] == 'connect_all' and Eventa['connect_all']:
            states = ''
            for f in j['data']["list"]:
                    states += '\n'+f
            for i in config['Group']:
                if Language['FakePlayerInfo'] != False:
                    sendGroupMsg(i,Language['FakePlayerInfo'].replace(r'%info%','已连接'+states))

        #聊天控制假人响应
        elif j['type'] == 'setChatControl' and Eventa['setchatcontrol']:
            if j['data']['success']:
                for i in config['Group']:
                    if Language['FakePlayerInfo'] != False:
                        sendGroupMsg(i,Language['FakePlayerInfo'].replace(r'%info%',j['data']['name']+'已修改完成'))
            else:
                for i in config['Group']:
                    if Language['FakePlayerError'] != False:
                        sendGroupMsg(i,Language['FakePlayerError'].replace(r'%error%',j['data']['reason']))  

def Build_Connect():
    global fws,ConnectED,ws
    try:
        fws = create_connection(config['FakePlayerService']['URL'])
        ConnectED = True
        recv = threading.Thread(target=RecvEvent)
        recv.setName('RecvFakePlayerEvent')
        recv.start()
        return True
    except Exception as e:
        log_debug(e)
        return False

def ConnectAllPlayer():
    if ConnectED and ControlList['StartConnect'] and EnableFakePlayer:
        conjson = {
            "id": "connect1",
            "type": "connect_all"
        }
        fws.send(json.dumps(conjson))

def DisConnectAllPlayer():
    if ConnectED and ControlList['StopDisConnect'] and EnableFakePlayer:
        disjson = {
            "id": "disconnect1",
            "type": "disconnect_all"
        }
        fws.send(json.dumps(disjson))

def AddFakePlayer(player,Skin='steve',Chat=False):
    if ConnectED and EnableFakePlayer:
        addplayer = {
            "type": "add",
            "data": {
                "name": player,
                "skin": Skin,
                "allowChatControl": Chat
            }
        }
        fws.send(json.dumps(addplayer))

        disjson = {
            "type": "disconnect",
            "data": {
                "name": player
            }
        }
        fws.send(json.dumps(disjson))
        
def RemoveFakePlayer(name):
    if ConnectED and EnableFakePlayer:
        removejson = {
            "type": "remove",
            "data": {
                "name": name
            }
        }
        fws.send(json.dumps(removejson))

def DisConnectPlayer(name):
    if ConnectED and EnableFakePlayer:
        disjson = {
            "type": "disconnect",
            "data": {
                "name": name
            }
        }
        fws.send(json.dumps(disjson))

def ConnectPlayer(name):
    if ConnectED and EnableFakePlayer:
        conjson = {
            "type": "connect",
            "data": {
                "name": name
            }
        }
        fws.send(json.dumps(conjson))

def setChatControl(name,control=False):
    if ConnectED and EnableFakePlayer:
        controljson = {
            "type": "setChatControl",
            "data": {
                "name": name,
                "allowChatControl": control
            }
        }
        fws.send(controljson)

def GetState(name):
    if ConnectED and EnableFakePlayer:
        statejson = {
            "type": "getState",
            "data": {
                "name": name
            }
        }
        fws.send(json.dumps(statejson))
    
def GetAllState():
    if ConnectED and EnableFakePlayer:
        statej = {
            "type": "getState_all"
        }
        fws.send(json.dumps(statej))

def GetList():
    if ConnectED and EnableFakePlayer:
        listj = {
            "type":'list'
        }
        fws.send(json.dumps(listj))

def Remove_All():
    if ConnectED and EnableFakePlayer:
        removej = {
            "type": "remove_all"
        }
        fws.send(json.dumps(removej))

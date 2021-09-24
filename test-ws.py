import websocket
import time
import json
from Library.src import *
import threading
def exit_ws():
    wss.send(json.dumps(
        {'type':'exit',
        'token':config['mcsm']['wsToken'],
        'name':config['mcsm']['serverName']
        }))

def recvLog():
    while True:
        time.sleep(0.1)
        rj = {'type':''}
        try:
            rj = json.loads(wss.recv())
        except Exception as e:
            log_debug(e)
            if str(e) == '[WinError 10054] 远程主机强迫关闭了一个现有的连接。':
                log_error(PLP['mcsm.disconnect'])
                break
            elif str(e) == 'socket is already closed.':
                log_error(PLP['mcsm.disconnect'])
                break
        print(rj)
        if rj['type'] == 'heart':
            wss.send(json.dumps(rj))
        elif rj['type'] == 'msg':
            exit_ws()

def wsinit():
    try:
        global wss
        wss = websocket.create_connection('ws://%s:%i' % (config['mcsm']['recvLog']['url'],config['mcsm']['recvLog']['port']))
        wss.send(json.dumps({'type':'connect','token':config['mcsm']['wsToken'],'name':config['mcsm']['serverName']}))
        log_info(PLP['mcsm.connectSuccess'])
        recvl = threading.Thread(target=recvLog)
        recvl.setDaemon(True)
        recvl.setName('Listen_MCSM')
        recvl.start()
    except Exception as e:
        log_debug(e)
        log_error(PLP['mcsm.connectError'])
wsinit()
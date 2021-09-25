import websocket
import time
import json
from Library.src import *
import threading
import hashlib
def exit_ws():
    wss.send(json.dumps(
        {'type':'exit',
        'token':config['mcsm']['wsToken'],
        'name':config['mcsm']['serverName']
        }
    )
)

def get_md5_value(src):
    myMd5 = hashlib.md5()
    myMd5.update(src)
    myMd5_Digest = myMd5.hexdigest()
    return myMd5_Digest


def runthisserver(servers):
    from Library.mcsm.http_req import getServer
    from Library.src import window_root,server
    if getServer(servers)['status']:
        server.NormalStop = False
        #窗口
        window_root.nameEntered.configure(state='normal')
        window_root.action.configure(state='normal')
        window_root.scrc.delete(1.0,'end')
        window_root.runserverb.configure(state='disabled')
        window_root.runserverc.configure(state='disabled')
        window_root.stoper.configure(state='normal')
        window_root.ServerNow.configure(text='%s %s' % (PLP['BDSUI.State'],PLP['Server.Running']))
        window_root.scrc.insert('end','[Phsebot] '+PLP['mcsm.startserver']+'\n')
        server.check = threading.Thread(target=server.checkBDS)
        server.check.setName('CheckBDS')
        server.check.start()

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

        #判断消息
        if rj['type'] == 'error':
            if rj['msg'] == 'token error':
                mBox.showerror(PLP['mcsm.tokenError.title'],PLP['mcsm.tokenError.msg'])
            elif rj['msg'] == 'name error':
                mBox.showerror(PLP['mcsm.nameError.title'],PLP['mcsm.nameError.msg'])

        elif rj['type'] == 'heart':
            wss.send(json.dumps(rj))

        elif rj['type'] == 'msg':
            from Library.src import server
            l = '[Phsebot] '+rj['msg']+'\n'
            server.insertscr(l.encode('utf8'))

        elif rj['type'] == 'log':
            from Library.src import server
            runthisserver(config['mcsm']['serverName'])
            logs = rj['log'].replace('\r','').replace('\n\n','\n').split('\n')
            for i in logs:
                if i != '':
                    ls = i + '\n'
                    server.insertscr(ls.encode('utf8'))

def wsinit():
    try:
        global wss,recvl
        md5token = get_md5_value(config['mcsm']['wsToken'].encode('utf8'))
        wss = websocket.create_connection('ws://%s:%i' % (config['mcsm']['recvLog']['url'],config['mcsm']['recvLog']['port']))
        wss.send(json.dumps({'type':'connect','token':str(md5token),'name':config['mcsm']['serverName']}))
        log_info(PLP['mcsm.connectSuccess'])
        recvl = threading.Thread(target=recvLog)
        recvl.setDaemon(True)
        recvl.setName('Listen_MCSM')
        recvl.start()
    except Exception as e:
        log_debug(e)
        log_error(PLP['mcsm.connectError'])

def reconnect_ws():
    global wss
    try:
        wss.close()
    except:
        pass

    if recvl in threading.enumerate():
        wss = websocket.create_connection('ws://%s:%i' % (config['mcsm']['recvLog']['url'],config['mcsm']['recvLog']['port']))
        wss.send(json.dumps({'type':'connect','token':config['mcsm']['wsToken'],'name':config['mcsm']['serverName']}))
        log_info(PLP['mcsm.connectSuccess'])
    else:
        wsinit()
    
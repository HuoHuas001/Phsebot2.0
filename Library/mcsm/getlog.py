import websockets
import asyncio
from Library.src import *
import threading
Log_Line = []
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


def websocket_log(url = '0.0.0.0',port = 23334):
    global Log_Line
    async def recv_log(websocket, path):
        global Log_Line
        try:
            async for message in websocket:
                msg = json.loads(message)
                if msg['type'] == 'log' and msg['server'] == config['mcsm']['serverName']:
                    runthisserver(msg['server'])
                    logs = msg['log'].replace('\r','')
                    l = logs.split('\n')
                    for i in l:
                        if '\n' not in i:
                            ls = i+'\n'
                        else:
                            ls = i
                        Log_Line.append(ls)
                        from Library.src import server
                        server.insertscr(ls.encode('utf8'))
        except Exception as e:
            log_debug(e)

    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    log_info(PLP['mcsm.enable'].replace(r'%url%','ws://%s:%i' % (url,port)))
    try:
        loop.run_until_complete(websockets.serve(recv_log, url, port))
        loop.run_forever()
    except Exception as e:
        log_debug(e)

def wsinit():
    wls = threading.Thread(target=websocket_log,args=(config['mcsm']['recvLog']['url'],config['mcsm']['recvLog']['port']))
    wls.setDaemon(True)
    wls.start()
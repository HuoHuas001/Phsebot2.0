from Library.Loader.Plugin import *
from datetime import datetime
import json
log_info('签到插件加载成功! Powered by HuoHuaX')

#签到一次加的金币
Sign = 10
#可选经济配置[llmoney或scoreboard]
Money_Type = 'llmoney'
#scoreboard名称(llmoney用户请忽略)
scoreboard = 'money'

checked = {}

def check(args):
    global checked
    qqid = args.senderId
    id = getXboxID(qqid)
    if id != r'%Xboxid%':
        checked[id] = False
        if Money_Type == 'llmoney':
            Runcmd('money add %s %i' % (id,Sign))
        with open('Plugin/check/checked.json','w',encoding='utf8') as f:
            f.write(json.dumps(checked))
        SendGroup(args.group,'签到成功')

def PlayerJoin(player):
    global checked
    if player in checked and checked[player] != True:
        Runcmd('scoreboard players add %s %s %i' % (player,scoreboard,Sign))
        checked[player] = True
        with open('Plugin/check/checked.json','w',encoding='utf8') as f:
            f.write(json.dumps(checked))

#重置签到
def clean_check():
    while True:
        time.sleep(5)
        times = datetime.now().strftime('%H-%M')
        if times == '00-00':
            checked = {}
            with open('Plugin/check/checked.json','w',encoding='utf8') as f:
                f.write('{}')

clean = threading.Thread(target=clean_check)
clean.setName('Check_Clean')
clean.setDaemon(True)
clean.start()

regBotCmd('check',check)
if Money_Type == 'scoreboard':
    regEvent('PlayerJoin',PlayerJoin)
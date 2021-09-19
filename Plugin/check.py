from Library.Loader.Plugin import *
from datetime import datetime
log_info('签到插件加载成功! Powered by HuoHuaX')

def check(args):
    pass

def clean_check():
    while True:
        times = datetime.now().strftime('%H-%M')
regBotCmd('check',check)

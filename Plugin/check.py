from Library.Loader.Plugin import *
log_info('签到插件加载成功! Powered by HuoHuaX')

def aaa(args):
    SendAllGroup('test')

regBotCmd('aaa',aaa)

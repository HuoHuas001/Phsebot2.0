from datetime import datetime
import json
import yaml
import colorama
from colorama import init,Fore,Back,Style
init(autoreset=True)

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        if '.json' in file:
            content = f.read()
            return json.loads(content)
        elif '.yml' in file:
            content = f.read()
            return yaml.load(content, Loader=yaml.FullLoader)

config = read_file('data/config.yml')

def log_info(text):
    if config['LowLog'] == 'info':
        print('\033[1;32;40m'+'['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' INFO] '+str(text)+'\033[0m')

def log_warn(text):
    if config['LowLog'] == 'info':
        print('\033[1;33m['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' WARN] '+str(text)+'\033[0m')
    elif config['LowLog'] == 'warn':
        print('\033[1;33m['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' WARN] '+str(text)+'\033[0m')

def log_error(text):
    if config['LowLog'] == 'info':
        print('\033[1;31m'+'['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' ERRO] '+str(text)+'\033[0m')
    elif config['LowLog'] == 'warn':
        print('\033[1;31m'+'['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' ERRO] '+str(text)+'\033[0m')
    elif config['LowLog'] == 'error':
        print('\033[1;31m'+'['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' ERRO] '+str(text)+'\033[0m')

def log_debug(text):
    if config['Debug']:
        print('\033[1;36m'+'[DEBUG] '+str(text)+'\033[0m')

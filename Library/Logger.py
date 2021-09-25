from datetime import datetime
import json
import yaml
import os
from tkinter import messagebox as mBox
from colorama import init,Fore,Back,Style
init(autoreset=True)

def read_file(file):
    with open(file,'r',encoding='utf-8') as f:
        if '.json' in file:
            try:
                content = f.read().replace('\\n','\n')
                return json.loads(content)
            except Exception as e:
                mBox.showerror('Error','Error parsing %s file:\n%s' % (file,str(e)))
                os._exit(1)

        elif '.yml' in file:
            try:
                content = f.read().replace('\\n','\n')
                return yaml.load(content, Loader=yaml.FullLoader)
            except Exception as e:
                mBox.showerror('Error','Error parsing %s file:\n%s' % (file,str(e)))
                os._exit(1)

config = read_file('data/config.yml')

def log_info(text):
    if config['LowLog'] == 'info':
        print('['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' INFO] '+str(text))

def log_warn(text):
    if config['LowLog'] == 'info':
        print('['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' WARN] '+str(text))
    elif config['LowLog'] == 'warn':
        print('['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' WARN] '+str(text))

def log_error(text):
    if config['LowLog'] == 'info':
        print('['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' ERRO] '+str(text))
    elif config['LowLog'] == 'warn':
        print('['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' ERRO] '+str(text))
    elif config['LowLog'] == 'error':
        print('['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' ERRO] '+str(text))

def log_debug(text):
    if config['Debug']:
        print('[DEBUG] '+str(text))

from datetime import datetime
import json
import yaml

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
        print('['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' INFO]',text)

def log_warn(text):
    if config['LowLog'] == 'info':
        print('['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' WARN]',text)
    elif config['LowLog'] == 'warn':
        print('['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' WARN]',text)

def log_error(text):
    if config['LowLog'] == 'info':
        print('['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' ERRO]',text)
    elif config['LowLog'] == 'warn':
        print('['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' ERRO]',text)
    elif config['LowLog'] == 'error':
        print('['+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+' ERRO]',text)

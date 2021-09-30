import urllib.request
import urllib.parse
from Library.src import *


def http_get(url):
    try:
        return urllib.request.urlopen(url).read().decode("utf-8")
    except Exception as e:
        log_debug(e)
        return '{}'

def http_post(url,data):
    url = url
    params = json.dumps(data)
    headers = {'Accept-Charset': 'utf-8', 'Content-Type': 'application/json'}
    #用bytes函数转换为字节
    params = bytes(params, 'utf8')
    try:
        req = urllib.request.Request(url=url, data=params, headers=headers, method='POST')
        response = urllib.request.urlopen(req).read()
        return response
    except Exception as e:
        log_debug(e)
        return None



def getServer(name:str) -> dict:
    url = config['mcsm']['URL']
    state = json.loads(http_get(url+'/api/status/'+name))
    return state

def startServer(name:str) -> dict:
    url = config['mcsm']['URL']
    server = name
    key = config['mcsm']['APIKey']
    urs = '{url}/api/start_server/{server}?apikey={key}'.format(url=url,server=server,key=key)
    return json.loads(http_get(urs))

def stopServer(name:str) -> dict:
    url = config['mcsm']['URL']
    server = name
    key = config['mcsm']['APIKey']
    urs = '{url}/api/stop_server/{server}?apikey={key}'.format(url=url,server=server,key=key)
    return json.loads(http_get(urs))

def sendCmd(name:str,cmd:str) -> dict:
    url = config['mcsm']['URL']
    server = name
    key = config['mcsm']['APIKey']
    d = {
        "name":server,
        "command":cmd
    }
    http_post('{url}/api/execute/?apikey={key}'.format(url=url,key=key),d)
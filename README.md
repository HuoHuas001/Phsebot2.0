# Phsebot
一个新的支持Pyr的机器人软件


![example](https://img.shields.io/badge/Python-3.7.9-blue.svg) 
![example](https://img.shields.io/github/downloads/HuoHuas001/Phsebot/total)
![example](https://img.shields.io/badge/Version-dev_0.8-green.svg) 

## 1.安装教程  
> 本教程适用于了解什么是cmd和pip以及json和yaml语法的用户

> 小白开启请使用 小白一键开启.bat

### 1.安装依赖库
>1.安装Python3.7.9 [下载地址](https://www.python.org/ftp/python/3.7.9/python-3.7.9.exe)
>2.bat运行如下命令
```
运行包内的Setup.bat
```

### 2.安装机器人
> 1.安装打包好的MCL => [下载地址](https://huohuas001.lanzoui.com/i50xYt6za2h)<br>

> 2.登录账号

### 3.启动Phsebot主程序
> 请注意修改config.yml<br>

> 双击 Run.bat 即可

## 2.控制台使用教程
### 1.按下<kbd>Ctrl</kbd>+<kbd>C</kbd>来快速关闭程序

## 3. 配置文件
>### 1.config.yml模板
```yaml
#服务端文件
ServerCmd: bedrock_server.exe

#服务端目录
ServerPath: E:\xxxx

#管理员列表
Admin:
  - 114514

#发消息的群聊
Group:
  - 123456789

#Mah登录地址
BotURL: "ws://localhost:8080"

#Mah登录Key
Key: "INITKEY8Gj5l2Hh"

#发消息的QQ号
Bot: 1919810
#崩服自动重启
AutoRestart: true
#@未绑定白名单的成员
AtNoXboxid: 
  #此功能开关
  Enable: false
  #自动撤回未绑定成员的消息
  Recall: false
  #自动改名
  Rename: true
#是否启用Cron表达式
EnableCron: true
#是否监听群消息
EnableGroup: true
#是否检测昵称被玩家改变
CheckNick:
  Enable: true
  WhiteList:
    - 123456
#是否开启玩家退群自动删白名单
LeftRemove: false
#DEBUG模式
Debug: true
#最低输出模式，可选:info/warn/error
LowLog: info
#最大重启次数
MaxAutoRestart: 3
#启用输出屏蔽功能
NoOut: true
#服务器信息卡片（慎用）
ServerInfoCard:
  #启用此功能
  Enable: true
  #卡片json
  CardJson: '{"app":"com.tencent.miniapp","desc":"","view":"notification","ver":"0.0.0.1","prompt":"Server Info ","appID":"","sourceName":"","actionData":"","actionData_A":"","sourceUrl":"","meta":{"notification":{"appInfo":{"appName":"服务器信息：","appType":4,"ext":"","appid":34544210,"iconUrl":"%Logo%"},"button":[{"action":"","name":" "}],"data":[{"title":"玩家状况","value":"%Online%\/%Max%"},{"title":"玩家列表","value":"%Players%"},{"title":"TPS","value":"20.0"}],"title":"状态","emphasis_keyword":""}},"text":"","sourceAd":"","extra":""}'
  Logo: 'https:\/\/z3.ax1x.com\/2021\/09\/09\/hOPbZQ.png'
#假人服务
FakePlayerService:
  Enable: true
  URL: 'ws://127.0.0.1:54321'
  Control:
    #开服自动连接假人
    StartConnect: true
    #关服自动断开假人
    StopDisConnect: true
  #通知到群里的消息
  Event:
    list: true
    add: true
    remove: true
    getstate: true
    getstate_all: true
    disconnect: true
    connect: true
    remove_all: true
    disconnect_all: true
    connect_all: true
    setchatcontrol: true
#语言包
LangPack: 'zh_cn'
#自动改变机器人名称
AutoChangeBotName:
  #启用此功能
  Enable: true
  #改变的字符串 %Online%在线人数 %Max%最大人数
  String: '服务器在线:%Online%/%Max%'
  #关服自动还原的昵称(注：还原原名称请填写'',不开启请设置false)
  StopReset: ''
#自动记录后台日志
AutoRecordBDS: true
AutoRecordBot: true
```

>### 2.Language.yml模板
```yaml
#正则语言包文件，不触发请设置为false

#ServerVersion可用变量：%Version%
ServerVersion: "[服务器] 服务器版本 %Version%"

#ServerStart可用变量：无
ServerStart: "[服务器] 服务器启动成功"

#OpenWorld可用变量：%World%
OpenWorld: "[服务器] 正在加载%World%"

#PortOpen可用变量：%Port%
PortOpen: "[服务器] 正在打开端口：%Port%"

#ServerStopping可用变量：无
ServerStopping: "[服务器] 正在请求关闭服务器"

#ServerStoped可用变量：无
ServerStoped: "[服务器] 服务器关闭完成"

#Crashed可用变量：无
Crashed: "[服务器] 服务器已崩溃，请管理员查看后台日志"

#Starting可用变量：无
Starting: "[服务器] 服务器正在启动，请稍后"

#ServerRunning可用变量：无
ServerRunning: "[服务器] 服务器已在运行中"

#ServerNotRunning可用变量：无
ServerNotRunning: "[服务器] 服务器不在运行中."

#MotdFaild可用变量：无
MotdFaild: "Motd请求失败"

#MotdSuccessful可用变量：
  #%ip% IP地址
  #%port% 端口
  #%motd% 说明
  #%agreement% 协议版本
  #%version% 客户端版本
  #%online% 在线玩家
  #%max% 最大在线玩家
  #%gamemode% 游戏模式
  #%delay% 本机到服务器的延迟
MotdSuccessful: '[MOTD] Motd成功\n服务器地址:%ip%:%port%\n说明:%motd%\n协议版本:%agreement%\n游戏版本:%version%\n在线:%online%/%max%\n游戏模式:%gamemode%\n延迟:%delay%'

#ForcedStop可用变量：无
ForcedStop: '[服务器] 服务器已被强制停止'

#AbendServer可用变量：无
AbendServer: '[服务器] 服务器异常终止'

#RestartServer可用变量：无
RestartServer: '[服务器] 服务器重新启动'

#PlayerJoin可用变量：%player% %xuid%
PlayerJoin: '[服务器] %player% 加入了服务器，其xuid为%xuid%'

#PlayerLeft可用变量：%player% %xuid%
PlayerLeft: '[服务器] %player% 离开了服务器，其xuid为%xuid%'

#XboxIDBinded可用变量：%binderqq%
XboxIDBinded: '这个XBOXID已被 QQ号为：%binderqq% 绑定'

#QQBinded可用变量：%xboxid%
QQBinded: 你已绑定xboxid：%xboxid%

#BindSuccessful可用变量：%xboxid%
BindSuccessful: 您已成功绑定%xboxid%

#NotFoundXboxID可用变量：无
NotFoundXboxID: 你没有已绑定的xboxid

#unBindSuccessful可用变量：%xboxid%
unBindSuccessful: 您已成功解绑%xboxid%

#NoPermission可用变量：无
NoPermission: '你没有权限'

#AtNotXboxid可用变量：无
AtNotXboxid: '还未绑定Xboxid'

#ChangeNick可用变量：无
ChangeNick: '请不要乱修改群名片'

#LeftGroup可用变量：%xboxid%
LeftGroup: '%xboxid% 离开了群聊，白名单自动删除'

#OnlineList可用变量：%Online% %Max% %Player%
OnlineList: '[服务器]在线玩家:%Online%/%Max%\n玩家列表:%Player%'

#FakePlayerError可用变量：%error%
FakePlayerError: '假人错误:%error%'

#FakePlayerList可用变量：%list%
FakePlayerList: '假人列表如下：\n%list%'

#FakePlayerInfo可用变量：%info%
FakePlayerInfo: '假人信息:%info%'

#MaxRestart可用变量：无
MaxRestart: '服务器已达到崩溃次数，请手动重启'
```

> ### 3.cron模板
```json
[
    {
        "cron":"*/1 * * * *",
        "cmd":">>测试114514"
    }
]
```

> ### 4.如何修改正则
- 方法一
- - 1.请先安装Navicat等其他数据库软件
- - 2.仿照已有的格式来编写正则

- 方法二
- - 正则表达式分栏双击编辑

## 4.问问题请先给开发者回答问题码才能保证您已看过Readme
> 问题码：Phsebot151915


from Library.src import *
# 弹窗
class Editregular(tk.Toplevel):
    def __init__(self, parent,content,tf):
        super().__init__()
        self.title('Phsebot - %s' % PLP['EditRegular.title'])
        self.content = content
        self.parent = parent # 显式地保留父窗口
        #self.iconbitmap(r'Library/Images/bot.ico')
        self.geometry('400x205')
        self.tf = tf
        self.resizable(0,0)
        ms = ttk.LabelFrame(self, text='%s' % PLP['EditRegular.frame'],width=9,height=10)
        ms.grid(column=0, row=0, padx=7, pady=4)
        
        # 第一行（两列）
        row1 = tk.Frame(ms)
        row1.pack(fill="x")
        tk.Label(row1, text=PLP['EditRegular.regular'], width=10).pack(side=tk.LEFT)
        self.path = tk.StringVar()
        self.path.set(content[0])
        path = tk.Entry(row1, textvariable=self.path, width=42)
        path.pack(side=tk.LEFT)
        
        # 第二行
        row2 = tk.Frame(ms)
        row2.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row2, text=PLP['EditRegular.command'], width=10).pack(side=tk.LEFT)
        self.file = tk.StringVar()
        self.file.set(content[1])
        file = tk.Entry(row2, textvariable=self.file, width=42)
        file.pack(side=tk.LEFT)

        # 第三行
        row3 = tk.Frame(ms)
        row3.pack(fill="x")
        self.autostatus=tk.IntVar()
        self.auto = tk.Checkbutton(row3, text=PLP['EditRegular.admin'],variable=self.autostatus)
        if content[2] == '管理员':
            self.auto.select()
        self.auto.pack(side=tk.LEFT)

        # 第四行
        row4 = tk.Frame(ms)
        row4.pack(fill="x", ipadx=1, ipady=1)
        self.iv_default = tk.IntVar()
        self.rb_default_Label = tk.Label(row4, text=PLP['EditRegular.from'])
        self.rb_default1 = tk.Radiobutton(row4, text='控制台', value=1, variable=self.iv_default)
        self.rb_default2 = tk.Radiobutton(row4, text='群消息', value=2, variable=self.iv_default)
        self.rb_default_Label.grid(row=2, column=0, sticky='E')
        self.rb_default1.grid(row=4, column=1, sticky='W')
        self.rb_default2.grid(row=4, column=2, sticky='W')
        if content[3] == '控制台':
            self.rb_default1.select()
        elif content[3] == '群消息':
            self.rb_default2.select()


        # 第六行
        row6 = tk.Frame(ms)
        row6.pack(fill="x")
        tk.Button(row6, text=PLP['EditRegular.Save'], command=self.ok).pack(side=tk.LEFT)
        tk.Button(row6, text=PLP['EditRegular.Canel'], command=self.cancel).pack(side=tk.RIGHT)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        
    def on_closing(self):
        if mBox.askyesno(PLP['EditRegular.Ask.title'],PLP['EditRegular.Ask.message']):
            self.ok()
        else:
            self.cancel()

        
    def ok(self):
        conn = sq.connect('data/regular.db')
        c = conn.cursor()
        #正则
        regular = self.path.get()
        #执行
        run = self.file.get()
        #权限
        if self.autostatus.get() == 1:
            admin = '管理员'
        else:
            admin = ''
        #捕获
        if self.iv_default.get() == 1:
            find = '控制台'
        else:
            find = '群消息'
        
        if self.tf:
            #修改原文
            c.execute(
                'UPDATE interactive set 正则="%s",捕获="%s",权限="%s",执行="%s" where rowid=%i'
                % (regular,find,admin,run,self.content[4]+2)
            )
            conn.commit()
        else:
            #提交新的正则
            c.execute("INSERT INTO interactive (正则,捕获,权限,执行) \
            VALUES ('%s','%s','%s','%s')" % (regular,find,admin,run))
        conn.commit()
        conn.close()
        import Library.Tool as tool
        tool.update()
        self.destroy() # 销毁窗口
        
    def cancel(self):
        self.destroy()

# 弹窗
class PopupDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__()
        self.title('Phsebot - '+PLP['EditConfig.title'])
        
        self.parent = parent # 显式地保留父窗口
        #self.iconbitmap(r'Library/Images/bot.ico')
        self.geometry('400x205')
        self.resizable(0,0)
        ms = ttk.LabelFrame(self, text=PLP['EditConfig.frame'],width=9,height=10)
        ms.grid(column=0, row=0, padx=7, pady=4)
        
        # 第一行（两列）
        row1 = tk.Frame(ms)
        row1.pack(fill="x")
        tk.Label(row1, text=PLP['EditConfig.EditPath'], width=10).pack(side=tk.LEFT,pady=4)
        self.path = tk.StringVar()
        self.path.set(config['ServerPath'])
        path = tk.Entry(row1, textvariable=self.path, width=42)
        path.pack(side=tk.LEFT)
        
        # 第二行
        row2 = tk.Frame(ms)
        row2.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row2, text=PLP['EditConfig.EditFile'], width=10).pack(side=tk.LEFT,pady=4)
        self.file = tk.StringVar()
        self.file.set(config['ServerCmd'])
        file = tk.Entry(row2, textvariable=self.file, width=42)
        file.pack(side=tk.LEFT)

        # 第三行
        row3 = tk.Frame(ms)
        row3.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row3, text=PLP['EditConfig.AdminList'], width=10).pack(side=tk.LEFT,pady=4)
        self.admin = tk.StringVar()
        admins = ''
        for i in config['Admin']:
            if admins == '':
                admins += str(i)
            else:
                admins += '|'+str(i)
        self.admin.set(admins)
        admin = tk.Entry(row3, textvariable=self.admin, width=42)
        admin.pack(side=tk.LEFT)

        # 第四行
        row4 = tk.Frame(ms)
        row4.pack(fill="x", ipadx=1, ipady=1)
        tk.Label(row4, text=PLP['EditConfig.Group'], width=10).pack(side=tk.LEFT,pady=4)
        self.group = tk.StringVar()
        groups = ''
        for i in config['Group']:
            if groups == '':
                groups += str(i)
            else:
                groups += '|'+str(i)
        self.group.set(groups)
        group = tk.Entry(row4, textvariable=self.group, width=42)
        group.pack(side=tk.LEFT)

        #第五行
        row5 = tk.Frame(ms)
        row5.pack(fill="x")
        self.autostatus=tk.IntVar()
        self.auto = tk.Checkbutton(row5, text=PLP['EditConfig.Restart'],variable=self.autostatus)
        if config['AutoRestart']:
            self.auto.select()
        self.auto.pack(side=tk.LEFT)
        
        # 第六行
        row6 = tk.Frame(ms)
        row6.pack(fill="x")
        tk.Button(row6, text=PLP['EditConfig.Save'], command=self.ok).pack(side=tk.LEFT)
        tk.Button(row6, text=PLP['EditConfig.Canel'], command=self.cancel).pack(side=tk.RIGHT)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        
    def on_closing(self):
        if mBox.askyesno(PLP['EditConfig.Ask'],PLP['EditConfig.Message']):
            self.ok()
        else:
            self.cancel()

        
    def ok(self):
        # 显式地更改父窗口参数

        #文件
        config['ServerCmd'] = self.file.get()

        #路径
        config['ServerPath'] = self.path.get()

        #管理员列表
        admins = []
        for i in self.admin.get().split('|'):
            admins.append(int(i))
        config['Admin'] = admins

        #群组列表
        groups = []
        for i in self.group.get().split('|'):
            groups.append(int(i))
        config['Group'] = groups

        #自动重启
        auto = False
        if self.autostatus.get() == 1:
            auto = True
        else:
            auto = False
        config['AutoRestart'] = auto

        #写入文件
        with open('data/config.yml','w') as f:
            y = yaml.dump(config)
            f.write(y)

        
        #写入bat
        with open('Library\index.bat','w') as f:
            run = '''@echo off
cd "%s"
%s'''
            f.write(run % (config['ServerPath'],config['ServerCmd']))
        
        self.destroy() # 销毁窗口
        
    def cancel(self):
        self.destroy()
#此文件为Plugin加载必要文件，请勿删除


import yaml
import os
def file_name_listdir(file_dir):
    l = []
    for files in os.listdir(file_dir):  # 不仅仅是文件，当前目录下的文件夹也会被认为遍历到
        if '.py' in files or '.pyd' in files or '.pyc' in files:
            if files != '__init__.py':
                l.append(files.replace('.py','').replace('.pyd','').replace('.pyc',''))
    return l

loadlist = file_name_listdir("./Plugin")
__all__ = loadlist
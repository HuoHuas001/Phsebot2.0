@echo off
title Phsebot控制台 - dev0.0.1
echo 正在安装依赖库
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo 安装完成正在启动
python index.py
pause
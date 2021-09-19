import tkinter as tk
import tkinter.font as tf
from datetime import datetime
from json import JSONDecodeError
from tkinter import *
from tkinter import Menu, Spinbox
from tkinter import messagebox as mBox
from tkinter import scrolledtext, ttk
from tkinter.constants import END

from main import *
from Library.Libs.basic import read_file

config = read_file('data/config.yml')
Language = read_file('data/Language.yml')
cron = read_file('data/Cron.json')
NoOut = read_file('data/NoOut.yml')
PLP = read_file('Library/Language/'+config['LangPack']+'.yml')
num = 0
BotVersion = '1.6-Beta'
HotFix = True

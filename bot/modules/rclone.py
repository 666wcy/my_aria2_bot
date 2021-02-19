import os
import time
import telebot
from telebot import types
import subprocess
import sys

Telegram_bot_api=os.environ.get('Telegram_bot_api')
bot = telebot.TeleBot(Telegram_bot_api)

def run_rclonecopy(onedir,twodir,message):

    name=message.chat.id
    shell=f"rclone copy {onedir} {twodir}  -v --stats-one-line --stats=5s --log-file=\"{name}.log\" "

    info=bot.send_message(chat_id=message.chat.id,text=shell,parse_mode='Markdown')
    print(shell)
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)
    # 实时输出
    temp_text=None
    while True:
        time.sleep(10)
        fname = f'{name}.log'
        with open(fname, 'r') as f:  #打开文件
            try:
                lines = f.readlines() #读取所有行

                for a in range(-1,-10,-1):
                    last_line = lines[a] #取最后一行
                    if last_line !="\n":
                        break

                print (f"上传中\n{last_line}")
                if temp_text != last_line:

                    bot.edit_message_text(text=f"rclone运行中\n{last_line}",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
                    temp_text = last_line
                f.close()

            except Exception as e:
                print(e)
                f.close()
                continue

        if subprocess.Popen.poll(cmd) == 0:  # 判断子进程是否结束
            print("上传结束")
            bot.send_message(text=f"rclone运行结束",chat_id=info.chat.id)
            os.remove(f"{name}.log")
            return

    return cmd.returncode
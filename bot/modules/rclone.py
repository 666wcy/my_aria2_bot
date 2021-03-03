import os
import time
import telebot
import subprocess
import sys
import re

Telegram_bot_api=os.environ.get('Telegram_bot_api')
bot = telebot.TeleBot(Telegram_bot_api)

def run_rclonecopy(onedir,twodir,message):

    name=f"{str(message.message_id)}_{str(message.chat.id)}"
    shell=f"rclone copy {onedir} {twodir}  -v --stats-one-line --stats=3s --log-file=\"{name}.log\" "
    print(shell)
    sys.stdout.flush()
    info=bot.send_message(chat_id=message.chat.id,text=shell)

    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)
    # 实时输出
    temp_text=None
    while True:
        time.sleep(6)
        fname = f'{name}.log'
        with open(fname, 'r') as f:  #打开文件
            try:
                lines = f.readlines() #读取所有行

                for a in range(-1,-10,-1):
                    last_line = lines[a] #取最后一行
                    if last_line !="\n":
                        break

                print (f"上传中\n{last_line}")
                sys.stdout.flush()
                if temp_text != last_line and "ETA" in last_line:
                    log_time,file_part,upload_Progress,upload_speed,part_time=re.findall("(.*?)INFO.*?(\d.*?),.*?(\d+%),.*?(\d.*?s).*?ETA.*?(\d.*?s)",last_line , re.S)[0]
                    text=f"源地址:`{onedir}`\n" \
                         f"目标地址:`{twodir}`\n" \
                         f"更新时间：`{log_time}`\n" \
                     f"传输部分：`{file_part}`\n" \
                     f"传输进度：`{upload_Progress}`\n" \
                     f"传输速度：`{upload_speed}`\n" \
                     f"剩余时间:`{part_time}`"
                    bot.edit_message_text(text=text,chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
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
import aria2p
import os
import time
import telebot
from telebot import types
import subprocess
import sys
import datetime
import pytz
import re
tz = pytz.timezone('Asia/Shanghai') #东八区
Telegram_bot_api=os.environ.get('Telegram_bot_api')
Aria2_host=os.environ.get('Aria2_host')
Aria2_port=os.environ.get('PORT')
Aria2_secret=os.environ.get('Aria2_secret')
bot = telebot.TeleBot(Telegram_bot_api)
aria2 = aria2p.API(
    aria2p.Client(
        host=Aria2_host,
        port=int(Aria2_port),
        secret=Aria2_secret
    )
)

def get_free_space_mb():
    result=os.statvfs('/root/')
    block_size=result.f_frsize
    total_blocks=result.f_blocks
    free_blocks=result.f_bfree
    giga=1000*1000*1000
    total_size=total_blocks*block_size/giga
    free_size=free_blocks*block_size/giga
    print('total_size = %s' % int(total_size))
    print('free_size = %s' % free_size)
    return int(free_size)

def progessbar(new, tot):
    """Builds progressbar
    Args:
        new: current progress
        tot: total length of the download
    Returns:
        progressbar as a string of length 20
    """
    length = 20
    progress = int(round(length * new / float(tot)))
    percent = round(new/float(tot) * 100.0, 1)
    bar = '=' * progress + '-' * (length - progress)
    return '[%s] %s %s\r' % (bar, percent, '%')

def hum_convert(value):
    value=float(value)
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size

def run_rclone(dir,title,info,file_num):

    Rclone_remote=os.environ.get('Remote')
    Upload=os.environ.get('Upload')
    upload_data = datetime.datetime.fromtimestamp(int(time.time()),tz).strftime('%Y年%m月%d日')
    name=f"{str(info.message_id)}_{str(info.chat.id)}"
    if int(file_num)==1:
        shell=f"rclone copy \"{dir}\" \"{Rclone_remote}:{Upload}/{upload_data}\"  -v --stats-one-line --stats=1s --log-file=\"{name}.log\" "
    else:
        shell=f"rclone copy \"{dir}\" \"{Rclone_remote}:{Upload}/{upload_data}/{title}\"  -v --stats-one-line --stats=1s --log-file=\"{name}.log\" "
    print(shell)
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=subprocess.PIPE, universal_newlines=True, shell=True, bufsize=1)
    # 实时输出
    temp_text=None
    while True:
        time.sleep(1)
        fname = f'{name}.log'
        with open(fname, 'r') as f:  #打开文件
            try:
                lines = f.readlines() #读取所有行

                for a in range(-1,-10,-1):
                    last_line = lines[a] #取最后一行
                    if last_line !="\n":
                        break

                print (f"上传中\n{last_line}")
                if temp_text != last_line and "ETA" in last_line:
                    log_time,file_part,upload_Progress,upload_speed,part_time=re.findall("(.*?)INFO.*?(\d.*?),.*?(\d+%),.*?(\d.*?s).*?ETA.*?(\d.*?s)",last_line , re.S)[0]
                    text=f"{title}\n" \
                         f"更新时间：`{log_time}`\n" \
                         f"上传部分：`{file_part}`\n" \
                         f"上传进度：`{upload_Progress}`\n" \
                         f"上传速度：`{upload_speed}`\n" \
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
            bot.send_message(text=f"{title}\n上传结束",chat_id=info.chat.id)
            os.remove(f"{name}.log")
            return

    return


def the_download(url,message):
    os.system("df -lh")
    try:
        download = aria2.add_magnet(url)
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            bot.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='Markdown')
            return None
    prevmessagemag = None
    info=bot.send_message(chat_id=message.chat.id,text="Downloading",parse_mode='Markdown')
    while download.is_active:
        try:
            download.update()
            print("Downloading metadata")
            bot.edit_message_text(text="Downloading metadata",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
            barop = progessbar(download.completed_length,download.total_length)

            updateText = f"Downloading \n" \
                         f"'{download.name}'\n" \
                         f"Progress : {hum_convert(download.completed_length)}/{hum_convert(download.total_length)} \n" \
                         f"Peers:{download.connections}\n" \
                         f"Speed {hum_convert(download.download_speed)}/s\n" \
                         f"{barop}\n" \
                         f"Free:{get_free_space_mb()}GB"
            if prevmessagemag != updateText:
                print(updateText)
                bot.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
                prevmessagemag = updateText
            time.sleep(2)
        except:
            print("Metadata download problem/Flood Control Measures!")
            bot.edit_message_text(text="Metadata download problem/Flood Control Measures!",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
            try:
                download.update()
            except Exception as e:
                if (str(e).endswith("is not found")):
                    print("Metadata Cancelled/Failed")
                    print("Metadata couldn't be downloaded")
                    bot.edit_message_text(text="Metadata couldn't be downloaded",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
                    return None
            time.sleep(2)
    time.sleep(2)
    match = str(download.followed_by_ids[0])
    downloads = aria2.get_downloads()
    currdownload = None
    for download in downloads:
        if download.gid == match:
            currdownload = download
            break
    print("Download complete")

    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton(f"Resume", callback_data=f"Resume {currdownload.gid}"),
               types.InlineKeyboardButton(f"Pause", callback_data=f"Pause {currdownload.gid}"),
               types.InlineKeyboardButton(f"Remove", callback_data=f"Remove {currdownload.gid}"))

    bot.edit_message_text(text="Download complete",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown', reply_markup=markup)
    prevmessage = None

    while currdownload.is_active or not currdownload.is_complete:

        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("Magnet Deleted")
                print("Magnet download was removed")
                bot.edit_message_text(text="Magnet download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
                break
            print(e)
            print("Issue in downloading!")

        if currdownload.status == 'removed':
            print("Magnet was cancelled")
            print("Magnet download was cancelled")
            bot.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
            break

        if currdownload.status == 'error':
            print("Mirror had an error")
            currdownload.remove(force=True, files=True)
            print("Magnet failed to resume/download!\nRun /cancel once and try again.")
            bot.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown', reply_markup=markup)
            break

        print(f"Magnet Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"Downloading \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"Free:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    bot.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown', reply_markup=markup)
                    prevmessage = updateText
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"Downloading \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Peers:{currdownload.connections}\n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"Free:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    bot.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown', reply_markup=markup)
                    prevmessage = updateText
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)
        time.sleep(2)

        time.sleep(1)

    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            files_num=int(len(currdownload.files))
            run_rclone(file_dir,currdownload.name,info=info,file_num=files_num)
            currdownload.remove(force=True,files=True)

        except Exception as e:
            print(e)
            print("Upload Issue!")
    return None

def http_download(url,message):
    try:
        currdownload = aria2.add_uris([url])
    except Exception as e:
        print(e)
        if (str(e).endswith("No URI to download.")):
            print("No link provided!")
            bot.send_message(chat_id=message.chat.id,text="No link provided!",parse_mode='Markdown')
            return None

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"Resume", callback_data=f"Resume {currdownload.gid}"),
               types.InlineKeyboardButton(f"Pause", callback_data=f"Pause {currdownload.gid}"),
               types.InlineKeyboardButton(f"Remove", callback_data=f"Remove {currdownload.gid}"))
    info=bot.send_message(chat_id=message.chat.id,text="Downloading",parse_mode='Markdown')
    prevmessage=None
    while currdownload.is_active or not currdownload.is_complete:

        try:
            currdownload.update()
        except Exception as e:
            if (str(e).endswith("is not found")):
                print("url Deleted")
                print("url download was removed")
                bot.edit_message_text(text="url download was removed",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
                break
            print(e)
            print("url in downloading!")

        if currdownload.status == 'removed':
            print("url was cancelled")
            print("url download was cancelled")
            bot.edit_message_text(text="Magnet download was cancelled",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
            break

        if currdownload.status == 'error':
            print("url had an error")
            currdownload.remove(force=True, files=True)
            print("url failed to resume/download!.")
            bot.edit_message_text(text="Magnet failed to resume/download!\nRun /cancel once and try again.",chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown', reply_markup=markup)
            break

        print(f"url Status? {currdownload.status}")

        if currdownload.status == "active":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"Downloading \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"Free:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    bot.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown', reply_markup=markup)
                    prevmessage = updateText
                time.sleep(2)
            except Exception as e:
                if (str(e).endswith("is not found")):
                    break
                print(e)
                print("Issue in downloading!")
                time.sleep(2)
        elif currdownload.status == "paused":
            try:
                currdownload.update()
                barop = progessbar(currdownload.completed_length,currdownload.total_length)

                updateText = f"Downloading \n" \
                             f"'{currdownload.name}'\n" \
                             f"Progress : {hum_convert(currdownload.completed_length)}/{hum_convert(currdownload.total_length)} \n" \
                             f"Speed {hum_convert(currdownload.download_speed)}/s\n" \
                             f"{barop}\n" \
                             f"Free:{get_free_space_mb()}GB"

                if prevmessage != updateText:
                    print(f"更新状态\n{updateText}")
                    bot.edit_message_text(text=updateText,chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown', reply_markup=markup)
                    prevmessage = updateText
                time.sleep(2)
            except Exception as e:
                print(e)
                print("Download Paused Flood")
                time.sleep(2)
        time.sleep(2)

        time.sleep(1)
    if currdownload.is_complete:
        print(currdownload.name)
        try:
            print("开始上传")
            file_dir=f"{currdownload.dir}/{currdownload.name}"
            run_rclone(file_dir,currdownload.name,info=info,file_num=1)
            currdownload.remove(force=True,files=True)

        except Exception as e:
            print(e)
            print("Upload Issue!")
    return None
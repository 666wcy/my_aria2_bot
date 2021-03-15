import os
import sys
import requests
import zipfile
import time
import re
import subprocess
from modules.creat_config import *
session = requests.Session()
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 5.8; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36",
    'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
}


def run_upload_rclone(dir,title,info,file_num):

    Rclone_remote=os.environ.get('Remote')
    Upload=os.environ.get('Upload')

    name=f"{str(info.message_id)}_{str(info.chat.id)}"
    if int(file_num)==1:
        shell=f"rclone copy \"{dir}\" \"{Rclone_remote}:{Upload}\"  -v --stats-one-line --stats=1s --log-file=\"{name}.log\" "
    else:
        shell=f"rclone copy \"{dir}\" \"{Rclone_remote}:{Upload}/{title}\"  -v --stats-one-line --stats=1s --log-file=\"{name}.log\" "
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
                sys.stdout.flush()
                if temp_text != last_line and "ETA" in last_line:
                    log_time,file_part,upload_Progress,upload_speed,part_time=re.findall("(.*?)INFO.*?(\d.*?),.*?(\d+%),.*?(\d.*?s).*?ETA.*?(\d.*?)",last_line , re.S)[0]
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

# 下载模块
def download(url, title,author, id):
    global session,header
    path = author
    if not os.path.exists(path):
        os.mkdir(path)
    title = str(title)
    id = str(id)
    title = eval(repr(title).replace('\\', ''))
    title = eval(repr(title).replace('/', ''))
    title = eval(repr(title).replace('?', ''))
    title = eval(repr(title).replace('*', ''))
    title = eval(repr(title).replace('・', ''))
    title = eval(repr(title).replace('！', ''))
    title = eval(repr(title).replace('|', ''))
    title = eval(repr(title).replace(' ', ''))
    r = session.get(url, headers=header)

    try:
        if "jpg" in url:
            with open(f'{author}\\{title}.jpg', 'wb') as f:
                f.write(r.content)
            print("下载成功:" + title )

            return True
        elif "png" in url:
            with open(f'{author}\\{title}.png', 'wb') as f:
                f.write(r.content)
            print( "下载成功:" + title )
            return True

    except Exception as e:
        print("下载失败:" + title )
        print(e)
        return False


def zip_ya(start_dir):
    start_dir = start_dir  # 要压缩的文件夹路径
    file_news = start_dir + '.zip'  # 压缩后文件夹的名字
    z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)
    for dir_path, dir_names, file_names in os.walk(start_dir):
        f_path = dir_path.replace(start_dir, '')  # 这一句很重要，不replace的话，就从根目录开始复制
        f_path = f_path and f_path + os.sep or ''  # 实现当前文件夹以及包含的所有文件的压缩
        for filename in file_names:
            z.write(os.path.join(dir_path, filename), f_path + filename)
    z.close()
    return file_news

def del_path(path):
    if not os.path.exists(path):
        return
    if os.path.isfile(path):
        os.remove(path)
        # print( 'delete file %s' % path)
    else:
        items = os.listdir(path)
        for f in items:
            c_path = os.path.join(path, f)
            if os.path.isdir(c_path):
                del_path(c_path)
            else:
                os.remove(c_path)
                # print('delete file %s' % c_path)
        os.rmdir(path)
        # print( 'delete dir %s' % path)

@bot.message_handler(commands=['pixivuser'],func=lambda message:str(message.chat.id) == str(Telegram_user_id))
def start_download_pixiv(message):
    try:
        keywords = str(message.text)
        keywords = keywords.replace(f"/pixivuser ", "")
        print(keywords)
        artistid = int(keywords)
        idurl = f"https://www.pixiv.net/ajax/user/{artistid}/profile/all"
        html2 = requests.get(idurl, headers=header)


        illusts=html2.json()['body']['illusts']
        info=bot.send_message(chat_id=message.chat.id,text="开始下载")
        img_num=len(illusts)
        img_su_num=0
        img_er_num=0
        for id in illusts:
            print(id)
            info_url = f"https://www.pixiv.net/touch/ajax/illust/details?illust_id={id}"
            ht = requests.get(url=info_url, headers=header)
            info_json=ht.json()
            img_url=info_json['body']['illust_details']['url_big']
            title=info_json['body']['illust_details']['meta']['title']+f"id-{id}"

            #.author_details.profile_img.main
            author=f"{info_json['body']['author_details']['user_name']}"

            title=str(title).replace("#","").replace(author,"").replace(":","").replace("@","").replace("/","")
            author=str(author).replace(":","").replace("@","").replace("/","")
            print(img_url)

            download_result=download(url=img_url,title=title,author=author,id=id)
            if download_result==True:
                img_su_num=img_su_num+1
            else:
                img_er_num=img_er_num+1

            text=f"Author:{author}\n" \
                 f"Number of pictures:{img_num}\n" \
                 f"Number of successes:{img_su_num}\n" \
                 f"Number of errors:{img_er_num}\n" \
                 f"Progessbar:\n{progessbar(img_su_num,img_num)}"
            bot.edit_message_text(text=text,chat_id=info.chat.id,message_id=info.message_id,parse_mode='Markdown')
        print("开始压缩")
        sys.stdout.flush()
        name = zip_ya(keywords)
        print(name)
        print("压缩完成，开始上传")
        del_path(keywords)
        try:
            run_upload_rclone(dir=name,title=name,info=info,file_num=1)
            print("uploading")
        except Exception as e:
            print(f"{e}")
            sys.stdout.flush()
            bot.send_message(message.chat_id, text="文件上传失败")
        bot.delete_message(message.chat_id, message.message_id)
        os.system("rm '" + name + "'")


    except Exception as e:
        print(e)
        sys.stdout.flush()
        return



import psutil
import os
from apscheduler.schedulers.background import BackgroundScheduler
#import config
os.environ['Aria2_host']="http://127.0.0.1"
from modules.creat_config import *

from modules.picacg import *

from modules.new_download import *

from modules.resume import *

from modules.pause import *

from modules.delete import *

from modules.rclone import *


'''command = [BotCommand("status","查看所有种子状态"),
           BotCommand("down", "后接磁力链接，下载种子"),
           BotCommand("resume", "后接hash，继续种子任务"),
           BotCommand("pause", "后接hash，暂停种子任务"),
           BotCommand("del", "后接hash，删除种子")]
print(bot.set_my_commands(commands=command))'''


# Press the green button in the gutter to run the script.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
def new_clock():
    try:
        downloads = aria2.get_downloads()
        for download in downloads:
            if download.status=="active":
                print(download.name, download.download_speed)
                print("任务正在进行,保持唤醒")
                print(requests.get(url=f"https://{app_title}.herokuapp.com/"))
                sys.stdout.flush()
                break
        else:
            print("无正在下载任务")
            sys.stdout.flush()
    except Exception as e:
            print(f"new_clock error :{e}")


def second_clock():
    try:
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name'])
            except psutil.NoSuchProcess:
                pass
            else:
                if "rclone" in str(pinfo['name']):
                    print("rclone 正在上传")
                    print(requests.get(url=f"https://{app_title}.herokuapp.com/"))
                    sys.stdout.flush()
                    break
        else:
            print("rclone 不在运行")
            sys.stdout.flush()
    except Exception as e:
        print(f"second_clock :{e}")

def start_bot():
    #scheduler = BlockingScheduler()
    scheduler = BackgroundScheduler()

    scheduler.add_job(new_clock, "interval", seconds=60)
    scheduler.add_job(second_clock, "interval", seconds=60)
    print("开启监控")

    sys.stdout.flush()
    scheduler.start()
    bot.send_message(chat_id=Telegram_user_id,text="bot已上线")
    # Load next_step_handlers from save file (default "./.handlers-saves/step.save")
    # WARNING It will work only if enable_save_next_step_handlers was called!
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(e)
            time.sleep(20)


if __name__ == '__main__':
    start_bot()

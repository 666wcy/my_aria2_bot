from modules.creat_config import *

@bot.callback_query_handler(func=lambda call: "Pause" in call.data)
def add_pause(call):
    try:
        print(call)
        caption = str(call.message.text)
        print(caption)
        print(call.data)
        key_data=str(call.data).replace("Pause ","")
        print(key_data)
        text=file_pause(key_data)
        bot.answer_callback_query(callback_query_id=call.id,text=text,cache_time=3)
    except Exception as e:
        print(f"Pause :{e}")

def file_pause(gid):
    print("暂停任务")
    try:
        the_pause = aria2.get_download(gid=str(gid))
        torrent_name=the_pause.name
        resume_result=the_pause.pause()
        if resume_result==True:
            print(f"{torrent_name}\n暂停成功")
            return f"暂停成功"
        else:
            print(f"{torrent_name}\n暂停失败")
            return f"暂停失败"
    except Exception as e:
        print (e)
        return f"\n暂停失败：{e}"
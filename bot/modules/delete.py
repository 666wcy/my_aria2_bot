from modules.creat_config import *

@bot.callback_query_handler(func=lambda call: "Remove" in call.data)
def add_del(call):
    try:
        print(call)
        caption = str(call.message.text)
        print(caption)
        print(call.data)
        key_data=str(call.data).replace("Remove ","")
        print(key_data)
        text=file_del(key_data)
        bot.answer_callback_query(callback_query_id=call.id,text=text,cache_time=3)
    except Exception as e:
        print(f"Remove :{e}")


def file_del(gid):
    print("开始删除")
    try:
        dele = aria2.get_download(gid=str(gid))
        torrent_name=dele.name
        del_result=dele.remove(force=True, files=True)
        if del_result==True:
            print(f"{torrent_name}\n删除成功")
            return f"删除成功"
        else:
            print(f"{torrent_name}\n删除失败")
            return f"删除失败"
    except Exception as e:
        print (e)
        return f"\n删除失败：{e}"
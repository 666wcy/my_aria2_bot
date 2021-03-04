from modules.creat_config import *

def file_resume(gid):
    print("开始任务")
    try:
        the_resume = aria2.get_download(gid=str(gid))
        torrent_name=the_resume.name
        resume_result=the_resume.resume()
        if resume_result==True:
            print(f"{torrent_name}\n开始成功")
            return f"开始成功"
        else:
            print(f"{torrent_name}\n开始失败")
            return f"开始失败"
    except Exception as e:
        print (e)
        return f"\n开始失败：{e}"


@bot.callback_query_handler(func=lambda call: "Resume" in call.data)
def add_resume(call):
    try:
        print(call)
        caption = str(call.message.text)
        print(caption)
        print(call.data)
        key_data=str(call.data).replace("Resume ","")
        print(key_data)
        text=file_resume(key_data)
        bot.answer_callback_query(callback_query_id=call.id,text=text,cache_time=3)
    except Exception as e:
        print(f"Resume :{e}")
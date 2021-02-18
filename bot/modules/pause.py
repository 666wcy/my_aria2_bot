import aria2p
import os
Aria2_host=os.environ.get('Aria2_host')
Aria2_port=os.environ.get('PORT')
Aria2_secret=os.environ.get('Aria2_secret')

aria2 = aria2p.API(
    aria2p.Client(
        host=Aria2_host,
        port=int(Aria2_port),
        secret=Aria2_secret
    )
)

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
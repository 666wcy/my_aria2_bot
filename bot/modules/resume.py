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
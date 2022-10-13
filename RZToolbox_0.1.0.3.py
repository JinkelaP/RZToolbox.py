#%% Made by RZStudio

# 先全给import了
from datetime import datetime
import time
from json.decoder import JSONDecodeError
import json
from unittest.main import main
import requests
import sys  # 传入argv，达到命令行一键
from tkinter import N
import urllib.request
import pandas as pd  # 以下为老三样
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns  # 图表美化
from pathlib import Path


BV2AV_API = 'https://api.bilibili.com/x/web-interface/view'  # ?bvid=
AV2BV_API = 'https://api.bilibili.com/x/web-interface/archive/stat'  # ?aid=
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/80.0.3987.149 Safari/537.36'}


class VideoInfo(object):
    def __init__(self, BVnumber, VideoNameShort='', OutFolder=str(Path(__file__).parent.resolve())) -> None:
        self.bv = BVnumber
        self.alias = VideoNameShort
        self.out = OutFolder
        self.av = self.get_av()

    def __str__(self) -> str: # str、print(self) 输出的一坨史
        return r'''BV号 BV\#: {}
简称 Alias: {}
AV号 AV\#: {}
导出文件夹 Out: {}'''.format(self.bv, self.alias, (self.av if self.av != None else "获取失败 Retrieve failed"), self.out)

    def get_av(self):
        return bv_to_av(self.bv)
    
    def get_filename(self, time=""):
        return r"{}_{}{}".format(self.bv, self.alias, ("_"+time if time != "" else ""))

    def get_path(self, time = '', extension='txt'):
        return self.out + '/' + self.get_filename(time) + '.' + extension

def bv_to_av(bv):
    r = requests.get(BV2AV_API, {'bvid': bv}, headers=HEADER)
    response = decode_json(r)
    try:
        return str(response['data']['aid'])
    except (KeyError, TypeError):
        return None

def decode_json(r):
    try:
        response = r.json()
    except JSONDecodeError:
        # 虽然用的是requests的json方法，但要捕获的这个异常来自json模块
        return -1
    else:
        return response

if __name__ == '__main__':
    print('Made by RZStudio')
    time.sleep(0.5)
    print('欢迎使用RZToolbox 0.1.0.3 Welcome! \n')
    time.sleep(1)

    
    try:  # 尝试读取命令行一键，如果没提供就手动输入
        BVnumber, VideoNameShort = sys.argv[1:3]
    except (IndexError,ValueError) as error:
        print("未检测到一键参数", error)
        BVnumber = input('请填写BV号 Please type the BVID\n') #请填写
        VideoNameShort = input('\n请填写视频简称 Please name your video\n') #请填写视频名字
    
    file_path_folder = input('\n请填写数据保存路径（默认为程序所在路径）\nPlease type path of your folder for saving data\nExample: D:\Works\Videodata\n')
    if file_path_folder == '':
        current_video = VideoInfo(BVnumber, VideoNameShort)
    else:
        current_video = VideoInfo(BVnumber, VideoNameShort, file_path_folder)

    print(current_video)

    #开爬！

    #ipList = ['xxx.xxx.xxx.xx:xx'] #定义多个代理IP的方法，备用
    proxy = {'http':'127.0.0.1:1080'} #妈的，有点问题，修不来

    #随机间隔
    create_time = time.asctime( time.localtime(time.time()) )
    cnt = 0

    try:
        assert current_video.av != None
        dataframes = []
        while True:
            rand_interval = np.abs(np.random.normal(1800, 60))
            localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            proxy_support = urllib.request.ProxyHandler(proxy)
            url = "https://api.bilibili.com/archive_stat/stat?aid={}".format(current_video.av) #设置av号 妈的还得转一次
            #url = "https://www.guaniukanyue.pw"
            param = {} #设置参数，参数是字典
            param = urllib.parse.urlencode(param).encode('utf_8') #将参数以utf-8编码方式来编码
            opener = urllib.request.build_opener(proxy_support)
            opener.addheaders = [("User-Agent", "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1")]
            urllib.request.install_opener(opener)
            
            response = urllib.request.urlopen(url)

            html = response.read() #读取响应的结果
            result = html.decode("utf-8") #按照utf-8编码来进行解码
            if result != "":
                cnt += 1

            # pandas大法
            data = json.loads(result)['data']
            data['time'] = localtime
            data = pd.DataFrame(data, index=[0])
            data['time'] = data['time'].astype('datetime64')
            # 将time列置顶
            cols = data.columns.tolist()
            data = data[[cols[-1]] + cols[:-1]]
            dataframes.append(data)

            print("\n第%s次获取信息 " %cnt)
            # print(localtime)
            # print(result)
            print(data.to_string(index=False))

            time.sleep(rand_interval)
    except KeyboardInterrupt: # 关播了
        # 生成dataframe
        df = pd.concat(dataframes, ignore_index=True)


        # 各种导
        df.to_json(current_video.get_path('', 'json'), orient='records')
        df.to_csv(current_video.get_path('', 'csv'),index=False)
        df.to_excel(current_video.get_path('', 'xlsx'),index=False)

        # 新建两行
        df['view/like'] = df['view'] / df['like']
        df['view_trend'] = df['view'].diff()
        # 画图
        fig = plt.figure()  # 新建画布
        sns.set_theme('paper')  # 选择主题
        sns.set_style("whitegrid")

        # 加两个图 （211 = 2*1排列第1个图，下同）
        ax0 = fig.add_subplot(211) 
        ax0.set_title("View / Like")
        ax0.set_xlabel("Timeline")
        ax0.set_ylabel("Ratio")
        ax0.plot(df['time'], df['view/like'])

        ax1 = fig.add_subplot(212)
        ax1.set_title("Trend per 30min(?)")
        ax1.set_xlabel("Timeline")
        ax1.set_ylabel("Views")
        ax1.plot(df['time'], df['view_trend'])

        print("\n最后10条导出数据:", df.tail(10))
        print("\n对面关播了，感谢使用 Gonna say goodbye")
        plt.show()
    except AssertionError: # 没AV号
        print("没AV号你爬你emoji呢")
#————————————————

# 不敢碰11111

#20220207_需要修改的地方: 用V2ray进guaniukanyue代理（有问题），时间添加随机量（完成），每隔?分钟将文件保存成txt （DONE!）
#20220208: 代理问题，在线人数api寻找

#V0.1.0.1 更新：生成一个带时间的文件与一个纯json文件，为未来json处理做准备
#V0.1 A stable version
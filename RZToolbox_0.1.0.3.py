# Made by RZStudio
print('Made by RZStudio')
print('欢迎使用RZToolbox 0.1.0.3 Welcome! \n')

#---------------------------------------------------------------------------------------------------------


BVnumber = input('请填写BV号 Please type the BVID\n') #请填写
VideoNameShort = input('\n请填写视频简称 Please name your video\n') #请填写视频名字
file_path_folder = input('\n请填写数据保存路径\nPlease type path of your folder for saving data\nExample: D:\Works\Videodata\n')
file_path =  r"{}\{}_{}.txt".format(file_path_folder,BVnumber,VideoNameShort) #txt保存位置
file_path_json = r"{}\{}_{}_json.txt".format(file_path_folder,BVnumber,VideoNameShort) #txt保存位置

#---------------------------------------

print('\n开始转换BV号 Start BVID transformation...')

#----------------------------------------------------------------------------------------------------------
#因为所知的API太垃圾，所以先bv转av


from json.decoder import JSONDecodeError
import requests

BV2AV_API = 'https://api.bilibili.com/x/web-interface/view'  # ?bvid=
AV2BV_API = 'https://api.bilibili.com/x/web-interface/archive/stat'  # ?aid=
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/80.0.3987.149 Safari/537.36'}



def bv_to_av(bv):
    r = requests.get(BV2AV_API, {'bvid': bv}, headers=HEADER)
    response = decode_json(r)
    try:
        return str(response['data']['aid'])
    except (KeyError, TypeError):
        return '获取av号失败'

def decode_json(r):
    try:
        response = r.json()
    except JSONDecodeError:
        # 虽然用的是requests的json方法，但要捕获的这个异常来自json模块
        return -1
    else:
        return response


print('对应av号转换成功！:' + bv_to_av(BVnumber))

AVnumber = bv_to_av(BVnumber)


#接下来是爬虫部分

import time
from tkinter import N
import urllib.request
import random

localtime = time.asctime( time.localtime(time.time()) )

#ipList = ['119.6.144.73:81', '183.203.208.166:8118', '111.1.32.28:81'] #定义多个代理IP的方法，备用
proxy = {'http':'127.0.0.1:1080'} #妈的，有点问题，修不来

cnt = 0

GapBtw = 1800+random.randint(-60,60) #间隔x+random.randint(a,b) 秒钟，使用random.randint增加随机量

#每一次记录的开头
f = open(file_path,mode='a',encoding='utf-8')
f.write("本次记录开始_开始时间是 ")
f.write(localtime)
f.write(" 祝发达~")
f.write('\r\n')
f.close()
#----------------------------------------------


#开头结束


#隐藏自己爬虫的身份的第一种策略是设置访问周期，使得程序更像是人为访问的
while True: #每隔 x+random.randint(-120,120) 秒钟访问一次指定视频的数据API
    
    localtimeB = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    proxy_support = urllib.request.ProxyHandler(proxy)
    url = "https://api.bilibili.com/archive_stat/stat?aid={}".format(AVnumber) #设置av号 妈的还得转一次
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
    print("第%s次获取信息 " %cnt)
    print(localtimeB)
    print(result)

    
    f = open(file_path,mode='a',encoding='utf-8')   #打开文件，若文件不存在系统自动创建。 
                                    #参数name 文件名，mode 模式。
                                    #w 只能操作写入  r 只能读取   a 向文件追加
                                    #w+ 可读可写   r+可读可写    a+可读可追加
                                    #wb+写入进制数据
                                    #w模式打开文件，如果文件中有数据，再次写入内容，会把原来的覆盖掉     
    
    f.write(localtimeB + '\n' + result + '\n')
    
                                    #writelines()函数 会将列表中的字符串写入文件中，但不会自动换行，如果需要换行，手动添加换行符
                                                    #参数 必须是一个只存放字符串的列
    f.close()              #关闭文件 

    f = open(file_path_json,mode='a',encoding='utf-8')   #打开文件，若文件不存在系统自动创建。 
                                    #参数name 文件名，mode 模式。
                                    #w 只能操作写入  r 只能读取   a 向文件追加
                                    #w+ 可读可写   r+可读可写    a+可读可追加
                                    #wb+写入进制数据
                                    #w模式打开文件，如果文件中有数据，再次写入内容，会把原来的覆盖掉     
    
    from jsonpath import jsonpath
    import json
    # 如果取不到将返回False # 返回列表，如果取不到将返回False
    
    resultdict = json.loads(result)
    result_data = jsonpath(resultdict, '$..data') 
    result_data_2 =  str(result_data).replace("'","\"").replace(r"\n","").strip(str([])).strip(str({}))
    print(result_data_2)
    
    f.write(',')
    f.write('\r')
    f.write("{")
    f.write('"time": "{}", '.format(localtimeB))
    f.write(result_data_2) # write 写入 
    f.write("}")
    
    f.close()              #关闭文件 


    time.sleep(GapBtw) #程序睡眠 间隔时间参照Gap的设置
#————————————————


#20220207_需要修改的地方: 用V2ray进guaniukanyue代理（有问题），时间添加随机量（完成），每隔?分钟将文件保存成txt （DONE!）
#20220208: 代理问题，在线人数api寻找

#V0.1.0.1 更新：生成一个带时间的文件与一个纯json文件，为未来json处理做准备
#V0.1 A stable version
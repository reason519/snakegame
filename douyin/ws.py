import asyncio
import json
from jsonpath import jsonpath
import websockets
import pyttsx3
import time
from douyin import util
import threading
import pyautogui
from collections import deque

engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[1].id)

#发礼物一定要说感谢，信息存入队列中
present_deque=deque()
flag=True

# 1用户发言#2用户点赞#3用户入房#4关注主播#5用户礼物#6人数统计
'''
str(fid[0:2])=="403": #字符串提取方便自定义命令
'''


def msg(data):
    global close
    load_json_data = json.loads(data.get("Data"))
    用户名 = jsonpath(load_json_data, '$.User.Nickname')
    用户等级 = jsonpath(load_json_data, '$.User.PayLevel')
    粉丝团 = jsonpath(load_json_data, '$.User.FansClub.ClubName')
    用户发言 = jsonpath(load_json_data, '$.Content')
    # if 用户发言[0] == "#关闭":
    #     close = False
    # else:
    #     # print(用户名[0])
    #     # print(用户等级[0])
    #     # print(用户发言[0])
    #
    #     engine.say( 用户发言[0])
    #     engine.runAndWait()
    if not len(present_deque):
        pass

def praise(data):  # type2
    load_json_data = json.loads(data.get("Data"))
    用户点赞 = jsonpath(load_json_data, '$.Content')

    # print(用户点赞[0].split())
    # print(用户点赞[0].split()[1][5:].split("，")[0][:-2])
    try:
        # util.color_little_change(conf.color_body,1)
        # util.color_little_change(conf.color_body,
        #         int(用户点赞[0].split()[1][5:].split("，")[0][:-2]))
        # a=用户点赞[0].split()[1][5:].split("，")[0][:-2]
        # if a>5:
        #     for i in range(5):
        #         pyautogui.press("left")
        # else:
        #     pyautogui.press("left")
        for i in range(int(用户点赞[0].split()[1][5:].split("，")[0][:-2])):
            pyautogui.press("left")
    except:
        print("无效点赞")
    print("sssss",len(present_deque))
    # if not len(present_deque):
    #     # if not engine._inLoop:
    #     #
    #     #     engine.say("感谢" + 用户点赞[0].split()[0] + "点赞")
    #     #     engine.runAndWait()
    #     pyttsx3.speak("感谢" + 用户点赞[0].split()[0] )


def welcome(data):  # type3
    load_json_data = json.loads(data.get("Data"))
    用户名 = jsonpath(load_json_data, '$.User.Nickname')
    粉丝团 = jsonpath(load_json_data, '$.User.FansClub.ClubName')
    # if 粉丝团[0] == "Reset":
    #     print("欢迎粉丝:" + 用户名[0])
    # else:
    #     print("欢迎:" + 用户名[0])


def thank(data):  # type5
    load_json_data = json.loads(data.get("Data"))
    粉丝团 = jsonpath(load_json_data, '$.User.FansClub.ClubName')
    用户送礼 = jsonpath(load_json_data, '$.Content')
    # txt1 = txt.replace("主播", "黎公子") #字符串替换功能方便拓展功能
    print(粉丝团)
    print(用户送礼)
    a = 用户送礼[0].split()
    if 粉丝团[0] == "Reset":
        print("感谢老板:" + 用户送礼[0])
        engine.say("感谢老板" + "".join(a[:-1]))
        engine.runAndWait()
        engine.endLoop()
    else:
        present_deque.append(a)




def check(data):  # type6
    load_json_data = json.loads(data.get("Data"))
    房间统计 = jsonpath(load_json_data, '$.Content')
    print(房间统计[0])

def fun(a,t):
    # if engine._inLoop:
    #     engine.endLoop()


    print("up")
    # engine.say("感谢" + a[0] + "送出" + a[-4] + a[-2] + "个,加速" + str(t * int(a[-2])) + "秒")
    # engine.runAndWait()
    pyttsx3.speak("感谢" + a[0] + "送出" + a[-4] + a[-2] + "个,加速" + str(t * int(a[-2])) + "秒")
    flag=True
    pyautogui.press("up")
    # start_time=time.time()
    # while time.time()-start_time<t*int(a[-2]):
    #     pass
    time.sleep(t*int(a[-2]))
    pyautogui.press("down")
    print("down")


def check_json(json_data):
    Token = json_data.get("Type")  # 标签类型
    if Token == 1:  # 1用户发言
        msg(json_data)
    elif Token == 2:  # 2用户点赞
        praise(json_data)
    # elif Token == 3:  # 3用户入房
    #     welcome(json_data)
    # elif Token == 4:  # 感谢关注
    #     print(str(json_data))
    # elif Token == 5:  # 5用户礼物
    #     thank(json_data)
    # elif Token == 6:  # 6人数统计
    #     check(json_data)
    # else:
    #     print(json_data)

def tread_thanks():
        while len(present_deque):
            a = present_deque.popleft()
            if a[-4] == "小心心":
                fun(a, 1)
            elif a[-4] == "大啤酒":
                fun(a, 2)
            elif a[-4] == "棒棒糖":
                fun(a, 10)
            elif a[-4] == "擂鼓助威":
                fun(a, 120)


async def main():
    global close
    # global present_deque
    # threading.Thread(target=tread_thanks).start()

    async with websockets.connect("ws://127.0.0.1:8888/", ping_interval=None) as ws:
        await ws.send("token")
        close = True
        while close is True:
            result = await ws.recv()
            check_json(json.loads(result))


        await ws.close()


close = True
asyncio.run(main())
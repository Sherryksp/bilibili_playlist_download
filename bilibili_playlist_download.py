import os
import re
from moviepy.editor import *
from lxml import etree
import requests
import subprocess

# 模拟浏览器
headers = {
    # Referer 防盗链, 告诉服务器请求链接是从哪里跳转过来
    "Referer":"https://www.bilibili.com/",
    # User-Agent 用户代理, 表示浏览器基本身份信息
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}
# 请求链接 开发者工具搜索https://api.bilibili.com/x/web-interface/wbi/view/detail
url = ''
# 发送请求
response = requests.get(url=url, headers=headers)
# 获取响应json数据 --> 字典数据类型 {}
json_data = response.json()
# 字典取值, 提取信息内容
pages = json_data['data']['View']['ugc_season']['sections'][0]['episodes']
# print(pages)
# for循环遍历, 提取列表里面元素
for page in pages: # page 定义变量名
    # 提取cid
    cid = page['cid']
    #提取playurl
    playurl = 'https://www.bilibili.com/video/' + page['bvid']
    # 提取标题
    title = page['title']
    print(cid, playurl, title)

    response_ = requests.get(playurl, headers=headers)
    str_data = response_.text  # 视频主页的html代码，类型是字符串

    # 使用xpath解析html代码，得到想要的url
    html_obj = etree.HTML(str_data)  # 转换格式类型

    # 使用xpath语法获取数据
    # 取到数据为列表，索引[0]取值取出里面的字符串，即包含纯视频纯音频文件的url字符串
    url_list_str = html_obj.xpath("//script[contains(text(),'window.__playinfo__')]/text()")[0]

    # 使用正则提取纯视频url
    video_url = re.findall(r'"video":\[{"id":\d+,"baseUrl":"(.*?)"', url_list_str)[0]

    # 使用正则提取纯音频url
    audio_url = re.findall(r'"audio":\[{"id":\d+,"baseUrl":"(.*?)"', url_list_str)[0]

    headers_ = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'referer': playurl
    }

    # 获取纯视频的数据
    response_video = requests.get(video_url, headers=headers_)
    bytes_video = response_video.content
    # 获取纯音频的数据
    response_audio = requests.get(audio_url, headers=headers_)
    bytes_audio = response_audio.content

    # 保存
    with open('video\\' + title + '.mp4', 'wb') as f:
        f.write(bytes_video)
        print('纯视频文件下载完毕....')
    with open('video\\' + title + '.mp3', 'wb') as f:
        f.write(bytes_audio)
        print('纯音频文件下载完毕....')

    #相对目录下建立video和out文件夹
    ffmpeg_tools.ffmpeg_merge_video_audio('video\\' + title + '.mp4', 'video\\' + title + '.mp3', 'out\\' + title + '.mp4')
    os.remove(f"video\\{title}.mp4")
    os.remove(f"video\\{title}.mp3")
    print('-----------视频合成成功-----------')
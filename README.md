wechat2mp3
============

Why?
-----

Why not?

How
----

一、导出微信的音频消息：



1. 使用iTunes创建一个不加密备份
2. 导出备份中的微信应用文件夹
3. 找到音频文件

二、转换silk3编码音频为mp3:

如果你是mac机器，只需要安装ffmpeg（推荐使用homebrew）然后运行脚本：

    python wechat2mp3.py 待转换音频所在文件夹

如果你是其他系统，确认你装好了ffmpeg之后，需要自己编译SILK解码库。

Based on the great work done By Gabriel B. Nunes (gabriel@kronopath.net) and Nicodemo Gawronski (nico@deftlinux.net)

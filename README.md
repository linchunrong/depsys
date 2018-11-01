Depsys 发版系统
---
- 基于 Python flask web 框架，要求运行在 Linux 系统上
- 运行前请先编辑 setting.py 文件进行相关配置
- 初次运行，请执行命令对数据库进行初始化
```shell
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
```
- 初始化管理员账号/密码
```shell
$ python manage.py init
```
- 启动命令
 ```shell
 # 直接启动
$ python ./runserver.py
# 利用 gunicorn Web 服务器启动
$ gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 127.0.0.1:5000 runserver:app
 ```

`注意：报表中利用 pdfkit 生成带中文的 PDF 文件时，需要Linux系统安装中文字体`

---
#### Dependencies
- python==3.6.0  
- mysql==5.6  
- ansible==2.4.2  
- git==1.8.3.1  
- wkhtmltopdf==0.12.5

所引入的 python 类库见 requirements.txt, pip 安装：
```shell
pip install -r requirements.txt
```

`注：版本仅作参考用`
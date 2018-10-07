### Depsys 发版系统

- 基于 Python flask web 框架
- 运行前请先编辑 setting.py 文件进行相关配置
- 初次运行，请执行命令对数据库进行初始化
```shell
$ python migrate.py db init
$ python migrate.py db migrate
$ python migrate.py db upgrade
```
- 启动命令为 python ./runserver.py

`注意：报表中利用 pdfkit 生成带中文的 PDF 文件时，需要Linux系统安装中文字体`
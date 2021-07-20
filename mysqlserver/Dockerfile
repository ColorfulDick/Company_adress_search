FROM ubuntu:20.04

RUN sed -i s:/archive.ubuntu.com:/mirrors.tuna.tsinghua.edu.cn/ubuntu:g /etc/apt/sources.list
RUN cat /etc/apt/sources.list
RUN apt-get -y update --fix-missing

RUN apt-get install -y python3.7 
RUN apt-get install -y python3-pip
RUN apt-get install -y python-setuptools
#MySQL-Python必须得先安装这个库
RUN apt-get install -y libmysqlclient-dev   
RUN mkdir /mysqlserver
#设置工作目录
WORKDIR /mysqlserver
#将当前目录加入到工作目录中
ADD . /mysqlserver
#install any needed pacakges in requirements.txt，你要把所有需要安装的Python模块加到这文件中。
RUN pip install -r requirements.txt -i  https://pypi.doubanio.com/simple/  --trusted-host pypi.doubanio.com
#对外暴露端口
EXPOSE 5102
#设置环境变量
ENV SPIDER=/mysqlserver
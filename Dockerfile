FROM ubuntu

RUN apt-get update
RUN apt-get install sudo
RUN sudo apt-get update
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' >/etc/timezone
RUN apt-get install wget -y
RUN apt-get install git -y
RUN apt-get install curl -y
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN sudo apt-get install python3-distutils -y
RUN python3 get-pip.py

RUN apt install tzdata -y
RUN apt-get install aria2 -y

RUN mkdir /root/.aria2
COPY config /root/.aria2/

COPY root /

RUN pip3 install pyTelegramBotAPI
RUN pip3 install aria2p
RUN pip3 install requests
RUN pip3 install apscheduler
RUN pip3 install psutil
RUN pip3 install -U pytz
RUN pip3 install -U flask
#COPY bot /bot

RUN sudo chmod 777 /root/.aria2/
RUN sudo chmod 777 /rclone
RUN mv /rclone /usr/bin/

RUN sudo chmod 777 /start.sh
CMD bash start.sh
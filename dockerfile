FROM python:3.10

WORKDIR /usr/src/snake-bot

COPY requirements.txt ./

RUN apt-get -y update
RUN apt-get install -y ffmpeg
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "./main.py"]
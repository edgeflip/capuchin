FROM ubuntu:14.04
RUN apt-get update && apt-get install -y wget python-dev
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python ./get-pip.py
ADD . /app
WORKDIR /app
RUN pip install -r ./requirements.txt
